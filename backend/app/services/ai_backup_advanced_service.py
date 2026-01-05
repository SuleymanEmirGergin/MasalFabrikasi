from typing import Dict, List, Optional
from app.services.backup_sync_service import BackupSyncService
from app.services.story_storage import StoryStorage
import json
import os
from datetime import datetime, timedelta
from app.core.config import settings


class AIBackupAdvancedService:
    def __init__(self):
        self.backup_service = BackupSyncService()
        self.story_storage = StoryStorage()
        self.backup_schedule_file = os.path.join(settings.STORAGE_PATH, "backup_schedule.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.backup_schedule_file):
            with open(self.backup_schedule_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def schedule_smart_backup(
        self,
        user_id: str,
        backup_frequency: str = "daily",
        backup_time: str = "02:00"
    ) -> Dict:
        """Akıllı yedekleme zamanlaması oluşturur."""
        schedule = {
            "user_id": user_id,
            "backup_frequency": backup_frequency,
            "backup_time": backup_time,
            "last_backup": None,
            "next_backup": self._calculate_next_backup(backup_frequency, backup_time),
            "is_active": True
        }
        
        with open(self.backup_schedule_file, 'r', encoding='utf-8') as f:
            schedules = json.load(f)
        schedules[user_id] = schedule
        with open(self.backup_schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)
        
        return schedule
    
    def _calculate_next_backup(self, frequency: str, backup_time: str) -> str:
        """Sonraki yedekleme zamanını hesaplar."""
        now = datetime.now()
        hour, minute = map(int, backup_time.split(':'))
        
        if frequency == "daily":
            next_backup = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_backup <= now:
                next_backup += timedelta(days=1)
        elif frequency == "weekly":
            next_backup = now + timedelta(days=7)
            next_backup = next_backup.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            next_backup = now + timedelta(days=1)
        
        return next_backup.isoformat()
    
    def optimize_backup_size(self, user_id: str) -> Dict:
        """Yedek boyutunu optimize eder."""
        # Backup servisinden yedekleri al
        backup_path = os.path.join(settings.STORAGE_PATH, "backups")
        if not os.path.exists(backup_path):
            return {"optimized": False, "message": "Yedek klasörü bulunamadı"}
        
        # Yedek dosyalarını listele
        backup_files = [f for f in os.listdir(backup_path) if f.startswith(user_id)]
        
        if len(backup_files) <= 5:
            return {"optimized": False, "message": "Optimizasyon gerekmiyor"}
        
        # En eski yedekleri sil
        backup_files_with_time = []
        for f in backup_files:
            file_path = os.path.join(backup_path, f)
            backup_files_with_time.append({
                "filename": f,
                "path": file_path,
                "created_at": os.path.getctime(file_path)
            })
        
        backup_files_with_time.sort(key=lambda x: x['created_at'], reverse=True)
        backups_to_keep = backup_files_with_time[:5]
        backups_to_delete = backup_files_with_time[5:]
        
        deleted_count = 0
        for backup in backups_to_delete:
            try:
                os.remove(backup['path'])
                deleted_count += 1
            except Exception as e:
                print(f"Yedek silme hatası: {e}")
        
        return {
            "optimized": True,
            "deleted_count": deleted_count,
            "remaining_count": len(backups_to_keep)
        }

