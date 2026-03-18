from typing import Dict


class AdaptiveReadingService:
    """
    Okuma deneyimini kişiselleştirmek için basit ayar hesaplayıcı.
    """

    async def get_profile(self, speed_wpm: int, dislexia_friendly: bool = False) -> Dict:
        theme = "soft" if dislexia_friendly else "default"
        highlight = "line" if speed_wpm < 140 else "phrase"
        return {
            "recommended_speed_wpm": max(80, min(speed_wpm, 240)),
            "highlight_mode": highlight,
            "theme": theme,
            "font": "OpenDyslexic" if dislexia_friendly else "Default",
        }


