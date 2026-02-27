"""
Bedtime Mode Service - Uyku modu için özel servis
Ninni, beyaz gürültü ve arka plan sesleri yönetimi
"""
import os
from typing import List, Dict, Optional
from app.core.config import settings


class BedtimeService:
    """Bedtime mode için ses ve müzik yönetimi"""
    
    def __init__(self):
        # Önceden tanımlı arka plan sesleri
        self.background_sounds = {
            "lullaby": {
                "name": "Ninni",
                "name_en": "Lullaby",
                "description": "Yumuşak piyano ninnisi",
                "description_en": "Soft piano lullaby",
                "duration": 300,  # 5 dakika
                "url": "/static/sounds/lullaby.mp3",  # Statik dosya
                "volume_recommended": 0.3
            },
            "white_noise": {
                "name": "Beyaz Gürültü",
                "name_en": "White Noise",
                "description": "Rahatlatıcı beyaz gürültü",
                "description_en": "Soothing white noise",
                "duration": 600,  # 10 dakika
                "url": "/static/sounds/white_noise.mp3",
                "volume_recommended": 0.4
            },
            "rain": {
                "name": "Yağmur Sesi",
                "name_en": "Rain Sounds",
                "description": "Yavaş yağmur sesi",
                "description_en": "Gentle rain sounds",
                "duration": 600,
                "url": "/static/sounds/rain.mp3",
                "volume_recommended": 0.35
            },
            "ocean": {
                "name": "Okyanus Dalgaları",
                "name_en": "Ocean Waves",
                "description": "Sakin okyanus dalgaları",
                "description_en": "Calm ocean waves",
                "duration": 600,
                "url": "/static/sounds/ocean.mp3",
                "volume_recommended": 0.35
            },
            "forest": {
                "name": "Orman Sesleri",
                "name_en": "Forest Ambience",
                "description": "Yumuşak orman sesleri ve kuş cıvıltıları",
                "description_en": "Soft forest sounds and bird chirps",
                "duration": 600,
                "url": "/static/sounds/forest.mp3",
                "volume_recommended": 0.3
            }
        }
    
    def get_all_sounds(self, language: str = "tr") -> List[Dict]:
        """Tüm arka plan seslerini listeler"""
        result = []
        for sound_id, sound_data in self.background_sounds.items():
            result.append({
                "id": sound_id,
                "name": sound_data["name"] if language == "tr" else sound_data["name_en"],
                "description": sound_data["description"] if language == "tr" else sound_data["description_en"],
                "duration": sound_data["duration"],
                "url": sound_data["url"],
                "volume_recommended": sound_data["volume_recommended"]
            })
        return result
    
    def get_sound(self, sound_id: str, language: str = "tr") -> Optional[Dict]:
        """Belirli bir arka plan sesini getirir"""
        sound_data = self.background_sounds.get(sound_id)
        if not sound_data:
            return None
        
        return {
            "id": sound_id,
            "name": sound_data["name"] if language == "tr" else sound_data["name_en"],
            "description": sound_data["description"] if language == "tr" else sound_data["description_en"],
            "duration": sound_data["duration"],
            "url": sound_data["url"],
            "volume_recommended": sound_data["volume_recommended"]
        }
    
    def get_bedtime_recommendations(self, age_group: str = "3-6", language: str = "tr") -> Dict:
        """
        Yaş grubuna göre uyku öncesi öneriler
        
        Args:
            age_group: '3-6', '7-10', '11+'
            language: 'tr' veya 'en'
        
        Returns:
            Öneri sözlüğü
        """
        recommendations = {
            "3-6": {
                "recommended_sounds": ["lullaby", "white_noise", "rain"],
                "story_length": "short",  # 5-7 dakika
                "tts_speed": 0.85,  # Yavaş
                "tips_tr": [
                    "Işıkları azaltın",
                    "Hacmi düşük tutun (30-40%)",
                    "Aynı rutini her gece tekrarlayın"
                ],
                "tips_en": [
                    "Dim the lights",
                    "Keep volume low (30-40%)",
                    "Repeat the same routine every night"
                ]
            },
            "7-10": {
                "recommended_sounds": ["ocean", "rain", "forest"],
                "story_length": "medium",  # 8-12 dakika
                "tts_speed": 0.9,
                "tips_tr": [
                    "Rahat bir oturma pozisyonu",
                    "Ekran ışığını minimum seviyeye alın",
                    "Hikayeden sonra 10 dakika dinlenme"
                ],
                "tips_en": [
                    "Comfortable sitting position",
                    "Minimize screen brightness",
                    "10 minutes of rest after story"
                ]
            },
            "11+": {
                "recommended_sounds": ["forest", "ocean", "white_noise"],
                "story_length": "medium",  # 10-15 dakika
                "tts_speed": 0.95,
                "tips_tr": [
                    "Telefonları uzaklaştırın",
                    "Derin nefes egzersizleri yapın",
                    "Aynı saatte yatmaya çalışın"
                ],
                "tips_en": [
                    "Put phones away",
                    "Practice deep breathing",
                    "Try to sleep at the same time"
                ]
            }
        }
        
        rec = recommendations.get(age_group, recommendations["3-6"])
        
        return {
            "age_group": age_group,
            "recommended_sounds": [self.get_sound(sid, language) for sid in rec["recommended_sounds"]],
            "story_length": rec["story_length"],
            "tts_speed": rec["tts_speed"],
            "tips": rec["tips_tr"] if language == "tr" else rec["tips_en"]
        }
