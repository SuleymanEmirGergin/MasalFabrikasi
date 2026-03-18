from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import uuid
from datetime import datetime
import os


class AIAssistantService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.conversations_file = os.path.join(settings.STORAGE_PATH, "ai_assistant_conversations.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.conversations_file):
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def get_realtime_suggestions(
        self,
        story_text: str,
        cursor_position: int,
        context: Optional[str] = None
    ) -> List[Dict]:
        """Gerçek zamanlı yazım önerileri getirir."""
        # Cursor pozisyonuna göre cümleyi al
        sentences = story_text.split('.')
        current_sentence = ""
        for sentence in sentences:
            if len(current_sentence) + len(sentence) < cursor_position:
                current_sentence += sentence + "."
            else:
                current_sentence = sentence
                break
        
        prompt = f"""
Aşağıdaki cümleyi tamamla veya iyileştir. 3 öneri sun.

Cümle: {current_sentence}
Bağlam: {context or 'Genel hikâye'}

JSON formatında döndür:
{{
  "suggestions": [
    {{
      "text": "Önerilen metin",
      "type": "completion/improvement/correction",
      "confidence": 0.9
    }}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir yazım asistanısın. Gerçek zamanlı öneriler sunuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result.get('suggestions', [])
        except:
            return []
    
    async def auto_complete(
        self,
        partial_text: str,
        context: Optional[str] = None
    ) -> str:
        """Otomatik tamamlama yapar."""
        prompt = f"""
Aşağıdaki metni tamamla. Sadece tamamlanmış metni döndür.

Kısmi Metin: {partial_text}
Bağlam: {context or 'Genel hikâye'}

Tamamlanmış Metin:
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir metin tamamlama uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
        except:
            return partial_text
    
    async def ask_question(
        self,
        question: str,
        story_context: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """Sorulara cevap verir."""
        system_prompt = "Sen bir hikâye yazma asistanısın. Kullanıcılara yardımcı oluyorsun."
        
        if story_context:
            system_prompt += f"\n\nHikâye Bağlamı: {story_context}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.5
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "question": question,
                "answer": answer,
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "question": question,
                "answer": "Üzgünüm, şu anda cevap veremiyorum.",
                "error": str(e)
            }
    
    async def get_writing_tips(self, story_type: str, language: str = "tr") -> List[str]:
        """Yazım ipuçları getirir."""
        prompt = f"""
{story_type} türünde hikâye yazmak için 5 ipucu ver.

JSON formatında döndür:
{{
  "tips": ["ipucu1", "ipucu2", "ipucu3", "ipucu4", "ipucu5"]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir yazım eğitmenisin."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result.get('tips', [])
        except:
            return []

    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Metin üretir (GPT-4)."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Generate text error: {e}")
            raise e

