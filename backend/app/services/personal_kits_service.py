from typing import Dict, List


class PersonalKitsService:
    """
    Kullanıcı profiline göre hazır şablon paketleri üretir.
    """

    async def generate_kit(self, age: int, interests: List[str], level: str = "orta") -> Dict:
        themes = interests[:3] or ["macera", "dostluk"]
        return {
            "age": age,
            "level": level,
            "themes": themes,
            "templates": [
                {"name": f"{theme.title()} Başlangıç", "length": "kısa", "reading_time_min": 5}
                for theme in themes
            ],
        }


