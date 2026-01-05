from typing import List, Dict, Optional
import uuid
from datetime import datetime

# In-memory storage for active sessions (Replace with Redis in production)
# Structure: { session_id: { ...data... } }
SESSIONS = {}

class CollaborationService:
    
    def create_session(self, host_user_id: str, theme: str) -> Dict:
        session_id = str(uuid.uuid4())[:8] # Short ID for easier sharing
        session = {
            "id": session_id,
            "host_id": host_user_id,
            "theme": theme,
            "participants": [host_user_id],
            "turn_index": 0, # Whose turn is it? (index in participants array)
            "segments": [], # List of text segments: { user_id, text, timestamp }
            "status": "waiting", # waiting, active, completed
            "created_at": datetime.now().isoformat()
        }
        SESSIONS[session_id] = session
        return session

    def join_session(self, session_id: str, user_id: str) -> Dict:
        if session_id not in SESSIONS:
            raise ValueError("Oturum bulunamadı.")
        
        session = SESSIONS[session_id]
        if session["status"] != "waiting":
            raise ValueError("Oturum zaten başladı veya bitti.")
        
        if user_id not in session["participants"]:
            session["participants"].append(user_id)
        
        return session

    def start_session(self, session_id: str, user_id: str) -> Dict:
        if session_id not in SESSIONS:
            raise ValueError("Oturum bulunamadı.")
        
        session = SESSIONS[session_id]
        if session["host_id"] != user_id:
            raise ValueError("Sadece oturum sahibi başlatabilir.")
            
        if len(session["participants"]) < 1: # Tek başına da yazabilsin test için
             raise ValueError("Yeterli katılımcı yok.")

        session["status"] = "active"
        session["turn_index"] = 0
        return session

    def submit_segment(self, session_id: str, user_id: str, text: str) -> Dict:
        if session_id not in SESSIONS:
            raise ValueError("Oturum bulunamadı.")
            
        session = SESSIONS[session_id]
        if session["status"] != "active":
             raise ValueError("Oturum aktif değil.")

        current_turn_user = session["participants"][session["turn_index"]]
        if current_turn_user != user_id:
             raise ValueError("Sıra sizde değil.")

        # Add segment
        session["segments"].append({
            "user_id": user_id,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Advance turn
        session["turn_index"] = (session["turn_index"] + 1) % len(session["participants"])
        
        return session

    def get_session(self, session_id: str) -> Dict:
        if session_id not in SESSIONS:
             raise ValueError("Oturum bulunamadı.")
        return SESSIONS[session_id]

    def get_active_sessions(self) -> List[Dict]:
        return [s for s in SESSIONS.values() if s["status"] == "waiting"]
