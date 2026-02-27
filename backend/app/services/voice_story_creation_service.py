from typing import Dict, Optional
from openai import OpenAI
from app.core.config import settings
import json


class VoiceStoryCreationService:
    def __init__(self):
        # STT Client (Wiro - Whisper)
        self.stt_client = OpenAI(
            api_key=settings.STT_API_KEY,
            base_url=settings.STT_BASE_URL
        )
        # LLM Client (Wiro - GPT-OSS)
        self.llm_client = OpenAI(
            api_key=settings.GPT_API_KEY,
            base_url=settings.GPT_BASE_URL
        )
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        try:
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            try:
                # If using specialized Wiro model (whisper-large-v3-turbo-turkish)
                if "whisper" in settings.STT_MODEL.lower() and "wiro" in settings.STT_BASE_URL:
                    parts = settings.STT_MODEL.split("/")
                    provider = parts[0] if len(parts) > 1 else "openai"
                    model_slug = parts[1] if len(parts) > 1 else parts[0]
                    
                    inputs = {
                        "language": "auto",
                        "maxNewTokens": "256",
                        "chunkLength": "30",
                        "batchSize": "8"
                    }
                    
                    with open(tmp_path, 'rb') as audio_file:
                        files = {"inputAudio": (os.path.basename(tmp_path), audio_file, "audio/mpeg")}
                        result = await wiro_client.run_and_wait(provider, model_slug, inputs, files=files)
                    
                    detail = result.get("detail", {})
                    if detail and detail.get("tasklist"):
                        # Whisper output is usually in debugoutput as text
                        return detail["tasklist"][0].get("debugoutput", "").strip()
                
                # Standard OpenAI transcription
                with open(tmp_path, 'rb') as audio_file:
                    transcript = self.stt_client.audio.transcriptions.create(
                        model=settings.STT_MODEL,
                        file=audio_file
                    )
                return transcript.text
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
        except Exception as e:
            print(f"Transkript hatası: {e}")
            return ""
    
    async def create_story_from_voice(self, audio_transcript: str, language: str = "tr") -> Dict:
        prompt = f"""
Aşağıdaki ses kaydından çıkarılan metni bir hikâyeye dönüştür. Metni düzenle, geliştir ve tam bir hikâye haline getir.

Ses Metni:
{audio_transcript}

Hikâyeyi oluştur. Sadece hikâye metnini döndür.
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=settings.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Sen bir hikâye yazarısın. Ses kayıtlarından hikâyeler oluşturuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            story_text = response.choices[0].message.content.strip()
            
            return {
                "original_transcript": audio_transcript,
                "story_text": story_text,
                "language": language,
                "word_count": len(story_text.split())
            }
        except Exception as e:
            return {
                "original_transcript": audio_transcript,
                "story_text": audio_transcript,
                "error": str(e)
            }

