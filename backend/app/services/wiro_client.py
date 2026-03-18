import os
import time
import hmac
import hashlib
import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
from app.core.config import settings
from app.core.resilience import retry_on_failure, wiro_circuit_breaker

logger = logging.getLogger(__name__)

class WiroClient:
    def __init__(self, base_url: str = "https://api.wiro.ai/v1"):
        self.base_url = base_url.rstrip("/")
        # Use settings for consistency, fallback to env if not in settings yet
        self.api_key = getattr(settings, "WIRO_API_KEY", os.environ.get("WIRO_API_KEY", ""))
        self.api_secret = getattr(settings, "WIRO_API_SECRET", os.environ.get("WIRO_API_SECRET", ""))

    def _signed_headers(self) -> Dict[str, str]:
        if not self.api_secret:
            return {"x-api-key": self.api_key}
            
        nonce = str(int(time.time()))
        msg = f"{self.api_secret}{nonce}".encode("utf-8")
        key = self.api_key.encode("utf-8")

        # HMAC-SHA256(key=API_KEY, message=API_SECRET+NONCE)
        signature = hmac.new(key, msg, hashlib.sha256).hexdigest()

        return {
            "x-api-key": self.api_key,
            "x-nonce": nonce,
            "x-signature": signature,
        }

    @wiro_circuit_breaker.call
    @retry_on_failure(max_retries=3, delay=2.0)
    async def run(self, provider: str, model_slug: str, inputs: Dict[str, Any], files: Optional[Dict[str, Any]] = None, is_json: bool = False) -> Dict[str, Any]:
        """
        Wiro Run Task Endpoint:
        POST /v1/Run/<provider>/<model_slug>
        """
        url = f"{self.base_url}/Run/{provider}/{model_slug}"
        headers = self._signed_headers()
        logger.info("Wiro run request: provider=%s model_slug=%s", provider, model_slug)

        async with httpx.AsyncClient(timeout=120) as client:
            if files:
                # Use multipart/form-data when files are present
                r = await client.post(url, headers=headers, data=inputs, files=files)
            elif is_json:
                # Explicit JSON request (e.g. gpt-oss-20b)
                r = await client.post(url, headers=headers, json=inputs)
            else:
                # Form data (e.g. gpt-5-nano: prompt, reasoning, verbosity, webSearch)
                r = await client.post(url, headers=headers, data=inputs)
            
            r.raise_for_status()
            out = r.json()
            taskid = out.get("taskid") or out.get("taskId")
            if taskid:
                logger.info("Wiro run completed: provider=%s model_slug=%s taskid=%s", provider, model_slug, taskid)
            return out

    @wiro_circuit_breaker.call
    @retry_on_failure(max_retries=3, delay=1.0)
    async def task_detail(self, taskid: Optional[str] = None, tasktoken: Optional[str] = None) -> Dict[str, Any]:
        """
        POST /v1/Task/Detail
        """
        if not taskid and not tasktoken:
            raise ValueError("taskid veya tasktoken gerekli")

        url = f"{self.base_url}/Task/Detail"
        headers = self._signed_headers()
        payload = {"taskid": taskid} if taskid else {"tasktoken": tasktoken}

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()

    async def run_and_wait(
        self,
        provider: str,
        model_slug: str,
        inputs: Dict[str, Any],
        files: Optional[Dict[str, Any]] = None,
        is_json: bool = False,
        poll_interval_s: float = 1.0,
        timeout_s: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Runs a task and polls until completion or timeout.
        """
        if timeout_s is None:
            timeout_s = getattr(settings, "WIRO_TASK_TIMEOUT_SECONDS", 120)
        start = time.time()
        run_resp = await self.run(provider, model_slug, inputs, files=files, is_json=is_json)

        taskid = str(run_resp.get("taskid") or "")
        tasktoken = run_resp.get("socketaccesstoken")

        if not taskid and not tasktoken:
            return {"run_response": run_resp, "detail": None}

        while True:
            if time.time() - start > timeout_s:
                return {"run_response": run_resp, "detail": {"status": "timeout"}}

            detail = await self.task_detail(taskid=taskid) if taskid else await self.task_detail(tasktoken=tasktoken)

            try:
                status = detail["tasklist"][0]["status"]
                debugerror = detail["tasklist"][0].get("debugerror", "")
            except Exception:
                status = None
                debugerror = ""

            if status in ("task_postprocess_end", "task_cancel"):
                return {"run_response": run_resp, "detail": detail}
            if status == "task_error" or debugerror:
                return {
                    "run_response": run_resp,
                    "detail": detail,
                    "error_message": debugerror or "Wiro task error",
                }

            await asyncio.sleep(poll_interval_s)

    @wiro_circuit_breaker.call
    async def kill_task(self, taskid: str) -> Dict[str, Any]:
        """
        POST /v1/Task/Kill
        """
        url = f"{self.base_url}/Task/Kill"
        headers = self._signed_headers()
        payload = {"taskid": taskid}
        
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()

    @wiro_circuit_breaker.call
    async def cancel_task(self, taskid: str) -> Dict[str, Any]:
        """
        POST /v1/Task/Cancel (For tasks on queue)
        """
        url = f"{self.base_url}/Task/Cancel"
        headers = self._signed_headers()
        payload = {"taskid": taskid}
        
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()

# Create a global instance
wiro_client = WiroClient()
