from typing import List, Dict, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.character_service import CharacterService
from app.services.story_storage import StoryStorage
import json
import uuid
from datetime import datetime
import os


class AIChatbotService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.character_service = CharacterService()
        self.story_storage = StoryStorage()
        self.conversations_file = os.path.join(settings.STORAGE_PATH, "chatbot_conversations.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Konuşmalar dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.conversations_file):
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def set_pending_state(self, conversation_id: str, state_type: str, data: Dict = None):
        """Konuşma için bekleme durumu ayarlar."""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
        except:
            conversations = []
        
        conversation = next((c for c in conversations if c.get('conversation_id') == conversation_id), None)
        if conversation:
            conversation['pending_state'] = {
                "type": state_type,
                "data": data or {},
                "timestamp": datetime.now().isoformat()
            }
            conversation['updated_at'] = datetime.now().isoformat()
            
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
            return True
        return False

    def get_pending_state(self, conversation_id: str) -> Optional[Dict]:
        """Konuşmanın bekleme durumunu getirir."""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            conversation = next((c for c in conversations if c.get('conversation_id') == conversation_id), None)
            return conversation.get('pending_state') if conversation else None
        except:
            return None

    def clear_pending_state(self, conversation_id: str):
        """Konuşmanın bekleme durumunu temizler."""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            conversation = next((c for c in conversations if c.get('conversation_id') == conversation_id), None)
            if conversation and 'pending_state' in conversation:
                del conversation['pending_state']
                conversation['updated_at'] = datetime.now().isoformat()
                
                with open(self.conversations_file, 'w', encoding='utf-8') as f:
                    json.dump(conversations, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    async def chat_with_character(
        self,
        character_id: str,
        user_message: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Karakterle sohbet eder.
        
        Args:
            character_id: Karakter ID'si
            user_message: Kullanıcı mesajı
            conversation_id: Konuşma ID'si (devam eden konuşma için)
            user_id: Kullanıcı ID'si
        
        Returns:
            Karakter yanıtı ve konuşma bilgisi
        """
        character = self.character_service.get_character(character_id)
        if not character:
            raise ValueError("Karakter bulunamadı")
        
        # Konuşma geçmişini al
        conversation_history = []
        pending_state = None
        
        if conversation_id:
            conversation_history = self._get_conversation_history(conversation_id)
            pending_state = self.get_pending_state(conversation_id)
        
        # Karakter kişiliğini hazırla
        character_personality = character.get('personality', '')
        character_description = character.get('description', '')
        character_name = character.get('name', 'Karakter')
        
        # Sistem prompt'u oluştur
        system_prompt = f"""
Sen {character_name} karakterisin. Aşağıdaki özelliklere sahipsin:

Kişilik: {character_personality}
Açıklama: {character_description}

Karakterin kişiliğine uygun, doğal ve samimi bir şekilde konuş. Çocuklarla konuşuyorsan basit ve anlaşılır bir dil kullan. Eğitici ve eğlenceli ol.
"""

        # Bekleme durumu varsa prompt'a ekle
        if pending_state:
            state_type = pending_state.get('type')
            state_data = pending_state.get('data', {})
            system_prompt += f"""
\nŞU ANDA ÖZEL BİR DURUMDASIN:
Durum: {state_type}
Bağlam: {json.dumps(state_data, ensure_ascii=False)}

Kullanıcının yazdığı mesajı bu bağlamda değerlendir. Eğer kullanıcı beklenen bilgiyi verirse, yanıtında bunu onayla.
"""
        
        # Konuşma geçmişini ekle
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in conversation_history[-10:]:  # Son 10 mesaj
            messages.append({"role": "user", "content": msg.get('user_message', '')})
            messages.append({"role": "assistant", "content": msg.get('character_response', '')})
        
        messages.append({"role": "user", "content": user_message})
        
        # AI'dan yanıt al
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            character_response = response.choices[0].message.content.strip()
            
            # Konuşmayı kaydet
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            self._save_message(
                conversation_id,
                character_id,
                user_id,
                user_message,
                character_response
            )
            
            return {
                "conversation_id": conversation_id,
                "character_id": character_id,
                "character_name": character_name,
                "user_message": user_message,
                "character_response": character_response,
                "timestamp": datetime.now().isoformat(),
                "pending_state": pending_state  # Frontend için durumu dön
            }
        
        except Exception as e:
            print(f"Chatbot hatası: {e}")
            return {
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "character_id": character_id,
                "character_name": character_name,
                "user_message": user_message,
                "character_response": "Üzgünüm, şu anda cevap veremiyorum. Lütfen daha sonra tekrar deneyin.",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Konuşma geçmişini getirir."""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            conversation = next(
                (c for c in conversations if c.get('conversation_id') == conversation_id),
                None
            )
            
            return conversation.get('messages', []) if conversation else []
        except:
            return []
    
    def _save_message(
        self,
        conversation_id: str,
        character_id: str,
        user_id: Optional[str],
        user_message: str,
        character_response: str
    ):
        """Mesajı kaydeder."""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
        except:
            conversations = []
        
        # Konuşmayı bul veya oluştur
        conversation = next(
            (c for c in conversations if c.get('conversation_id') == conversation_id),
            None
        )
        
        if not conversation:
            conversation = {
                "conversation_id": conversation_id,
                "character_id": character_id,
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            conversations.append(conversation)
        
        # Mesajı ekle
        conversation['messages'].append({
            "user_message": user_message,
            "character_response": character_response,
            "timestamp": datetime.now().isoformat()
        })
        
        conversation['updated_at'] = datetime.now().isoformat()
        
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Kullanıcının konuşmalarını getirir."""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            return [
                {
                    "conversation_id": c.get('conversation_id'),
                    "character_id": c.get('character_id'),
                    "message_count": len(c.get('messages', [])),
                    "last_message": c.get('messages', [])[-1] if c.get('messages') else None,
                    "updated_at": c.get('updated_at')
                }
                for c in conversations
                if c.get('user_id') == user_id
            ]
        except:
            return []
    
    async def chat_with_story_character(
        self,
        story_id: str,
        character_name: str,
        user_message: str,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Hikâyedeki bir karakterle sohbet eder.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        
        # Karakteri hikâyeden çıkar
        prompt = f"""
Aşağıdaki hikâyede {character_name} karakterini analiz et ve onun kişiliğini, özelliklerini belirle.

Hikâye:
{story_text}

Karakterin özelliklerini JSON formatında döndür:
{{
  "name": "{character_name}",
  "personality": "Kişilik özellikleri",
  "description": "Karakter açıklaması",
  "role": "Karakterin hikâyedeki rolü"
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir karakter analiz uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            character_data_text = response.choices[0].message.content
            
            if "```json" in character_data_text:
                character_data_text = character_data_text.split("```json")[1].split("```")[0].strip()
            elif "```" in character_data_text:
                character_data_text = character_data_text.split("```")[1].split("```")[0].strip()
            
            character_data = json.loads(character_data_text)
            
            # Geçici karakter oluştur ve sohbet et
            temp_character = {
                "character_id": f"story_{story_id}_{character_name}",
                "name": character_data.get('name', character_name),
                "personality": character_data.get('personality', ''),
                "description": character_data.get('description', '')
            }
            
            # Sohbet et
            return await self.chat_with_character(
                temp_character["character_id"],
                user_message,
                conversation_id,
                None
            )
        
        except Exception as e:
            print(f"Story character chat hatası: {e}")
            raise ValueError("Karakterle sohbet başlatılamadı")

