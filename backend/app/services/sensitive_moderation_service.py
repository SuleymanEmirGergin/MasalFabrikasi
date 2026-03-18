from typing import Dict, List


class SensitiveModerationService:
    """
    Yaş uygunluk ve hassas konu kontrolü için basit etiketleyici.
    """

    SENSITIVE_TOPICS = ["şiddet", "korku", "uygunsuz", "hakaret"]

    async def check(self, text: str, region: str = "tr") -> Dict:
        findings: List[Dict] = []
        lowered = text.lower()
        for topic in self.SENSITIVE_TOPICS:
            if topic in lowered:
                findings.append({"topic": topic, "severity": "medium"})
        score = min(100, len(findings) * 20)
        return {
            "region": region,
            "risk_score": score,
            "findings": findings,
            "age_rating": "7+" if score < 40 else "13+",
        }


