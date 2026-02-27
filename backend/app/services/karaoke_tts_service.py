from typing import Dict, List


class KaraokeTTSService:
    """
    Metni basit zaman damgalı segmentlere böler. Gerçek TTS entegrasyonu
    ileride zamanlama ile güncellenebilir.
    """

    async def align_text(self, text: str) -> Dict:
        words = text.split()
        segments: List[Dict] = []
        time = 0.0
        for word in words:
            duration = max(0.25, len(word) * 0.05)
            segments.append({"word": word, "start": round(time, 2), "end": round(time + duration, 2)})
            time += duration
        return {"total_duration": round(time, 2), "segments": segments}


