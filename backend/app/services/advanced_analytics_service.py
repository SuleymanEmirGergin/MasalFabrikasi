from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.story_storage import StoryStorage
from app.services.performance_metrics_service import PerformanceMetricsService


class AdvancedAnalyticsService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.performance_metrics = PerformanceMetricsService()
        self.analytics_file = os.path.join(settings.STORAGE_PATH, "advanced_analytics.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Analitik dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def record_scroll_depth(
        self,
        story_id: str,
        user_id: str,
        scroll_percentage: float,
        time_spent: float
    ):
        """
        Scroll derinliğini kaydeder.
        
        Args:
            story_id: Hikâye ID'si
            user_id: Kullanıcı ID'si
            scroll_percentage: Scroll yüzdesi (0-100)
            time_spent: Geçirilen süre (saniye)
        """
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                analytics = json.load(f)
        except:
            analytics = {}
        
        if story_id not in analytics:
            analytics[story_id] = {
                "scroll_data": [],
                "heatmap_data": {},
                "engagement_points": []
            }
        
        scroll_entry = {
            "user_id": user_id,
            "scroll_percentage": scroll_percentage,
            "time_spent": time_spent,
            "timestamp": datetime.now().isoformat()
        }
        
        analytics[story_id]["scroll_data"].append(scroll_entry)
        
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, ensure_ascii=False, indent=2)
    
    def record_heatmap_data(
        self,
        story_id: str,
        section_index: int,
        interaction_type: str,
        user_id: Optional[str] = None
    ):
        """
        Heatmap verisi kaydeder.
        
        Args:
            story_id: Hikâye ID'si
            section_index: Bölüm indeksi
            interaction_type: Etkileşim tipi (click, hover, read)
            user_id: Kullanıcı ID'si
        """
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                analytics = json.load(f)
        except:
            analytics = {}
        
        if story_id not in analytics:
            analytics[story_id] = {
                "scroll_data": [],
                "heatmap_data": {},
                "engagement_points": []
            }
        
        section_key = f"section_{section_index}"
        if section_key not in analytics[story_id]["heatmap_data"]:
            analytics[story_id]["heatmap_data"][section_key] = {
                "clicks": 0,
                "hovers": 0,
                "reads": 0
            }
        
        analytics[story_id]["heatmap_data"][section_key][f"{interaction_type}s"] = \
            analytics[story_id]["heatmap_data"][section_key].get(f"{interaction_type}s", 0) + 1
        
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, ensure_ascii=False, indent=2)
    
    def get_scroll_analytics(self, story_id: str) -> Dict:
        """
        Scroll analitiklerini getirir.
        """
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                analytics = json.load(f)
        except:
            return {}
        
        story_analytics = analytics.get(story_id, {})
        scroll_data = story_analytics.get('scroll_data', [])
        
        if not scroll_data:
            return {
                "average_scroll_depth": 0,
                "completion_rate": 0,
                "drop_off_points": []
            }
        
        # Ortalama scroll derinliği
        avg_scroll = sum(s.get('scroll_percentage', 0) for s in scroll_data) / len(scroll_data)
        
        # Tamamlama oranı (100% scroll)
        completion_rate = sum(1 for s in scroll_data if s.get('scroll_percentage', 0) >= 95) / len(scroll_data) * 100
        
        # Drop-off noktaları
        drop_offs = {}
        for s in scroll_data:
            scroll_pct = s.get('scroll_percentage', 0)
            if scroll_pct < 100:
                # En yakın 10'luk dilime yuvarla
                bucket = (scroll_pct // 10) * 10
                drop_offs[bucket] = drop_offs.get(bucket, 0) + 1
        
        return {
            "average_scroll_depth": round(avg_scroll, 2),
            "completion_rate": round(completion_rate, 2),
            "total_reads": len(scroll_data),
            "drop_off_points": [
                {"scroll_percentage": k, "drop_off_count": v}
                for k, v in sorted(drop_offs.items())
            ]
        }
    
    def get_heatmap_data(self, story_id: str) -> Dict:
        """
        Heatmap verilerini getirir.
        """
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                analytics = json.load(f)
        except:
            return {}
        
        story_analytics = analytics.get(story_id, {})
        heatmap = story_analytics.get('heatmap_data', {})
        
        return {
            "heatmap": heatmap,
            "total_interactions": sum(
                sum(section.values()) for section in heatmap.values()
            )
        }
    
    def create_ab_test(
        self,
        story_id: str,
        variant_a: Dict,
        variant_b: Dict,
        test_name: str
    ) -> Dict:
        """
        A/B test oluşturur.
        
        Args:
            story_id: Hikâye ID'si
            variant_a: A varyantı (orijinal)
            variant_b: B varyantı (test)
            test_name: Test adı
        
        Returns:
            A/B test objesi
        """
        import uuid
        
        test = {
            "test_id": str(uuid.uuid4()),
            "story_id": story_id,
            "test_name": test_name,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "results": {
                "variant_a": {"views": 0, "conversions": 0},
                "variant_b": {"views": 0, "conversions": 0}
            }
        }
        
        # Testi kaydet
        tests_file = os.path.join(settings.STORAGE_PATH, "ab_tests.json")
        try:
            with open(tests_file, 'r', encoding='utf-8') as f:
                tests = json.load(f)
        except:
            tests = []
        
        tests.append(test)
        
        with open(tests_file, 'w', encoding='utf-8') as f:
            json.dump(tests, f, ensure_ascii=False, indent=2)
        
        return test
    
    def record_ab_test_view(
        self,
        test_id: str,
        variant: str,
        user_id: Optional[str] = None
    ):
        """
        A/B test görüntülemesini kaydeder.
        """
        tests_file = os.path.join(settings.STORAGE_PATH, "ab_tests.json")
        
        try:
            with open(tests_file, 'r', encoding='utf-8') as f:
                tests = json.load(f)
        except:
            return
        
        test = next((t for t in tests if t.get('test_id') == test_id), None)
        if not test:
            return
        
        if variant in ['A', 'B']:
            test['results'][f'variant_{variant.lower()}']['views'] += 1
        
        with open(tests_file, 'w', encoding='utf-8') as f:
            json.dump(tests, f, ensure_ascii=False, indent=2)
    
    def get_user_behavior_analysis(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Kullanıcı davranış analizi yapar.
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        all_stories = self.story_storage.get_all_stories()
        
        # Kullanıcının okuduğu hikâyeler (gerçek uygulamada metrics'ten alınabilir)
        user_metrics = self.performance_metrics.get_user_analytics(user_id)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_stories_read": user_metrics.get('total_stories', 0),
            "average_reading_time": user_metrics.get('average_story_length', 0),
            "preferred_themes": [],  # Gerçek uygulamada analiz edilebilir
            "reading_patterns": {
                "peak_hours": [],
                "preferred_days": []
            }
        }

    def query_analytics(
        self,
        metric_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Esnek analitik sorgulama metodu.
        
        Args:
            metric_type: Metrik tipi (scroll_depth, heatmap, reading_time)
            start_date: Başlangıç tarihi (ISO format)
            end_date: Bitiş tarihi (ISO format)
            filters: Ek filtreler (user_id, story_id, vb.)
        """
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                analytics = json.load(f)
        except:
            return {}
        
        results = {}
        
        # Tarih filtreleme yardımcı fonksiyonu
        def is_in_date_range(timestamp_str):
            if not timestamp_str:
                return False
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if start_date and dt < datetime.fromisoformat(start_date):
                return False
            if end_date and dt > datetime.fromisoformat(end_date):
                return False
            return True
        
        # Filtreleme yardımcı fonksiyonu
        def matches_filters(item_data):
            if not filters:
                return True
            for k, v in filters.items():
                if item_data.get(k) != v:
                    return False
            return True

        # Metrik tipine göre işlem
        if metric_type == "scroll_depth":
            for story_id, data in analytics.items():
                if filters and filters.get('story_id') and filters['story_id'] != story_id:
                    continue
                
                filtered_scrolls = [
                    s for s in data.get('scroll_data', [])
                    if is_in_date_range(s.get('timestamp')) and matches_filters(s)
                ]
                
                if filtered_scrolls:
                    results[story_id] = filtered_scrolls

        elif metric_type == "heatmap":
            for story_id, data in analytics.items():
                if filters and filters.get('story_id') and filters['story_id'] != story_id:
                    continue
                results[story_id] = data.get('heatmap_data', {})

        return results

