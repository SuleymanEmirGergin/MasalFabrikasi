from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class SyncEnhancedService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.sync_file = os.path.join(settings.STORAGE_PATH, "sync_enhanced.json")
        self.conflicts_file = os.path.join(settings.STORAGE_PATH, "sync_conflicts.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.sync_file, self.conflicts_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def sync_stories(
        self,
        user_id: str,
        device_id: str,
        device_stories: List[Dict]
    ) -> Dict:
        """Gelişmiş senkronizasyon."""
        server_stories = self.story_storage.get_all_stories()
        user_server_stories = [s for s in server_stories if s.get('user_id') == user_id]
        
        server_story_ids = {s.get('story_id') for s in user_server_stories}
        device_story_ids = {s.get('story_id') for s in device_stories}
        
        # Senkronizasyon planı
        to_download = [s for s in user_server_stories if s.get('story_id') not in device_story_ids]
        to_upload = [s for s in device_stories if s.get('story_id') not in server_story_ids]
        
        # Çakışmaları kontrol et
        conflicts = []
        for device_story in device_stories:
            story_id = device_story.get('story_id')
            if story_id in server_story_ids:
                server_story = next((s for s in user_server_stories if s.get('story_id') == story_id), None)
                if server_story:
                    device_updated = device_story.get('updated_at', '')
                    server_updated = server_story.get('updated_at', '')
                    
                    if device_updated != server_updated:
                        conflicts.append({
                            "story_id": story_id,
                            "device_version": device_story,
                            "server_version": server_story
                        })
        
        # Senkronizasyon durumunu kaydet
        sync_status = {
            "user_id": user_id,
            "device_id": device_id,
            "sync_time": datetime.now().isoformat(),
            "to_download": len(to_download),
            "to_upload": len(to_upload),
            "conflicts": len(conflicts)
        }
        
        with open(self.sync_file, 'r', encoding='utf-8') as f:
            syncs = json.load(f)
        if user_id not in syncs:
            syncs[user_id] = []
        syncs[user_id].append(sync_status)
        with open(self.sync_file, 'w', encoding='utf-8') as f:
            json.dump(syncs, f, ensure_ascii=False, indent=2)
        
        # Çakışmaları kaydet
        if conflicts:
            with open(self.conflicts_file, 'r', encoding='utf-8') as f:
                all_conflicts = json.load(f)
            if user_id not in all_conflicts:
                all_conflicts[user_id] = []
            all_conflicts[user_id].extend(conflicts)
            with open(self.conflicts_file, 'w', encoding='utf-8') as f:
                json.dump(all_conflicts, f, ensure_ascii=False, indent=2)
        
        return {
            "sync_status": sync_status,
            "stories_to_download": to_download,
            "stories_to_upload": to_upload,
            "conflicts": conflicts
        }
    
    def resolve_conflict(
        self,
        user_id: str,
        story_id: str,
        resolution: str,
        chosen_version: Optional[Dict] = None
    ) -> Dict:
        """Çakışmayı çözer."""
        with open(self.conflicts_file, 'r', encoding='utf-8') as f:
            all_conflicts = json.load(f)
        
        user_conflicts = all_conflicts.get(user_id, [])
        conflict = next((c for c in user_conflicts if c.get('story_id') == story_id), None)
        
        if not conflict:
            raise ValueError("Çakışma bulunamadı")
        
        if resolution == "use_device":
            chosen = conflict.get('device_version')
        elif resolution == "use_server":
            chosen = conflict.get('server_version')
        elif resolution == "merge" and chosen_version:
            chosen = chosen_version
        else:
            raise ValueError("Geçersiz çözüm")
        
        # Hikâyeyi güncelle
        self.story_storage.save_story(chosen)
        
        # Çakışmayı kaldır
        all_conflicts[user_id] = [c for c in user_conflicts if c.get('story_id') != story_id]
        with open(self.conflicts_file, 'w', encoding='utf-8') as f:
            json.dump(all_conflicts, f, ensure_ascii=False, indent=2)
        
        return {
            "story_id": story_id,
            "resolved": True,
            "resolution": resolution,
            "resolved_at": datetime.now().isoformat()
        }
    
    def get_sync_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Senkronizasyon geçmişini getirir."""
        with open(self.sync_file, 'r', encoding='utf-8') as f:
            syncs = json.load(f)
        
        user_syncs = syncs.get(user_id, [])
        return user_syncs[-limit:]

