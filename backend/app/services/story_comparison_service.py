from typing import Dict, List
from app.services.story_storage import StoryStorage
from app.services.story_analysis_service import StoryAnalysisService
import difflib


class StoryComparisonService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.analysis_service = StoryAnalysisService()
    
    async def compare_stories(
        self,
        story_id_1: str,
        story_id_2: str
    ) -> Dict:
        """
        İki hikâyeyi karşılaştırır.
        
        Args:
            story_id_1: İlk hikâye ID'si
            story_id_2: İkinci hikâye ID'si
        
        Returns:
            Karşılaştırma sonuçları
        """
        story1 = self.story_storage.get_story(story_id_1)
        story2 = self.story_storage.get_story(story_id_2)
        
        if not story1 or not story2:
            raise ValueError("Hikâye bulunamadı")
        
        text1 = story1.get('story_text', '')
        text2 = story2.get('story_text', '')
        
        # Metin karşılaştırması
        similarity = self._calculate_text_similarity(text1, text2)
        
        # Analiz karşılaştırması
        analysis1 = await self.analysis_service.analyze_story(text1, story1.get('language', 'tr'))
        analysis2 = await self.analysis_service.analyze_story(text2, story2.get('language', 'tr'))
        
        # İstatistik karşılaştırması
        stats1 = analysis1.get('statistics', {})
        stats2 = analysis2.get('statistics', {})
        
        # Tema karşılaştırması
        theme1 = story1.get('theme', '').lower()
        theme2 = story2.get('theme', '').lower()
        theme_similarity = self._calculate_text_similarity(theme1, theme2)
        
        # Duygu karşılaştırması
        emotions1 = analysis1.get('emotions', {})
        emotions2 = analysis2.get('emotions', {})
        emotion_scores1 = emotions1.get('emotion_score', {})
        emotion_scores2 = emotions2.get('emotion_score', {})
        
        return {
            "story1": {
                "story_id": story_id_1,
                "theme": story1.get('theme'),
                "word_count": stats1.get('word_count', 0),
                "reading_time": stats1.get('reading_time_minutes', 0),
                "primary_emotion": emotions1.get('primary', 'neutral')
            },
            "story2": {
                "story_id": story_id_2,
                "theme": story2.get('theme'),
                "word_count": stats2.get('word_count', 0),
                "reading_time": stats2.get('reading_time_minutes', 0),
                "primary_emotion": emotions2.get('primary', 'neutral')
            },
            "comparison": {
                "text_similarity": round(similarity * 100, 2),
                "theme_similarity": round(theme_similarity * 100, 2),
                "word_count_difference": abs(stats1.get('word_count', 0) - stats2.get('word_count', 0)),
                "reading_time_difference": abs(stats1.get('reading_time_minutes', 0) - stats2.get('reading_time_minutes', 0)),
                "emotion_comparison": {
                    "happy": {
                        "story1": emotion_scores1.get('happy', 0),
                        "story2": emotion_scores2.get('happy', 0),
                        "difference": abs(emotion_scores1.get('happy', 0) - emotion_scores2.get('happy', 0))
                    },
                    "sad": {
                        "story1": emotion_scores1.get('sad', 0),
                        "story2": emotion_scores2.get('sad', 0),
                        "difference": abs(emotion_scores1.get('sad', 0) - emotion_scores2.get('sad', 0))
                    },
                    "excited": {
                        "story1": emotion_scores1.get('excited', 0),
                        "story2": emotion_scores2.get('excited', 0),
                        "difference": abs(emotion_scores1.get('excited', 0) - emotion_scores2.get('excited', 0))
                    }
                },
                "reading_level_comparison": {
                    "story1": analysis1.get('reading_level', {}),
                    "story2": analysis2.get('reading_level', {})
                }
            }
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """İki metin arasındaki benzerliği hesaplar."""
        if not text1 or not text2:
            return 0.0
        
        # Basit benzerlik hesaplama
        similarity = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        return similarity
    
    async def find_similar_stories(
        self,
        story_id: str,
        threshold: float = 0.3,
        limit: int = 5
    ) -> List[Dict]:
        """
        Benzer hikâyeler bulur.
        
        Args:
            story_id: Referans hikâye ID'si
            threshold: Benzerlik eşiği (0.0 - 1.0)
            limit: Maksimum sonuç sayısı
        
        Returns:
            Benzer hikâyeler listesi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        story_theme = story.get('theme', '').lower()
        
        all_stories = self.story_storage.get_all_stories()
        similar_stories = []
        
        for s in all_stories:
            if s.get('story_id') == story_id:
                continue
            
            s_text = s.get('story_text', '')
            s_theme = s.get('theme', '').lower()
            
            # Metin benzerliği
            text_similarity = self._calculate_text_similarity(story_text, s_text)
            
            # Tema benzerliği
            theme_similarity = self._calculate_text_similarity(story_theme, s_theme)
            
            # Kombine benzerlik
            combined_similarity = (text_similarity * 0.7) + (theme_similarity * 0.3)
            
            if combined_similarity >= threshold:
                similar_stories.append({
                    "story": s,
                    "similarity": round(combined_similarity * 100, 2),
                    "text_similarity": round(text_similarity * 100, 2),
                    "theme_similarity": round(theme_similarity * 100, 2)
                })
        
        # Benzerliğe göre sırala
        similar_stories.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_stories[:limit]

