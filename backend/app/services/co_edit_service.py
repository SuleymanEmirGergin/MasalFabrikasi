from typing import Dict, List


class CoEditService:
    """
    Basit eşzamanlı yazım oturumu takibi.
    """

    async def start_session(self, story_id: str, users: List[str]) -> Dict:
        return {"story_id": story_id, "session_id": f"ses-{story_id}", "participants": users}

    async def apply_suggestion(self, session_id: str, user_id: str, diff: str) -> Dict:
        return {"session_id": session_id, "applied_by": user_id, "diff_preview": diff[:120]}


