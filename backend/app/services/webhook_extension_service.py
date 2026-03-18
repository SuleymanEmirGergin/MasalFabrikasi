from typing import Dict, List


class WebhookExtensionService:
    """
    LMS/ebeveyn paneli gibi harici sistemler için webhook şablonları.
    """

    async def list_events(self) -> Dict:
        return {"events": ["story.created", "story.published", "reading.completed"]}

    async def register(self, target_url: str, events: List[str]) -> Dict:
        return {"target_url": target_url, "events": events, "status": "registered"}


