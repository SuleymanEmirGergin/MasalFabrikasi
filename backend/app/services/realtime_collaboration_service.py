from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage
from app.services.collaboration_service import CollaborationService


class RealtimeCollaborationService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.collaboration_service = CollaborationService()
        self.active_sessions_file = os.path.join(settings.STORAGE_PATH, "realtime_sessions.json")
        self.change_history_file = os.path.join(settings.STORAGE_PATH, "change_history.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.active_sessions_file):
            with open(self.active_sessions_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.change_history_file):
            with open(self.change_history_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def create_collaboration_session(
        self,
        story_id: str,
        user_id: str
    ) -> Dict:
        """
        Gerçek zamanlı işbirliği oturumu oluşturur.
        
        Args:
            story_id: Hikâye ID'si
            user_id: Oturum oluşturan kullanıcı ID'si
        
        Returns:
            Oturum bilgisi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        session_id = str(uuid.uuid4())
        
        session = {
            "session_id": session_id,
            "story_id": story_id,
            "owner_id": user_id,
            "participants": [user_id],
            "active_users": [user_id],
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "is_active": True
        }
        
        self._save_session(session)
        
        return session
    
    def _save_session(self, session: Dict):
        """Oturumu kaydeder."""
        try:
            with open(self.active_sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
        except:
            sessions = {}
        
        sessions[session['session_id']] = session
        
        with open(self.active_sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    def join_session(
        self,
        session_id: str,
        user_id: str
    ) -> Dict:
        """
        Oturuma katılır.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        if user_id not in session.get('participants', []):
            session['participants'].append(user_id)
        
        if user_id not in session.get('active_users', []):
            session['active_users'].append(user_id)
        
        session['last_activity'] = datetime.now().isoformat()
        self._save_session(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Oturumu getirir."""
        try:
            with open(self.active_sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
            return sessions.get(session_id)
        except:
            return None
    
    def apply_change(
        self,
        session_id: str,
        user_id: str,
        change_type: str,
        change_data: Dict
    ) -> Dict:
        """
        Değişikliği uygular.
        
        Args:
            session_id: Oturum ID'si
            user_id: Değişiklik yapan kullanıcı
            change_type: Değişiklik tipi (insert, delete, update, format)
            change_data: Değişiklik verisi
        
        Returns:
            Uygulanan değişiklik bilgisi
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        if user_id not in session.get('active_users', []):
            raise ValueError("Kullanıcı oturumda aktif değil")
        
        change = {
            "change_id": str(uuid.uuid4()),
            "session_id": session_id,
            "story_id": session.get('story_id'),
            "user_id": user_id,
            "change_type": change_type,
            "change_data": change_data,
            "timestamp": datetime.now().isoformat(),
            "applied": True
        }
        
        # Değişiklik geçmişine ekle
        self._save_change(change)
        
        # Oturum aktivitesini güncelle
        session['last_activity'] = datetime.now().isoformat()
        self._save_session(session)
        
        return change
    
    def _save_change(self, change: Dict):
        """Değişikliği kaydeder."""
        try:
            with open(self.change_history_file, 'r', encoding='utf-8') as f:
                changes = json.load(f)
        except:
            changes = {}
        
        story_id = change.get('story_id')
        if story_id not in changes:
            changes[story_id] = []
        
        changes[story_id].append(change)
        
        with open(self.change_history_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, ensure_ascii=False, indent=2)
    
    def get_change_history(
        self,
        story_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Değişiklik geçmişini getirir.
        """
        try:
            with open(self.change_history_file, 'r', encoding='utf-8') as f:
                changes = json.load(f)
            return changes.get(story_id, [])[-limit:]
        except:
            return []
    
    def add_suggestion(
        self,
        session_id: str,
        user_id: str,
        suggestion_text: str,
        position: Optional[Dict] = None
    ) -> Dict:
        """
        Öneri ekler.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        suggestion = {
            "suggestion_id": str(uuid.uuid4()),
            "session_id": session_id,
            "story_id": session.get('story_id'),
            "user_id": user_id,
            "suggestion_text": suggestion_text,
            "position": position,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Önerileri oturuma ekle
        if 'suggestions' not in session:
            session['suggestions'] = []
        
        session['suggestions'].append(suggestion)
        session['last_activity'] = datetime.now().isoformat()
        self._save_session(session)
        
        return suggestion
    
    def accept_suggestion(
        self,
        session_id: str,
        suggestion_id: str,
        user_id: str
    ) -> Dict:
        """
        Öneriyi kabul eder.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Oturum bulunamadı")
        
        suggestions = session.get('suggestions', [])
        suggestion = next((s for s in suggestions if s.get('suggestion_id') == suggestion_id), None)
        
        if not suggestion:
            raise ValueError("Öneri bulunamadı")
        
        suggestion['status'] = 'accepted'
        suggestion['accepted_by'] = user_id
        suggestion['accepted_at'] = datetime.now().isoformat()
        
        session['last_activity'] = datetime.now().isoformat()
        self._save_session(session)
        
        return suggestion
    
    def leave_session(self, session_id: str, user_id: str):
        """Oturumdan ayrılır."""
        session = self.get_session(session_id)
        if not session:
            return
        
        if user_id in session.get('active_users', []):
            session['active_users'].remove(user_id)
        
        session['last_activity'] = datetime.now().isoformat()
        self._save_session(session)
    
    def get_active_sessions(self, story_id: Optional[str] = None) -> List[Dict]:
        """Aktif oturumları getirir."""
        try:
            with open(self.active_sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
            
            active = [s for s in sessions.values() if s.get('is_active', False)]
            
            if story_id:
                active = [s for s in active if s.get('story_id') == story_id]
            
            return active
        except:
            return []

