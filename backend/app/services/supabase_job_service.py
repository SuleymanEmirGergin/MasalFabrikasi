from typing import Dict, Any, Optional
import logging
from app.core.supabase import supabase
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseJobService:
    """
    Supabase DB'deki jobs tablosunu güncelleyen servis.
    Bu tablo Realtime (Postgres Changes) üzerinden frontend tarafından dinlenir.
    """
    
    def __init__(self):
        self.table_name = "jobs"

    def upsert_job(self, job_id: str, user_id: str, status: str, progress: int = 0, message: str = ""):
        """
        Job durumunu Supabase'de oluşturur veya günceller.
        """
        try:
            data = {
                "id": job_id,
                "user_id": user_id,
                "status": status,
                "progress": progress,
                "message": message,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Using service role (supabase client) to bypass RLS
            result = supabase.table(self.table_name).upsert(data).execute()
            return result
        except Exception as e:
            logger.error(f"Failed to upsert job to Supabase: {e}")
            return None

    def update_progress(self, job_id: str, progress: int, message: str = "", status: str = "processing"):
        """
        Sadece ilerleme durumunu günceller.
        """
        try:
            data = {
                "progress": progress,
                "message": message,
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            result = supabase.table(self.table_name).update(data).eq("id", job_id).execute()
            return result
        except Exception as e:
            logger.error(f"Failed to update job progress in Supabase: {e}")
            return None

supabase_job_service = SupabaseJobService()
