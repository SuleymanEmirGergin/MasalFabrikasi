from typing import List, Dict, Optional
from app.services.story_storage import StoryStorage
from app.services.user_profile_service import UserProfileService
import json
import os
from app.core.config import settings


class RecommendationService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.user_profile_service = UserProfileService()
        self.user_preferences_file = os.path.join(settings.STORAGE_PATH, "user_preferences.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Kullanıcı tercihleri dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.user_preferences_file):
            with open(self.user_preferences_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Kullanıcı için hikâye önerileri getirir.
        
        Args:
            user_id: Kullanıcı ID'si
            limit: Öneri sayısı
        
        Returns:
            Önerilen hikâyeler listesi
        """
        # Kullanıcı tercihlerini al
        preferences = self._get_user_preferences(user_id)
        
        # Kullanıcının okuduğu hikâyeleri al
        user_stories = self.story_storage.get_user_stories(user_id)
        read_story_ids = {s.get('story_id') for s in user_stories}
        
        # Tüm hikâyeleri al
        all_stories = self.story_storage.get_all_stories()
        
        # Okunmamış hikâyeleri filtrele
        unread_stories = [s for s in all_stories if s.get('story_id') not in read_story_ids]
        
        # Skorlama yap
        scored_stories = []
        for story in unread_stories:
            score = self._calculate_recommendation_score(story, preferences, user_stories)
            scored_stories.append({
                "story": story,
                "score": score,
                "reason": self._get_recommendation_reason(story, preferences)
            })
        
        # Skora göre sırala
        scored_stories.sort(key=lambda x: x['score'], reverse=True)
        
        # İlk N tanesini döndür
        recommendations = scored_stories[:limit]
        
        return [r['story'] for r in recommendations]
    
    def _get_user_preferences(self, user_id: str) -> Dict:
        """Kullanıcı tercihlerini getirir."""
        try:
            with open(self.user_preferences_file, 'r', encoding='utf-8') as f:
                preferences = json.load(f)
            return preferences.get(user_id, {})
        except:
            return {}
    
    def _calculate_recommendation_score(
        self,
        story: Dict,
        preferences: Dict,
        user_stories: List[Dict]
    ) -> float:
        """Hikâye için öneri skoru hesaplar."""
        score = 0.0
        
        # Tema tercihi
        preferred_themes = preferences.get('themes', [])
        story_theme = story.get('theme', '').lower()
        if any(theme.lower() in story_theme for theme in preferred_themes):
            score += 20
        
        # Hikâye türü tercihi
        preferred_types = preferences.get('story_types', [])
        story_type = story.get('story_type', '').lower()
        if story_type in [t.lower() for t in preferred_types]:
            score += 15
        
        # Popülerlik (beğeni sayısı)
        like_count = story.get('like_count', 0)
        score += min(like_count * 2, 30)  # Maksimum 30 puan
        
        # Yeni hikâyeler (son 7 gün)
        from datetime import datetime, timedelta
        created_at = story.get('created_at', '')
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if created_date > datetime.now() - timedelta(days=7):
                score += 10
        except:
            pass
        
        # Benzer hikâyeler (kullanıcının okuduğu hikâyelerle benzerlik)
        user_themes = {s.get('theme', '').lower() for s in user_stories}
        if story_theme in user_themes:
            score += 15
        
        # Trend hikâyeler
        if story.get('is_trending', False):
            score += 25
        
        return score
    
    def _get_recommendation_reason(self, story: Dict, preferences: Dict) -> str:
        """Öneri nedeni açıklaması."""
        reasons = []
        
        preferred_themes = preferences.get('themes', [])
        story_theme = story.get('theme', '').lower()
        if any(theme.lower() in story_theme for theme in preferred_themes):
            reasons.append("Sevdiğin temalara uygun")
        
        if story.get('is_trending', False):
            reasons.append("Şu anda popüler")
        
        like_count = story.get('like_count', 0)
        if like_count > 10:
            reasons.append("Çok beğenilmiş")
        
        if not reasons:
            reasons.append("Senin için önerilen")
        
        return ", ".join(reasons)
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict
    ):
        """Kullanıcı tercihlerini günceller."""
        try:
            with open(self.user_preferences_file, 'r', encoding='utf-8') as f:
                all_preferences = json.load(f)
        except:
            all_preferences = {}
        
        # Mevcut tercihleri güncelle
        if user_id not in all_preferences:
            all_preferences[user_id] = {}
        
        all_preferences[user_id].update(preferences)
        
        with open(self.user_preferences_file, 'w', encoding='utf-8') as f:
            json.dump(all_preferences, f, ensure_ascii=False, indent=2)
    
    async def get_similar_stories(
        self,
        story_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Benzer hikâyeler getirir.
        
        Args:
            story_id: Referans hikâye ID'si
            limit: Öneri sayısı
        
        Returns:
            Benzer hikâyeler listesi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            return []
        
        story_theme = story.get('theme', '').lower()
        story_type = story.get('story_type', '').lower()
        
        all_stories = self.story_storage.get_all_stories()
        similar_stories = []
        
        for s in all_stories:
            if s.get('story_id') == story_id:
                continue
            
            similarity_score = 0
            
            # Tema benzerliği
            if story_theme in s.get('theme', '').lower():
                similarity_score += 30
            
            # Tür benzerliği
            if story_type == s.get('story_type', '').lower():
                similarity_score += 20
            
            # Dil benzerliği
            if story.get('language') == s.get('language'):
                similarity_score += 10
            
            if similarity_score > 0:
                similar_stories.append({
                    "story": s,
                    "similarity": similarity_score
                })
        
        # Benzerliğe göre sırala
        similar_stories.sort(key=lambda x: x['similarity'], reverse=True)
        
        return [s['story'] for s in similar_stories[:limit]]

