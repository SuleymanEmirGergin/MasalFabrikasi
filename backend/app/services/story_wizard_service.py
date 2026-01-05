from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_service import StoryService
import json
import os
import uuid
from datetime import datetime


class StoryWizardService:
    """Hikaye oluşturma sihirbazı servisi - adım adım hikaye oluşturma"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_service = StoryService()
        self.wizard_sessions_file = os.path.join(settings.STORAGE_PATH, "wizard_sessions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.wizard_sessions_file):
            with open(self.wizard_sessions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def start_wizard_session(
        self,
        user_id: str,
        initial_theme: Optional[str] = None
    ) -> Dict:
        """Yeni bir sihirbaz oturumu başlatır."""
        session_id = str(uuid.uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "step": 1,
            "theme": initial_theme,
            "characters": [],
            "setting": None,
            "plot_points": [],
            "style": None,
            "length": "medium",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        sessions = self._load_sessions()
        sessions.append(session)
        self._save_sessions(sessions)
        
        return {
            "session_id": session_id,
            "step": 1,
            "message": "Hikaye oluşturma sihirbazına hoş geldiniz!",
            "next_question": "Hikayenizin teması nedir?"
        }
    
    async def update_wizard_step(
        self,
        session_id: str,
        step: int,
        answer: str
    ) -> Dict:
        """Sihirbaz adımını günceller."""
        sessions = self._load_sessions()
        session = next((s for s in sessions if s["session_id"] == session_id), None)
        
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        if step == 1:
            session["theme"] = answer
            session["step"] = 2
            next_question = "Hikayenizde hangi karakterler olacak? (virgülle ayırın)"
        elif step == 2:
            characters = [c.strip() for c in answer.split(",")]
            session["characters"] = characters
            session["step"] = 3
            next_question = "Hikaye nerede geçiyor? (mekan/ortam)"
        elif step == 3:
            session["setting"] = answer
            session["step"] = 4
            next_question = "Hikayenin ana olay örgüsü nedir? (kısa özet)"
        elif step == 4:
            session["plot_points"] = [answer]
            session["step"] = 5
            next_question = "Hikaye stili nedir? (masal, macera, fantastik, vb.)"
        elif step == 5:
            session["style"] = answer
            session["step"] = 6
            next_question = "Hikaye uzunluğu? (kısa, orta, uzun)"
        elif step == 6:
            session["length"] = answer
            session["step"] = 7
            session["updated_at"] = datetime.now().isoformat()
            # Hikayeyi oluştur
            story_result = await self._generate_story_from_wizard(session)
            session["story_id"] = story_result.get("story_id")
            self._save_sessions(sessions)
            return {
                "session_id": session_id,
                "step": 7,
                "completed": True,
                "story_id": story_result.get("story_id"),
                "message": "Hikayeniz başarıyla oluşturuldu!"
            }
        else:
            next_question = "Tamamlandı"
        
        session["updated_at"] = datetime.now().isoformat()
        self._save_sessions(sessions)
        
        return {
            "session_id": session_id,
            "step": session["step"],
            "message": "Bilgi kaydedildi",
            "next_question": next_question
        }
    
    async def _generate_story_from_wizard(self, session: Dict) -> Dict:
        """Sihirbaz verilerinden hikaye oluşturur."""
        prompt = f"""Aşağıdaki bilgilere göre bir {session.get('style', 'masal')} hikayesi yaz:

Tema: {session.get('theme', '')}
Karakterler: {', '.join(session.get('characters', []))}
Mekan: {session.get('setting', '')}
Olay Örgüsü: {session.get('plot_points', [''])[0]}
Uzunluk: {session.get('length', 'orta')}

Hikayeyi Türkçe olarak yaz ve çocuklar için uygun bir dil kullan."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir çocuk hikayesi yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        story_text = response.choices[0].message.content
        
        # StoryService kullanarak hikayeyi kaydet
        result = await self.story_service.create_story(
            theme=session.get('theme', 'Sihirbaz Hikayesi'),
            language="tr",
            story_type=session.get('style', 'masal'),
            story_text=story_text
        )
        
        return result
    
    def _load_sessions(self) -> List[Dict]:
        """Oturumları yükler."""
        try:
            with open(self.wizard_sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_sessions(self, sessions: List[Dict]):
        """Oturumları kaydeder."""
        with open(self.wizard_sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    async def get_wizard_session(self, session_id: str) -> Optional[Dict]:
        """Sihirbaz oturumunu getirir."""
        sessions = self._load_sessions()
        return next((s for s in sessions if s["session_id"] == session_id), None)
    
    async def cancel_wizard_session(self, session_id: str) -> Dict:
        """Sihirbaz oturumunu iptal eder."""
        sessions = self._load_sessions()
        sessions = [s for s in sessions if s["session_id"] != session_id]
        self._save_sessions(sessions)
        return {"message": "Oturum iptal edildi"}

