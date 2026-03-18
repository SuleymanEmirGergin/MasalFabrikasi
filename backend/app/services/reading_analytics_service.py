"""
Reading Analytics Service - Okuma istatistikleri ve gelişim takibi
Maliyet artırmayan, sadece DB tabanlı analiz servisi
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.models import Story, UserProfile
import uuid


class ReadingAnalyticsService:
    """Kullanıcı okuma istatistikleri ve analiz servisi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_reading_stats(self, user_id: uuid.UUID) -> Dict:
        """
        Kullanıcının okuma istatistiklerini getirir
        
        Returns:
            - total_stories_read: Toplam okunan hikaye
            - total_reading_time: Tahmini toplam okuma süresi (dk)
            - favorite_count: Favori hikaye sayısı
            - stories_this_week: Bu hafta okunan
            - stories_this_month: Bu ay okunan
            - current_streak: Günlük okuma serisi
            - longest_streak: En uzun okuma serisi
        """
        # Toplam hikaye sayısı (user'a ait olanlar)
        total_stories = self.db.query(func.count(Story.id)).filter(
            Story.user_id == user_id
        ).scalar() or 0
        
        # Favori sayısı
        favorite_count = self.db.query(func.count(Story.id)).filter(
            and_(Story.user_id == user_id, Story.is_favorite == True)
        ).scalar() or 0
        
        # Bu hafta okunan
        week_ago = datetime.now() - timedelta(days=7)
        stories_this_week = self.db.query(func.count(Story.id)).filter(
            and_(Story.user_id == user_id, Story.created_at >= week_ago)
        ).scalar() or 0
        
        # Bu ay okunan
        month_ago = datetime.now() - timedelta(days=30)
        stories_this_month = self.db.query(func.count(Story.id)).filter(
            and_(Story.user_id == user_id, Story.created_at >= month_ago)
        ).scalar() or 0
        
        # Tahmini okuma süresi (ortalama 5 dk/hikaye varsayımı)
        total_reading_time = total_stories * 5
        
        # Streak hesaplama
        current_streak = self._calculate_current_streak(user_id)
        longest_streak = self._calculate_longest_streak(user_id)
        
        return {
            "total_stories_read": total_stories,
            "total_reading_time_minutes": total_reading_time,
            "favorite_count": favorite_count,
            "stories_this_week": stories_this_week,
            "stories_this_month": stories_this_month,
            "current_streak_days": current_streak,
            "longest_streak_days": longest_streak,
            "average_per_week": round(total_stories / max(1, (datetime.now() - week_ago).days / 7), 1)
        }
    
    def _calculate_current_streak(self, user_id: uuid.UUID) -> int:
        """Mevcut günlük okuma serisini hesaplar"""
        current_date = datetime.now().date()
        streak = 0
        
        while True:
            # O gün hikaye var mı kontrol et
            story_exists = self.db.query(Story).filter(
                and_(
                    Story.user_id == user_id,
                    func.date(Story.created_at) == current_date
                )
            ).first()
            
            if story_exists:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
                
            # Max 365 gün kontrolü (performans)
            if streak >= 365:
                break
        
        return streak
    
    def _calculate_longest_streak(self, user_id: uuid.UUID) -> int:
        """Şimdiye kadarki en uzun okuma serisini hesaplar"""
        # Son 1 yıldaki tüm hikayeleri çek
        year_ago = datetime.now() - timedelta(days=365)
        stories = self.db.query(Story.created_at).filter(
            and_(Story.user_id == user_id, Story.created_at >= year_ago)
        ).order_by(Story.created_at).all()
        
        if not stories:
            return 0
        
        # Günlere göre grupla
        reading_dates = set()
        for story in stories:
            reading_dates.add(story.created_at.date())
        
        # Sıralı listeye çevir
        sorted_dates = sorted(reading_dates)
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def get_reading_distribution(self, user_id: uuid.UUID) -> Dict:
        """
        Okuma dağılımını analiz eder
        
        Returns:
            - by_type: Hikaye türüne göre dağılım
            - by_language: Dile göre dağılım
            - by_hour: Saate göre okuma tercihi
            - by_day_of_week: Haftanın gününe göre
        """
        # Türlere göre
        by_type = self.db.query(
            Story.story_type,
            func.count(Story.id).label('count')
        ).filter(Story.user_id == user_id).group_by(Story.story_type).all()
        
        # Dillere göre
        by_language = self.db.query(
            Story.language,
            func.count(Story.id).label('count')
        ).filter(Story.user_id == user_id).group_by(Story.language).all()
        
        # Saatlere göre (created_at'ten saat çıkar)
        stories = self.db.query(Story.created_at).filter(Story.user_id == user_id).all()
        
        hour_distribution = {}
        day_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Pazartesi-Pazar
        
        for story in stories:
            hour = story.created_at.hour
            day = story.created_at.weekday()
            
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
            day_distribution[day] = day_distribution.get(day, 0) + 1
        
        return {
            "by_type": [{"type": t, "count": c} for t, c in by_type],
            "by_language": [{"language": l, "count": c} for l, c in by_language],
            "by_hour": [{"hour": h, "count": c} for h, c in sorted(hour_distribution.items())],
            "by_day_of_week": [{"day": d, "count": c} for d, c in sorted(day_distribution.items())]
        }
    
    def get_reading_goals(self, user_id: uuid.UUID) -> Dict:
        """
        Okuma hedeflerini ve ilerlemesini getirir
        
        Hedefler:
        - weekly_goal: Haftalık 3 hikaye
        - monthly_goal: Aylık 12 hikaye
        - streak_goal: 7 günlük seri
        """
        stats = self.get_reading_stats(user_id)
        
        weekly_goal = 3
        monthly_goal = 12
        streak_goal = 7
        
        return {
            "weekly": {
                "goal": weekly_goal,
                "current": stats["stories_this_week"],
                "percentage": min(100, int((stats["stories_this_week"] / weekly_goal) * 100))
            },
            "monthly": {
                "goal": monthly_goal,
                "current": stats["stories_this_month"],
                "percentage": min(100, int((stats["stories_this_month"] / monthly_goal) * 100))
            },
            "streak": {
                "goal": streak_goal,
                "current": stats["current_streak_days"],
                "percentage": min(100, int((stats["current_streak_days"] / streak_goal) * 100))
            }
        }
    
    def get_reading_insights(self, user_id: uuid.UUID) -> List[str]:
        """
        Kullanıcıya özel okuma içgörüleri ve öneriler üretir
        """
        stats = self.get_reading_stats(user_id)
        distribution = self.get_reading_distribution(user_id)
        insights = []
        
        # Streak insights
        if stats["current_streak_days"] >= 7:
            insights.append(f"🔥 Harika! {stats['current_streak_days']} gündür her gün okuyorsunuz!")
        elif stats["current_streak_days"] > 0:
            days_to_week = 7 - stats["current_streak_days"]
            insights.append(f"💪 {days_to_week} gün daha okuyarak 1 haftalık seriye ulaşabilirsiniz!")
        
        # Favorite type
        if distribution["by_type"]:
            top_type = max(distribution["by_type"], key=lambda x: x["count"])
            insights.append(f"📚 En sevdiğiniz tür: {top_type['type']} ({top_type['count']} hikaye)")
        
        # Peak reading time
        if distribution["by_hour"]:
            peak_hour = max(distribution["by_hour"], key=lambda x: x["count"])
            insights.append(f"⏰ En çok {peak_hour['hour']}:00 saatlerinde okuyorsunuz")
        
        # Total achievement
        if stats["total_stories_read"] >= 100:
            insights.append(f"🏆 100+ hikaye tamamladınız! İnanılmaz bir başarı!")
        elif stats["total_stories_read"] >= 50:
            insights.append(f"🌟 50+ hikaye okudunuz! 100'e çok yakınsınız!")
        
        return insights
