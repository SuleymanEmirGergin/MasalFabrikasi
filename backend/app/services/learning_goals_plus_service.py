from typing import Dict, List


class LearningGoalsPlusService:
    """
    Okuma hedefleri ve kelime haznesi takibi için basit sayaç.
    """

    async def summarize_progress(self, user_id: str, words_read: int, minutes: int) -> Dict:
        streak = 3 if minutes > 10 else 0
        achievements: List[str] = []
        if words_read > 300:
            achievements.append("300+ kelime")
        if minutes > 15:
            achievements.append("15+ dakika")
        return {
            "user_id": user_id,
            "words_read": words_read,
            "minutes": minutes,
            "streak_days": streak,
            "achievements": achievements,
        }


