from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryAiCharacterChatAdvancedService:
    """Hikaye AI karakter sohbetleri geliştirmeleri servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.chat_sessions_file = os.path.join(settings.STORAGE_PATH, "character_chat_sessions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.chat_sessions_file):
            with open(self.chat_sessions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_character_chatbot(
        self,
        story_id: str,
        character_name: str,
        character_background: str,
        personality_traits: List[str]
    ) -> Dict:
        """Karakter chatbot'u oluşturur."""
        chatbot_id = str(uuid.uuid4())
        
        chatbot = {
            "chatbot_id": chatbot_id,
            "story_id": story_id,
            "character_name": character_name,
            "character_background": character_background,
            "personality_traits": personality_traits,
            "conversation_history": [],
            "created_at": datetime.now().isoformat()
        }
        
        chatbots = self._load_chatbots()
        chatbots.append(chatbot)
        self._save_chatbots(chatbots)
        
        return {
            "chatbot_id": chatbot_id,
            "character_name": character_name,
            "message": "Karakter chatbot'u oluşturuldu"
        }
    
    async def chat_with_character(
        self,
        chatbot_id: str,
        user_message: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """Karakterle sohbet eder."""
        chatbots = self._load_chatbots()
        chatbot = next((c for c in chatbots if c["chatbot_id"] == chatbot_id), None)
        
        if not chatbot:
            raise ValueError("Chatbot bulunamadı")
        
        # Karakter kişiliğini oluştur
        personality_prompt = f"""Sen {chatbot['character_name']} karakterisin.
Arka plan: {chatbot['character_background']}
Kişilik özellikleri: {', '.join(chatbot['personality_traits'])}

Bu karakter gibi konuş ve cevap ver."""

        # Konuşma geçmişini ekle
        context = ""
        if chatbot["conversation_history"]:
            recent_history = chatbot["conversation_history"][-5:]  # Son 5 mesaj
            context = "\n".join([
                f"Kullanıcı: {h['user_message']}\nKarakter: {h['character_response']}"
                for h in recent_history
            ])
        
        prompt = f"""{personality_prompt}

{context}

Kullanıcı: {user_message}
Karakter:"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": personality_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=300
        )
        
        character_response = response.choices[0].message.content
        
        # Konuşma geçmişine ekle
        conversation_entry = {
            "entry_id": str(uuid.uuid4()),
            "user_id": user_id,
            "user_message": user_message,
            "character_response": character_response,
            "timestamp": datetime.now().isoformat()
        }
        
        chatbot["conversation_history"].append(conversation_entry)
        chatbot["updated_at"] = datetime.now().isoformat()
        
        self._save_chatbots(chatbots)
        
        return {
            "character_response": character_response,
            "character_name": chatbot["character_name"],
            "conversation_id": conversation_entry["entry_id"]
        }
    
    async def create_group_chat(
        self,
        story_id: str,
        character_ids: List[str]
    ) -> Dict:
        """Grup sohbeti oluşturur."""
        group_chat_id = str(uuid.uuid4())
        
        chatbots = self._load_chatbots()
        characters = [
            c for c in chatbots
            if c["chatbot_id"] in character_ids
        ]
        
        if len(characters) != len(character_ids):
            raise ValueError("Bazı karakterler bulunamadı")
        
        group_chat = {
            "group_chat_id": group_chat_id,
            "story_id": story_id,
            "characters": [
                {
                    "chatbot_id": c["chatbot_id"],
                    "character_name": c["character_name"]
                }
                for c in characters
            ],
            "conversations": [],
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "group_chat_id": group_chat_id,
            "characters_count": len(characters),
            "message": "Grup sohbeti oluşturuldu"
        }
    
    def _load_chatbots(self) -> List[Dict]:
        """Chatbot'ları yükler."""
        try:
            with open(self.chat_sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_chatbots(self, chatbots: List[Dict]):
        """Chatbot'ları kaydeder."""
        with open(self.chat_sessions_file, 'w', encoding='utf-8') as f:
            json.dump(chatbots, f, ensure_ascii=False, indent=2)

