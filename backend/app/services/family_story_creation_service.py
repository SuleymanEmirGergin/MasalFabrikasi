from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class FamilyStoryCreationService:
    """Ebeveyn-çocuk birlikte hikaye oluşturma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.family_sessions_file = os.path.join(settings.STORAGE_PATH, "family_sessions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.family_sessions_file):
            with open(self.family_sessions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def start_family_session(
        self,
        parent_id: str,
        child_id: str,
        child_age: int,
        initial_idea: Optional[str] = None
    ) -> Dict:
        """Aile hikaye oturumu başlatır."""
        session_id = str(uuid.uuid4())
        
        session = {
            "session_id": session_id,
            "parent_id": parent_id,
            "child_id": child_id,
            "child_age": child_age,
            "initial_idea": initial_idea,
            "contributions": [],
            "story_text": "",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        sessions = self._load_sessions()
        sessions.append(session)
        self._save_sessions(sessions)
        
        # Çocuk için uygun başlangıç önerisi
        suggestion = await self._generate_age_appropriate_suggestion(child_age, initial_idea)
        
        return {
            "session_id": session_id,
            "suggestion": suggestion,
            "message": "Aile hikaye oturumu başlatıldı"
        }
    
    async def add_contribution(
        self,
        session_id: str,
        contributor_id: str,
        contribution_text: str,
        contributor_type: str  # "parent" or "child"
    ) -> Dict:
        """Katkı ekler."""
        sessions = self._load_sessions()
        session = next((s for s in sessions if s["session_id"] == session_id), None)
        
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        contribution = {
            "contribution_id": str(uuid.uuid4()),
            "contributor_id": contributor_id,
            "contributor_type": contributor_type,
            "text": contribution_text,
            "timestamp": datetime.now().isoformat()
        }
        
        session["contributions"].append(contribution)
        session["story_text"] += " " + contribution_text
        session["updated_at"] = datetime.now().isoformat()
        
        self._save_sessions(sessions)
        
        # AI ile öneri oluştur
        next_suggestion = await self._generate_next_suggestion(
            session["story_text"],
            session["child_age"],
            contributor_type
        )
        
        return {
            "contribution_id": contribution["contribution_id"],
            "next_suggestion": next_suggestion,
            "message": "Katkı eklendi"
        }
    
    async def finalize_story(
        self,
        session_id: str,
        parent_id: str
    ) -> Dict:
        """Hikayeyi tamamlar."""
        sessions = self._load_sessions()
        session = next((s for s in sessions if s["session_id"] == session_id), None)
        
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        if session["parent_id"] != parent_id:
            raise ValueError("Bu oturumu tamamlama yetkiniz yok")
        
        # Hikayeyi düzenle ve iyileştir
        improved_story = await self._improve_story(
            session["story_text"],
            session["child_age"]
        )
        
        session["final_story"] = improved_story
        session["status"] = "completed"
        session["completed_at"] = datetime.now().isoformat()
        
        self._save_sessions(sessions)
        
        return {
            "session_id": session_id,
            "final_story": improved_story,
            "contributions_count": len(session["contributions"]),
            "message": "Hikaye tamamlandı"
        }
    
    async def _generate_age_appropriate_suggestion(
        self,
        age: int,
        initial_idea: Optional[str]
    ) -> str:
        """Yaşa uygun öneri oluşturur."""
        if age < 5:
            age_group = "okul öncesi"
        elif age < 8:
            age_group = "ilkokul"
        else:
            age_group = "ortaokul"
        
        prompt = f"""Bir {age_group} çocuğu için hikaye başlangıcı öner:
{f"Fikir: {initial_idea}" if initial_idea else ""}

Kısa, yaratıcı ve çocuğun ilgisini çekecek bir başlangıç."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir çocuk hikayesi uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        
        return response.choices[0].message.content
    
    async def _generate_next_suggestion(
        self,
        current_story: str,
        child_age: int,
        last_contributor: str
    ) -> str:
        """Sonraki öneri oluşturur."""
        next_person = "ebeveyn" if last_contributor == "child" else "çocuk"
        
        prompt = f"""Hikaye şu ana kadar:
{current_story}

{next_person} için bir sonraki cümle önerisi yap. Kısa ve yaratıcı olsun."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=150
        )
        
        return response.choices[0].message.content
    
    async def _improve_story(
        self,
        story_text: str,
        child_age: int
    ) -> str:
        """Hikayeyi iyileştirir."""
        prompt = f"""Aşağıdaki hikayeyi {child_age} yaşındaki bir çocuk için düzenle ve iyileştir. 
Dil basit ve anlaşılır olsun, ama hikayenin özünü koru:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir çocuk hikayesi editörüsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _load_sessions(self) -> List[Dict]:
        """Oturumları yükler."""
        try:
            with open(self.family_sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_sessions(self, sessions: List[Dict]):
        """Oturumları kaydeder."""
        with open(self.family_sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)

