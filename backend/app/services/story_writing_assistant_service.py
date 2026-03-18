from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryWritingAssistantService:
    """Hikaye AI yazım asistanı servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.assistant_sessions_file = os.path.join(settings.STORAGE_PATH, "writing_assistant_sessions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.assistant_sessions_file):
            with open(self.assistant_sessions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def start_writing_session(
        self,
        user_id: str,
        story_idea: Optional[str] = None,
        writing_style: str = "children"
    ) -> Dict:
        """Yazım oturumu başlatır."""
        session_id = str(uuid.uuid4())
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "story_idea": story_idea,
            "writing_style": writing_style,
            "current_text": "",
            "suggestions": [],
            "created_at": datetime.now().isoformat()
        }
        
        sessions = self._load_sessions()
        sessions.append(session)
        self._save_sessions(sessions)
        
        # İlk öneri
        initial_suggestion = await self._generate_initial_suggestion(story_idea, writing_style)
        
        return {
            "session_id": session_id,
            "initial_suggestion": initial_suggestion,
            "message": "Yazım oturumu başlatıldı"
        }
    
    async def get_writing_suggestion(
        self,
        session_id: str,
        current_text: str,
        context: Optional[str] = None
    ) -> Dict:
        """Yazım önerisi alır."""
        sessions = self._load_sessions()
        session = next((s for s in sessions if s["session_id"] == session_id), None)
        
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        prompt = f"""Aşağıdaki hikayeye devam etmek için öneriler sun.
Mevcut metin:
{current_text}

{f"Bağlam: {context}" if context else ""}

{len(current_text.split())} kelimelik bir devam önerisi yap."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Sen bir {session['writing_style']} hikayesi yazım asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )
        
        suggestion = response.choices[0].message.content
        
        session["suggestions"].append({
            "suggestion_id": str(uuid.uuid4()),
            "text": suggestion,
            "timestamp": datetime.now().isoformat()
        })
        session["updated_at"] = datetime.now().isoformat()
        
        self._save_sessions(sessions)
        
        return {
            "suggestion": suggestion,
            "suggestions_count": len(session["suggestions"])
        }
    
    async def improve_text(
        self,
        session_id: str,
        text: str,
        improvement_type: str = "general"
    ) -> Dict:
        """Metni iyileştirir."""
        sessions = self._load_sessions()
        session = next((s for s in sessions if s["session_id"] == session_id), None)
        
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        improvement_prompts = {
            "general": "Metni genel olarak iyileştir",
            "grammar": "Dilbilgisi hatalarını düzelt",
            "style": "Yazım stilini iyileştir",
            "creativity": "Daha yaratıcı hale getir",
            "simplicity": "Daha basit ve anlaşılır yap"
        }
        
        prompt = f"""{improvement_prompts.get(improvement_type, "Metni iyileştir")}:

{text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir metin editörüsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        improved_text = response.choices[0].message.content
        
        return {
            "original_text": text,
            "improved_text": improved_text,
            "improvement_type": improvement_type
        }
    
    async def check_grammar(
        self,
        text: str
    ) -> Dict:
        """Dilbilgisi kontrolü yapar."""
        prompt = f"""Aşağıdaki metindeki dilbilgisi hatalarını bul ve düzelt:

{text}

Hataları liste halinde göster."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir dilbilgisi uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        corrections = response.choices[0].message.content
        
        return {
            "corrections": corrections,
            "errors_found": len(corrections.split('\n')) if corrections else 0
        }
    
    async def _generate_initial_suggestion(
        self,
        story_idea: Optional[str],
        writing_style: str
    ) -> str:
        """İlk öneri oluşturur."""
        prompt = f"""Bir {writing_style} hikayesi için başlangıç önerisi yap.
{f"Fikir: {story_idea}" if story_idea else ""}

Kısa ve ilgi çekici bir başlangıç."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye yazım asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        
        return response.choices[0].message.content
    
    def _load_sessions(self) -> List[Dict]:
        """Oturumları yükler."""
        try:
            with open(self.assistant_sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_sessions(self, sessions: List[Dict]):
        """Oturumları kaydeder."""
        with open(self.assistant_sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)

