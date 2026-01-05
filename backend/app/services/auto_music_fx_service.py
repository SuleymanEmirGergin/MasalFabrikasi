from typing import Dict, List


class AutoMusicFXService:
    """
    Paragraflara göre basit müzik/efekt seçici.
    """

    async def suggest(self, paragraphs: List[str]) -> Dict:
        selections: List[Dict] = []
        for idx, para in enumerate(paragraphs):
            mood = "calm" if len(para) < 120 else "adventure"
            selections.append(
                {
                    "index": idx,
                    "mood": mood,
                    "music_track": f"{mood}_track.mp3",
                    "effects": ["wind"] if "orman" in para.lower() else [],
                }
            )
        return {"selections": selections}


