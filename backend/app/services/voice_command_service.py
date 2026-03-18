from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.wiro_client import wiro_client
import json


class VoiceCommandService:
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

    async def transcribe_audio(self, audio_file) -> str:
        """
        Ses dosyasını metne dönüştürür (Wiro Whisper veya Standard).
        """
        try:
            if "whisper" in settings.STT_MODEL.lower() and "wiro" in settings.STT_BASE_URL:
                parts = settings.STT_MODEL.split("/")
                provider = parts[0] if len(parts) > 1 else "openai"
                model_slug = parts[1] if len(parts) > 1 else parts[0]
                
                inputs = {
                    "inputAudioUrl": "",
                    "language": "auto",
                    "maxNewTokens": "256",
                    "chunkLength": "30",
                    "batchSize": "8",
                    "numSpeakers": "1",
                    "diarization": "--diarization"
                }
                
                # audio_file is expected to be a binary file object
                files = {"inputAudio": ("command.mp3", audio_file, "audio/mpeg")}
                result = await wiro_client.run_and_wait(provider, model_slug, inputs, files=files)
                
                detail = result.get("detail", {})
                if detail and detail.get("tasklist"):
                    return detail["tasklist"][0].get("debugoutput", "").strip()

            # Standard path
            transcript = self.stt_client.audio.transcriptions.create(
                model=settings.STT_MODEL, 
                file=audio_file,
                response_format="text"
            )
            return transcript
        except Exception as e:
            print(f"Transkripsiyon hatası: {e}")
            raise e

    
    async def process_voice_command(
        self,
        audio_transcript: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Sesli komutu işler ve komutu çıkarır.
        """
        prompt = f"""
Aşağıdaki sesli komutu analiz et ve JSON formatında komut bilgilerini döndür.

Sesli Komut: "{audio_transcript}"

Olası komutlar:
- create_story: "Yeni hikâye oluştur", "Hikâye yaz"
- search_story: "Hikâye ara", "Masal bul"
- play_audio: "Sesi oynat", "Dinle"
- pause_audio: "Durdur", "Pause"
- next_story: "Sonraki hikâye", "İleri"
- previous_story: "Önceki hikâye", "Geri"
- share_story: "Paylaş", "Paylaşım yap"
- save_story: "Kaydet", "Favorilere ekle"

JSON formatında döndür:
{{
  "command": "komut_tipi",
  "action": "create_story",
  "parameters": {{
    "theme": "tema (varsa)",
    "language": "dil (varsa)",
    "story_type": "hikâye_türü (varsa)"
  }},
  "confidence": 0.9
}}
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=settings.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Sen bir sesli komut işleme uzmanısın. Kullanıcı komutlarını analiz ediyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            command_text = response.choices[0].message.content
            
            if "```json" in command_text:
                command_text = command_text.split("```json")[1].split("```")[0].strip()
            elif "```" in command_text:
                command_text = command_text.split("```")[1].split("```")[0].strip()
            
            command_data = json.loads(command_text)
            
            return {
                "original_transcript": audio_transcript,
                "command": command_data.get('command', 'unknown'),
                "action": command_data.get('action', 'unknown'),
                "parameters": command_data.get('parameters', {}),
                "confidence": command_data.get('confidence', 0.5),
                "user_id": user_id
            }
        
        except Exception as e:
            print(f"Sesli komut işleme hatası: {e}")
            return {
                "original_transcript": audio_transcript,
                "command": "unknown",
                "action": "unknown",
                "parameters": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def create_story_from_voice(
        self,
        audio_transcript: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Sesli komuttan hikâye oluşturur.
        
        Args:
            audio_transcript: Ses komutu transkripti
            user_id: Kullanıcı ID'si
        
        Returns:
            Hikâye oluşturma bilgileri
        """
        # Komutu analiz et
        command = await self.process_voice_command(audio_transcript, user_id)
        
        if command.get('action') != 'create_story':
            return {
                "success": False,
                "error": "Komut hikâye oluşturma komutu değil",
                "command": command
            }
        
        parameters = command.get('parameters', {})
        theme = parameters.get('theme', 'Genel bir hikâye')
        
        # Hikâye oluşturma için bilgileri döndür
        return {
            "success": True,
            "theme": theme,
            "language": parameters.get('language', 'tr'),
            "story_type": parameters.get('story_type', 'masal'),
            "command": command,
            "note": "Hikâye oluşturmak için story_service kullanılabilir"
        }
    
    def get_voice_command_examples(self) -> List[Dict]:
        """Sesli komut örneklerini getirir."""
        return [
            {
                "command": "create_story",
                "examples": [
                    "Yeni bir hikâye oluştur",
                    "Masal yaz",
                    "Hikâye yarat",
                    "Bir hikâye oluştur, konusu orman"
                ]
            },
            {
                "command": "search_story",
                "examples": [
                    "Hikâye ara",
                    "Masal bul",
                    "Ejderha hikâyesi ara"
                ]
            },
            {
                "command": "play_audio",
                "examples": [
                    "Sesi oynat",
                    "Dinle",
                    "Hikâyeyi dinle"
                ]
            },
            {
                "command": "share_story",
                "examples": [
                    "Paylaş",
                    "Hikâyeyi paylaş",
                    "Sosyal medyada paylaş"
                ]
            }
        ]

