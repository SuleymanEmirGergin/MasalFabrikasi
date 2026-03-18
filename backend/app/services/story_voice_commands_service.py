from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryVoiceCommandsService:
    """Hikaye sesli komutlar servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.commands_file = os.path.join(settings.STORAGE_PATH, "voice_commands.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.commands_file):
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def process_voice_command(
        self,
        user_id: str,
        audio_text: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Sesli komutu işler."""
        command_id = str(uuid.uuid4())
        
        # Komutu analiz et
        command_type = self._identify_command_type(audio_text)
        
        # Komutu çalıştır
        result = await self._execute_command(command_type, audio_text, context)
        
        command_record = {
            "command_id": command_id,
            "user_id": user_id,
            "audio_text": audio_text,
            "command_type": command_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        commands = self._load_commands()
        commands.append(command_record)
        self._save_commands(commands)
        
        return {
            "command_id": command_id,
            "command_type": command_type,
            "result": result
        }
    
    async def _execute_command(
        self,
        command_type: str,
        audio_text: str,
        context: Optional[Dict]
    ) -> Dict:
        """Komutu çalıştırır."""
        if command_type == "create_story":
            return await self._handle_create_story(audio_text)
        elif command_type == "search_story":
            return await self._handle_search_story(audio_text)
        elif command_type == "edit_story":
            return await self._handle_edit_story(audio_text, context)
        elif command_type == "delete_story":
            return await self._handle_delete_story(audio_text, context)
        elif command_type == "share_story":
            return await self._handle_share_story(audio_text, context)
        else:
            return {"message": "Komut anlaşılamadı", "action": "none"}
    
    def _identify_command_type(self, audio_text: str) -> str:
        """Komut tipini belirler."""
        text_lower = audio_text.lower()
        
        if any(word in text_lower for word in ["oluştur", "yaz", "yeni hikaye", "masal"]):
            return "create_story"
        elif any(word in text_lower for word in ["ara", "bul", "göster", "listele"]):
            return "search_story"
        elif any(word in text_lower for word in ["düzenle", "değiştir", "güncelle"]):
            return "edit_story"
        elif any(word in text_lower for word in ["sil", "kaldır", "çıkar"]):
            return "delete_story"
        elif any(word in text_lower for word in ["paylaş", "gönder", "göster"]):
            return "share_story"
        else:
            return "unknown"
    
    async def _handle_create_story(self, audio_text: str) -> Dict:
        """Hikaye oluşturma komutunu işler."""
        prompt = f"""Kullanıcı şunu söyledi: {audio_text}
Bu komuttan bir hikaye oluştur. Kısa ve çocuklar için uygun olsun."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        story_text = response.choices[0].message.content
        
        return {
            "action": "create_story",
            "story_text": story_text,
            "message": "Hikaye oluşturuldu"
        }
    
    async def _handle_search_story(self, audio_text: str) -> Dict:
        """Arama komutunu işler."""
        return {
            "action": "search_story",
            "search_query": audio_text,
            "message": "Arama yapılıyor"
        }
    
    async def _handle_edit_story(self, audio_text: str, context: Optional[Dict]) -> Dict:
        """Düzenleme komutunu işler."""
        return {
            "action": "edit_story",
            "edit_instruction": audio_text,
            "story_id": context.get("story_id") if context else None,
            "message": "Düzenleme yapılıyor"
        }
    
    async def _handle_delete_story(self, audio_text: str, context: Optional[Dict]) -> Dict:
        """Silme komutunu işler."""
        return {
            "action": "delete_story",
            "story_id": context.get("story_id") if context else None,
            "message": "Hikaye siliniyor"
        }
    
    async def _handle_share_story(self, audio_text: str, context: Optional[Dict]) -> Dict:
        """Paylaşım komutunu işler."""
        return {
            "action": "share_story",
            "story_id": context.get("story_id") if context else None,
            "message": "Hikaye paylaşılıyor"
        }
    
    def _load_commands(self) -> List[Dict]:
        """Komutları yükler."""
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_commands(self, commands: List[Dict]):
        """Komutları kaydeder."""
        with open(self.commands_file, 'w', encoding='utf-8') as f:
            json.dump(commands, f, ensure_ascii=False, indent=2)

