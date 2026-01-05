from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class StorySeriesService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.series_file = os.path.join(settings.STORAGE_PATH, "story_series.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Seri dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.series_file):
            with open(self.series_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_series(
        self,
        title: str,
        description: Optional[str] = None,
        created_by: str = None
    ) -> Dict:
        """
        Yeni bir hikâye serisi oluşturur.
        
        Args:
            title: Seri başlığı
            description: Seri açıklaması
            created_by: Oluşturan kullanıcı ID'si
        
        Returns:
            Seri objesi
        """
        series = {
            "series_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "created_by": created_by,
            "stories": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_public": False
        }
        
        self._save_series(series)
        return series
    
    def _save_series(self, series: Dict):
        """Seriyi kaydeder."""
        with open(self.series_file, 'r', encoding='utf-8') as f:
            all_series = json.load(f)
        
        # Mevcut seriyi güncelle veya yeni ekle
        all_series = [s for s in all_series if s.get('series_id') != series.get('series_id')]
        all_series.append(series)
        
        with open(self.series_file, 'w', encoding='utf-8') as f:
            json.dump(all_series, f, ensure_ascii=False, indent=2)
    
    def add_story_to_series(
        self,
        series_id: str,
        story_id: str,
        chapter_number: Optional[int] = None
    ) -> Dict:
        """
        Seriye hikâye ekler.
        
        Args:
            series_id: Seri ID'si
            story_id: Hikâye ID'si
            chapter_number: Bölüm numarası (opsiyonel)
        
        Returns:
            Güncellenmiş seri
        """
        series = self.get_series(series_id)
        if not series:
            raise ValueError("Seri bulunamadı")
        
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Bölüm numarasını belirle
        if chapter_number is None:
            existing_stories = series.get('stories', [])
            chapter_number = len(existing_stories) + 1
        
        # Hikâyeyi seriye ekle
        story_entry = {
            "story_id": story_id,
            "chapter_number": chapter_number,
            "title": story.get('theme', 'Bölüm ' + str(chapter_number)),
            "added_at": datetime.now().isoformat()
        }
        
        stories = series.get('stories', [])
        stories.append(story_entry)
        
        # Bölüm numaralarına göre sırala
        stories.sort(key=lambda x: x.get('chapter_number', 0))
        
        series['stories'] = stories
        series['updated_at'] = datetime.now().isoformat()
        
        self._save_series(series)
        return series
    
    def get_series(self, series_id: str) -> Optional[Dict]:
        """Seriyi getirir."""
        with open(self.series_file, 'r', encoding='utf-8') as f:
            all_series = json.load(f)
        
        return next((s for s in all_series if s.get('series_id') == series_id), None)
    
    def get_user_series(self, user_id: str) -> List[Dict]:
        """Kullanıcının serilerini getirir."""
        with open(self.series_file, 'r', encoding='utf-8') as f:
            all_series = json.load(f)
        
        return [s for s in all_series if s.get('created_by') == user_id]
    
    def get_public_series(self) -> List[Dict]:
        """Herkese açık serileri getirir."""
        with open(self.series_file, 'r', encoding='utf-8') as f:
            all_series = json.load(f)
        
        return [s for s in all_series if s.get('is_public', False)]
    
    def get_series_stories(self, series_id: str) -> List[Dict]:
        """Serideki hikâyeleri getirir."""
        series = self.get_series(series_id)
        if not series:
            return []
        
        story_ids = [s.get('story_id') for s in series.get('stories', [])]
        stories = []
        
        for story_id in story_ids:
            story = self.story_storage.get_story(story_id)
            if story:
                stories.append(story)
        
        return stories
    
    def remove_story_from_series(self, series_id: str, story_id: str) -> Dict:
        """Seriden hikâye çıkarır."""
        series = self.get_series(series_id)
        if not series:
            raise ValueError("Seri bulunamadı")
        
        stories = series.get('stories', [])
        stories = [s for s in stories if s.get('story_id') != story_id]
        
        series['stories'] = stories
        series['updated_at'] = datetime.now().isoformat()
        
        self._save_series(series)
        return series
    
    def update_series(
        self,
        series_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Dict:
        """Seriyi günceller."""
        series = self.get_series(series_id)
        if not series:
            raise ValueError("Seri bulunamadı")
        
        if title:
            series['title'] = title
        if description is not None:
            series['description'] = description
        if is_public is not None:
            series['is_public'] = is_public
        
        series['updated_at'] = datetime.now().isoformat()
        self._save_series(series)
        
        return series
    
    def delete_series(self, series_id: str) -> bool:
        """Seriyi siler."""
        with open(self.series_file, 'r', encoding='utf-8') as f:
            all_series = json.load(f)
        
        original_count = len(all_series)
        all_series = [s for s in all_series if s.get('series_id') != series_id]
        
        if len(all_series) < original_count:
            with open(self.series_file, 'w', encoding='utf-8') as f:
                json.dump(all_series, f, ensure_ascii=False, indent=2)
            return True
        
        return False

