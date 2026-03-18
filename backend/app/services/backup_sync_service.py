from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage
import shutil


class BackupSyncService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.backups_path = os.path.join(settings.STORAGE_PATH, "backups")
        self.sync_status_file = os.path.join(settings.STORAGE_PATH, "sync_status.json")
        self._ensure_directory()
        self._ensure_file()
    
    def _ensure_directory(self):
        """Yedekler dizinini oluşturur."""
        os.makedirs(self.backups_path, exist_ok=True)
    
    def _ensure_file(self):
        """Senkronizasyon durumu dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.sync_status_file):
            with open(self.sync_status_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def create_backup(
        self,
        user_id: str,
        backup_name: Optional[str] = None
    ) -> Dict:
        """
        Kullanıcının hikâyelerini yedekler.
        
        Args:
            user_id: Kullanıcı ID'si
            backup_name: Yedek adı (opsiyonel)
        
        Returns:
            Yedek objesi
        """
        user_stories = self.story_storage.get_user_stories(user_id)
        
        backup_id = str(uuid.uuid4())
        backup_name = backup_name or f"Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_data = {
            "backup_id": backup_id,
            "user_id": user_id,
            "backup_name": backup_name,
            "stories": user_stories,
            "created_at": datetime.now().isoformat(),
            "story_count": len(user_stories)
        }
        
        # Yedeği dosyaya kaydet
        backup_path = os.path.join(self.backups_path, f"{backup_id}.json")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return {
            "backup_id": backup_id,
            "backup_name": backup_name,
            "story_count": len(user_stories),
            "created_at": backup_data["created_at"],
            "file_path": backup_path
        }
    
    def restore_backup(
        self,
        backup_id: str,
        user_id: str
    ) -> Dict:
        """
        Yedeği geri yükler.
        
        Args:
            backup_id: Yedek ID'si
            user_id: Kullanıcı ID'si
        
        Returns:
            Geri yükleme sonucu
        """
        backup_path = os.path.join(self.backups_path, f"{backup_id}.json")
        
        if not os.path.exists(backup_path):
            raise ValueError("Yedek bulunamadı")
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        if backup_data.get('user_id') != user_id:
            raise ValueError("Bu yedek bu kullanıcıya ait değil")
        
        # Hikâyeleri geri yükle
        restored_count = 0
        for story in backup_data.get('stories', []):
            try:
                self.story_storage.save_story(story)
                restored_count += 1
            except:
                pass
        
        return {
            "backup_id": backup_id,
            "restored_count": restored_count,
            "total_stories": len(backup_data.get('stories', [])),
            "restored_at": datetime.now().isoformat()
        }
    
    def get_user_backups(self, user_id: str) -> List[Dict]:
        """Kullanıcının yedeklerini getirir."""
        backups = []
        
        for filename in os.listdir(self.backups_path):
            if filename.endswith('.json'):
                backup_path = os.path.join(self.backups_path, filename)
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    if backup_data.get('user_id') == user_id:
                        backups.append({
                            "backup_id": backup_data.get('backup_id'),
                            "backup_name": backup_data.get('backup_name'),
                            "story_count": backup_data.get('story_count', 0),
                            "created_at": backup_data.get('created_at')
                        })
                except:
                    pass
        
        # Tarihe göre sırala (yeni önce)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return backups
    
    def delete_backup(self, backup_id: str, user_id: str) -> bool:
        """Yedeği siler."""
        backup_path = os.path.join(self.backups_path, f"{backup_id}.json")
        
        if not os.path.exists(backup_path):
            return False
        
        # Kullanıcı kontrolü
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        if backup_data.get('user_id') != user_id:
            return False
        
        os.remove(backup_path)
        return True
    
    def set_sync_status(
        self,
        user_id: str,
        device_id: str,
        last_sync: str
    ):
        """
        Senkronizasyon durumunu kaydeder.
        
        Args:
            user_id: Kullanıcı ID'si
            device_id: Cihaz ID'si
            last_sync: Son senkronizasyon zamanı (ISO format)
        """
        try:
            with open(self.sync_status_file, 'r', encoding='utf-8') as f:
                sync_status = json.load(f)
        except:
            sync_status = {}
        
        if user_id not in sync_status:
            sync_status[user_id] = {}
        
        sync_status[user_id][device_id] = {
            "last_sync": last_sync,
            "device_id": device_id
        }
        
        with open(self.sync_status_file, 'w', encoding='utf-8') as f:
            json.dump(sync_status, f, ensure_ascii=False, indent=2)
    
    def get_sync_status(self, user_id: str) -> Dict:
        """Senkronizasyon durumunu getirir."""
        try:
            with open(self.sync_status_file, 'r', encoding='utf-8') as f:
                sync_status = json.load(f)
            return sync_status.get(user_id, {})
        except:
            return {}
    
    def sync_stories(
        self,
        user_id: str,
        device_stories: List[Dict]
    ) -> Dict:
        """
        Hikâyeleri senkronize eder.
        
        Args:
            user_id: Kullanıcı ID'si
            device_stories: Cihazdaki hikâyeler
        
        Returns:
            Senkronizasyon sonucu
        """
        server_stories = self.story_storage.get_user_stories(user_id)
        server_story_ids = {s.get('story_id') for s in server_stories}
        device_story_ids = {s.get('story_id') for s in device_stories}
        
        # Sunucuda olup cihazda olmayanlar
        to_download = [s for s in server_stories if s.get('story_id') not in device_story_ids]
        
        # Cihazda olup sunucuda olmayanlar
        to_upload = [s for s in device_stories if s.get('story_id') not in server_story_ids]
        
        # Her iki tarafta da olanlar (tarihe göre güncelle)
        to_update = []
        for device_story in device_stories:
            story_id = device_story.get('story_id')
            if story_id in server_story_ids:
                server_story = next(s for s in server_stories if s.get('story_id') == story_id)
                device_updated = device_story.get('updated_at', '')
                server_updated = server_story.get('updated_at', '')
                
                if device_updated > server_updated:
                    to_update.append(device_story)
        
        return {
            "to_download": len(to_download),
            "to_upload": len(to_upload),
            "to_update": len(to_update),
            "stories_to_download": to_download,
            "stories_to_upload": to_upload,
            "stories_to_update": to_update
        }

