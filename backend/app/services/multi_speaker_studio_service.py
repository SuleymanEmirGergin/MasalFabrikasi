from typing import Dict, List


class MultiSpeakerStudioService:
    """
    Çoklu konuşmacı için basit ses planı üretir.
    """

    async def plan_dialogue(self, dialogues: List[Dict]) -> Dict:
        tracks: List[Dict] = []
        for item in dialogues:
            speaker = item.get("speaker", "unknown")
            text = item.get("text", "")
            tracks.append(
                {
                    "speaker": speaker,
                    "voice": item.get("voice", "default"),
                    "emotion": item.get("emotion", "neutral"),
                    "text": text,
                    "estimated_duration": round(max(1.0, len(text) * 0.06), 2),
                }
            )
        return {"tracks": tracks, "total_tracks": len(tracks)}


