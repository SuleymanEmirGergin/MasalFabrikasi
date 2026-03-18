from typing import Dict, List


class RealtimeQualityService:
    """
    Basit metin kalite denetimi ve anlık uyarılar için sahte servis.
    Gerçek entegrasyon için dilbilgisi/toksisite modelleri eklenebilir.
    """

    async def analyze_snippet(self, text: str, cursor: int) -> Dict:
        issues: List[Dict] = []
        if len(text) < 5:
            issues.append({"type": "length", "message": "Metin çok kısa görünüyor"})
        if any(bad in text.lower() for bad in ["kötü kelime", "hakaret"]):
            issues.append({"type": "toxicity", "message": "Uygunsuz ifade tespit edildi"})
        return {
            "text_length": len(text),
            "cursor": cursor,
            "issues": issues,
            "suggestions": ["Daha fazla detay ekleyin", "Tonunu yumuşatın"] if issues else [],
        }


