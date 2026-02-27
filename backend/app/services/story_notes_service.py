from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class StoryNotesService:
    def __init__(self):
        self.notes_file = os.path.join(settings.STORAGE_PATH, "story_notes.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.notes_file):
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def add_note(
        self,
        story_id: str,
        user_id: str,
        note_text: str,
        position: Optional[int] = None
    ) -> Dict:
        """Not ekler."""
        note = {
            "note_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "note_text": note_text,
            "position": position,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(self.notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        if user_id not in notes:
            notes[user_id] = {}
        
        if story_id not in notes[user_id]:
            notes[user_id][story_id] = []
        
        notes[user_id][story_id].append(note)
        
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        
        return note
    
    def update_note(
        self,
        note_id: str,
        user_id: str,
        story_id: str,
        new_text: str
    ) -> Dict:
        """Notu günceller."""
        with open(self.notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        if user_id in notes and story_id in notes[user_id]:
            note = next(
                (n for n in notes[user_id][story_id] if n.get('note_id') == note_id),
                None
            )
            
            if note:
                note['note_text'] = new_text
                note['updated_at'] = datetime.now().isoformat()
                
                with open(self.notes_file, 'w', encoding='utf-8') as f:
                    json.dump(notes, f, ensure_ascii=False, indent=2)
                
                return note
        
        raise ValueError("Not bulunamadı")
    
    def delete_note(
        self,
        note_id: str,
        user_id: str,
        story_id: str
    ) -> bool:
        """Notu siler."""
        with open(self.notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        if user_id in notes and story_id in notes[user_id]:
            initial_count = len(notes[user_id][story_id])
            notes[user_id][story_id] = [
                n for n in notes[user_id][story_id]
                if n.get('note_id') != note_id
            ]
            
            if len(notes[user_id][story_id]) < initial_count:
                with open(self.notes_file, 'w', encoding='utf-8') as f:
                    json.dump(notes, f, ensure_ascii=False, indent=2)
                return True
        
        return False
    
    def get_story_notes(
        self,
        story_id: str,
        user_id: str
    ) -> List[Dict]:
        """Hikâye notlarını getirir."""
        with open(self.notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        if user_id in notes and story_id in notes[user_id]:
            return notes[user_id][story_id]
        
        return []

