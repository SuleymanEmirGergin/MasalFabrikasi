"""
Enhanced Parental Dashboard Service - Gelişmiş ebeveyn dashboard'u
Çocuk okuma gelişimi, kelime dağarcığı analizi
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta
from app.models import Story
from app.services.reading_analytics_service import ReadingAnalyticsService


class EnhancedParentalService:
    """Ebeveynler için gelişmiş analiz ve raporlama"""
    
    # Yaş gruplarına göre kelime dağarcığı ortalama artışı (aylık)
    VOCAB_GROWTH_ESTIMATES = {
        "3-6": 50,   # 3-6 yaş: ayda ~50 kelime
        "7-10": 100,  # 7-10 yaş: ayda ~100 kelime
        "11+": 150    # 11+: ayda ~150 kelime
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_child_reading_development(self, child_user_id: uuid.UUID, age_group: str = "7-10") -> Dict:
        """
        Çocuğun okuma gelişimini analiz eder
        
        Args:
            child_user_id: Çocuk kullanıcı ID
            age_group: Yaş grubu ("3-6", "7-10", "11+")
        
        Returns:
            Gelişim raporu
        """
        analytics = ReadingAnalyticsService(self.db)
        stats = analytics.get_reading_stats(child_user_id)
        distribution = analytics.get_reading_distribution(child_user_id)
        
        # Kelime dağarcığı tahmini
        months_active = self._calculate_months_active(child_user_id)
        estimated_vocab_growth = months_active * self.VOCAB_GROWTH_ESTIMATES.get(age_group, 100)
        
        # Okuma hızı gelişimi (hikaye/hafta artışı)
        weekly_growth = self._calculate_reading_pace_growth(child_user_id)
        
        # Tür çeşitliliği skoru
        diversity_score = len(distribution["by_type"]) * 20  # Her tür +20 puan
        
        return {
            "total_stories_read": stats["total_stories_read"],
            "current_streak": stats["current_streak_days"],
            "estimated_vocabulary_growth": estimated_vocab_growth,
            "reading_pace_growth_percentage": weekly_growth,
            "genre_diversity_score": min(100, diversity_score),
            "consistency_score": self._calculate_consistency_score(stats),
            "months_active": months_active,
            "developmental_insights": self._generate_developmental_insights(
                stats, distribution, age_group
            )
        }
    
    def get_topic_distribution_analysis(self, child_user_id: uuid.UUID) -> Dict:
        """
        Okunan konuların detaylı dağılımı ve yorumu
        
        Returns:
            - Tür dağılımı
            - En sevilen konular
            - Eksik kalan alanlar
            - Öneriler
        """
        analytics = ReadingAnalyticsService(self.db)
        distribution = analytics.get_reading_distribution(child_user_id)
        
        # Tür dağılımı analizi
        type_analysis = {}
        total_stories = sum(item["count"] for item in distribution["by_type"])
        
        for item in distribution["by_type"]:
            percentage = (item["count"] / total_stories * 100) if total_stories > 0 else 0
            type_analysis[item["type"]] = {
                "count": item["count"],
                "percentage": round(percentage, 1)
            }
        
        # Eksik alanlar
        all_types = ["masal", "macera", "bilimkurgu", "eğitici", "komedi"]
        missing_types = [t for t in all_types if t not in type_analysis]
        
        return {
            "type_distribution": type_analysis,
            "favorite_topics": self._get_top_topics(distribution),
            "underexplored_areas": missing_types,
            "recommendations": self._generate_topic_recommendations(type_analysis, missing_types)
        }
    
    def compare_with_age_group(self, child_user_id: uuid.UUID, age_group: str) -> Dict:
        """
        Çocuğu yaş grubundaki ortalama ile karşılaştırır
        
        Returns:
            - Ortalamanın üstünde/altında olduğu metrikler
            - Güçlü yönler
            - Gelişim alanları
        """
        # Yaş grubu ortalama değerleri (example benchmarks)
        AGE_BENCHMARKS = {
            "3-6": {
                "avg_stories_per_month": 8,
                "avg_streak": 3,
                "avg_diversity": 3
            },
            "7-10": {
                "avg_stories_per_month": 12,
                "avg_streak": 5,
                "avg_diversity": 4
            },
            "11+": {
                "avg_stories_per_month": 15,
                "avg_streak": 7,
                "avg_diversity": 5
            }
        }
        
        benchmark = AGE_BENCHMARKS.get(age_group, AGE_BENCHMARKS["7-10"])
        
        analytics = ReadingAnalyticsService(self.db)
        stats = analytics.get_reading_stats(child_user_id)
        distribution = analytics.get_reading_distribution(child_user_id)
        
        child_metrics = {
            "stories_per_month": stats["stories_this_month"],
            "current_streak": stats["current_streak_days"],
            "diversity": len(distribution["by_type"])
        }
        
        comparison = {}
        strengths = []
        improvement_areas = []
        
        for metric, child_value in child_metrics.items():
            avg_key = f"avg_{metric}"
            avg_value = benchmark.get(avg_key, 0)
            
            difference_pct = ((child_value - avg_value) / avg_value * 100) if avg_value > 0 else 0
            
            comparison[metric] = {
                "child_value": child_value,
                "age_average": avg_value,
                "difference_percentage": round(difference_pct, 1),
                "above_average": child_value > avg_value
            }
            
            if child_value > avg_value:
                strengths.append(self._metric_to_readable(metric))
            else:
                improvement_areas.append(self._metric_to_readable(metric))
        
        return {
            "age_group": age_group,
            "comparison": comparison,
            "strengths": strengths,
            "improvement_areas": improvement_areas,
            "overall_performance": "above_average" if len(strengths) > len(improvement_areas) else "developing"
        }
    
    def _calculate_months_active(self, user_id: uuid.UUID) -> float:
        """İlk hikayeden bu yana kaç ay geçtiğini hesaplar"""
        first_story = self.db.query(Story).filter(
            Story.user_id == user_id
        ).order_by(Story.created_at.asc()).first()
        
        if not first_story:
            return 0
        
        delta = datetime.now() - first_story.created_at
        return max(1, delta.days / 30)
    
    def _calculate_reading_pace_growth(self, user_id: uuid.UUID) -> float:
        """Son ayın okuma hızını önceki aya göre karşılaştırır"""
        now = datetime.now()
        last_month_start = now - timedelta(days=30)
        two_months_ago = now - timedelta(days=60)
        
        last_month = self.db.query(Story).filter(
            Story.user_id == user_id,
            Story.created_at >= last_month_start
        ).count()
        
        previous_month = self.db.query(Story).filter(
            Story.user_id == user_id,
            Story.created_at >= two_months_ago,
            Story.created_at < last_month_start
        ).count()
        
        if previous_month == 0:
            return 100 if last_month > 0 else 0
        
        growth = ((last_month - previous_month) / previous_month) * 100
        return round(growth, 1)
    
    def _calculate_consistency_score(self, stats: Dict) -> int:
        """Okuma tutarlılığı skoru (0-100)"""
        streak_score = min(50, stats["current_streak_days"] * 7)
        volume_score = min(50, stats["stories_this_month"] * 4)
        return int(streak_score + volume_score)
    
    def _generate_developmental_insights(
        self,
        stats: Dict,
        distribution: Dict,
        age_group: str
    ) -> List[str]:
        """Gelişim içgörüleri üretir"""
        insights = []
        
        if stats["current_streak_days"] >= 7:
            insights.append("✅ Mükemmel okuma düzeni! Günlük okuma alışkanlığı yerleşmiş.")
        
        if len(distribution["by_type"]) >= 4:
            insights.append("🌈 Geniş tür yelpazesi! Farklı konulara ilgi gösteriyor.")
        
        if stats["stories_this_month"] >= 15:
            insights.append("📚 Yüksek okuma hacmi! Yaşıtlarının üzerinde performans.")
        
        return insights
    
    def _get_top_topics(self, distribution: Dict) -> List[str]:
        """En popüler konuları getirir"""
        if not distribution["by_type"]:
            return []
        
        sorted_types = sorted(
            distribution["by_type"],
            key=lambda x: x["count"],
            reverse=True
        )
        
        return [item["type"] for item in sorted_types[:3]]
    
    def _generate_topic_recommendations(
        self,
        type_analysis: Dict,
        missing_types: List[str]
    ) -> List[str]:
        """Konu önerileri üretir"""
        recommendations = []
        
        if missing_types:
            recommendations.append(
                f"Yeni türleri keşfetmeyi deneyin: {', '.join(missing_types[:2])}"
            )
        
        if len(type_analysis) <= 2:
            recommendations.append("Farklı türlerde hikayeler okuyarak kelime dağarcığını genişletebilir.")
        
        return recommendations
    
    def _metric_to_readable(self, metric: str) -> str:
        """Metrik isimlerini okunabilir hale getirir"""
        readable = {
            "stories_per_month": "Aylık okuma sayısı",
            "current_streak": "Günlük okuma serisi",
            "diversity": "Tür çeşitliliği"
        }
        return readable.get(metric, metric)
