from typing import Dict, List
from datetime import datetime, timedelta


class PlannerAutomationService:
    """
    Yayın takvimi ve otomasyon görevleri için basit planlayıcı.
    """

    async def schedule_publish(self, story_id: str, when_minutes: int) -> Dict:
        eta = datetime.utcnow() + timedelta(minutes=when_minutes)
        return {"story_id": story_id, "scheduled_at": eta.isoformat() + "Z"}

    async def list_reminders(self, user_id: str) -> Dict:
        return {"user_id": user_id, "reminders": [{"title": "Okuma zamanı", "in_minutes": 60}]}


