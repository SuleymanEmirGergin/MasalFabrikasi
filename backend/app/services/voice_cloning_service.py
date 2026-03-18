import os
import httpx
from typing import List, Dict, Optional
from app.core.config import settings
from fastapi import UploadFile

class VoiceCloningService:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
        }

    async def get_cloned_voices(self) -> List[Dict]:
        """ElevenLabs hesabındaki tüm sesleri getirir."""
        if not self.api_key:
            return []

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Sadece klonlanmış sesleri filtreleyebiliriz veya hepsini dönebiliriz.
                # 'category': 'cloned' olanlar klonlanmış seslerdir.
                voices = []
                for voice in data.get("voices", []):
                     if voice.get("category") == "cloned":
                        voices.append({
                            "id": voice["voice_id"],
                            "name": voice["name"],
                            "preview_url": voice.get("preview_url")
                        })
                return voices
            except Exception as e:
                print(f"ElevenLabs get_voices error: {e}")
                return []

    async def clone_voice(self, name: str, files: List[str], description: str = "") -> Dict:
        """
        Ses dosyalarından yeni bir ses klonlar (Instant Voice Cloning).
        files: List of file paths to audio samples.
        """
        if not self.api_key:
            raise Exception("ElevenLabs API Key is missing.")

        url = f"{self.base_url}/voices/add"
        
        async with httpx.AsyncClient() as client:
            try:
                # Multipart form data hazırlığı
                files_data = []
                for file_path in files:
                    file_name = os.path.basename(file_path)
                    files_data.append(
                        ("files", (file_name, open(file_path, "rb"), "audio/mpeg")) # Mime type tahmin edilebilir
                    )
                
                data = {
                    "name": name,
                    "description": description
                }

                response = await client.post(
                    url,
                    headers=self.headers,
                    data=data,
                    files=files_data
                )
                
                # Dosyaları kapat
                for _, (fn, f, _) in files_data:
                    f.close()

                response.raise_for_status()
                return response.json() # Returns {"voice_id": "..."}
                
            except httpx.HTTPStatusError as e:
                print(f"ElevenLabs clone_voice error: {e.response.text}")
                raise Exception(f"Voice cloning failed: {e.response.text}")
            except Exception as e:
                print(f"ElevenLabs clone_voice error: {e}")
                raise

    async def delete_voice(self, voice_id: str) -> bool:
        """Klonlanmış sesi siler."""
        if not self.api_key:
            return False
            
        url = f"{self.base_url}/voices/{voice_id}"
        async with httpx.AsyncClient() as client:
             try:
                response = await client.delete(url, headers=self.headers)
                response.raise_for_status()
                return True
             except Exception as e:
                 print(f"ElevenLabs delete_voice error: {e}")
                 return False

    async def generate_speech(self, text: str, voice_id: str) -> bytes:
        """ElevenLabs ile metni sese çevirir (Wiro veya Direct)."""
        
        # Wiro Run/Poll Path
        if "elevenlabs" in settings.TTS_MODEL.lower() and "wiro" in settings.GPT_BASE_URL:
            from app.services.wiro_client import wiro_client
            try:
                inputs = {
                    "prompt": text,
                    "model": "eleven_flash_v2_5",
                    "voice": voice_id or settings.TTS_VOICE,
                    "outputFormat": settings.TTS_FORMAT
                }
                parts = settings.TTS_MODEL.split("/")
                provider = parts[0] if len(parts) > 1 else "elevenlabs"
                model_slug = parts[1] if len(parts) > 1 else parts[0]
                
                result = await wiro_client.run_and_wait(provider, model_slug, inputs)
                detail = result.get("detail", {})
                if detail and detail.get("tasklist"):
                    outputs = detail["tasklist"][0].get("outputs", [])
                    if outputs:
                        audio_url = outputs[0]["url"]
                        async with httpx.AsyncClient() as client:
                            audio_resp = await client.get(audio_url)
                            audio_resp.raise_for_status()
                            return audio_resp.content
            except Exception as e:
                print(f"Wiro ElevenLabs TTS error: {e}")

        # Direct ElevenLabs API Path
        if not self.api_key:
            raise Exception("ElevenLabs API Key missing")
            
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
                    json=payload,
                    timeout=60.0 # Uzun sürebilir
                )
                response.raise_for_status()
                return response.content
            except Exception as e:
                print(f"ElevenLabs generate_speech error: {e}")
                raise

voice_cloning_service = VoiceCloningService()
