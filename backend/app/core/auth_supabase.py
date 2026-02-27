import httpx
from fastapi import Header, HTTPException, Depends
from app.core.config import settings
from typing import Dict

async def get_current_user_supabase(authorization: str = Header(None)) -> Dict:
    """
    Verifies the JWT token by calling Supabase Auth API.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid Authorization header. Use 'Bearer <token>'"
        )

    token = authorization.split(" ", 1)[1]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
