from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.services.reading_goals_service import ReadingGoalsService
from app.services.story_rating_service import StoryRatingService
from app.services.backup_sync_service import BackupSyncService
from app.services.personalization_service import PersonalizationService
from app.services.story_security_service import StorySecurityService
from app.services.mobile_features_service import MobileFeaturesService
from app.services.mood_recommendation_service import MoodRecommendationService
from app.services.curated_collections_service import CuratedCollectionsService
from app.services.ai_gamification_advanced_service import AIGamificationAdvancedService
from app.services.ai_backup_advanced_service import AIBackupAdvancedService
from app.services.security_privacy_advanced_service import SecurityPrivacyAdvancedService
from app.services.interactive_gamification_service import InteractiveGamificationService
from app.services.story_gamification_badges_service import StoryGamificationBadgesService
from app.services.story_favorites_service import StoryFavoritesService
from app.services.story_notifications_service import StoryNotificationsService
from app.services.story_activity_log_service import StoryActivityLogService

router = APIRouter()

reading_goals_service = ReadingGoalsService()
story_rating_service = StoryRatingService()
backup_sync_service = BackupSyncService()
personalization_service = PersonalizationService()
story_security_service = StorySecurityService()
mobile_features_service = MobileFeaturesService()
mood_recommendation_service = MoodRecommendationService()
curated_collections_service = CuratedCollectionsService()
ai_gamification_advanced_service = AIGamificationAdvancedService()
ai_backup_advanced_service = AIBackupAdvancedService()
security_privacy_advanced_service = SecurityPrivacyAdvancedService()
interactive_gamification_service = InteractiveGamificationService()
story_gamification_badges_service = StoryGamificationBadgesService()
story_favorites_service = StoryFavoritesService()
story_notifications_service = StoryNotificationsService()
story_activity_log_service = StoryActivityLogService()


# ========== Okuma Hedefleri ==========
class GoalRequest(BaseModel):
    goal_type: str
    target: int
    period: str = "weekly"


@router.post("/users/{user_id}/reading-goals")
async def create_goal(user_id: str, request: GoalRequest):
    return reading_goals_service.create_reading_goal(user_id, request.goal_type, request.target, request.period)


# ========== Hikâye Derecelendirme ==========
class RateRequest(BaseModel):
    rating: float
    review_text: Optional[str] = None


@router.post("/stories/{story_id}/rate")
async def rate_story(story_id: str, user_id: str, request: RateRequest):
    try:
        if request.review_text:
            return story_rating_service.add_review(story_id, user_id, request.rating, request.review_text)
        return story_rating_service.rate_story(story_id, user_id, request.rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stories/{story_id}/rating")
async def get_story_rating(story_id: str):
    return story_rating_service.get_story_rating(story_id)


# ========== Yedekleme ==========
@router.post("/users/{user_id}/backup")
async def create_backup(user_id: str, backup_name: Optional[str] = None):
    return backup_sync_service.create_backup(user_id, backup_name)


@router.get("/users/{user_id}/backups")
async def get_backups(user_id: str):
    return {"backups": backup_sync_service.get_user_backups(user_id)}


@router.post("/users/{user_id}/smart-backup")
async def schedule_smart_backup(user_id: str, backup_frequency: str = "daily", backup_time: str = "02:00"):
    return ai_backup_advanced_service.schedule_smart_backup(user_id, backup_frequency, backup_time)


@router.post("/users/{user_id}/optimize-backup")
async def optimize_backup(user_id: str):
    return ai_backup_advanced_service.optimize_backup_size(user_id)


# ========== Kişiselleştirme ==========
@router.get("/users/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    return personalization_service.get_user_preferences(user_id)


@router.put("/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: Dict):
    return personalization_service.update_user_preferences(user_id, preferences)


@router.get("/personalization/themes")
async def get_available_themes():
    return {"themes": personalization_service.get_available_themes()}


@router.get("/personalization/fonts")
async def get_available_fonts():
    return {"fonts": personalization_service.get_available_fonts()}


# ========== Güvenlik ==========
class AccessControlRequest(BaseModel):
    allowed_users: List[str]
    password: Optional[str] = None


@router.post("/stories/{story_id}/access-control")
async def set_access_control(story_id: str, user_id: str, request: AccessControlRequest):
    try:
        return story_security_service.set_access_control(story_id, user_id, request.allowed_users, request.password)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stories/{story_id}/check-access")
async def check_access(story_id: str, user_id: str, password: Optional[str] = None):
    has_access = story_security_service.check_access(story_id, user_id, password)
    if not has_access:
        raise HTTPException(status_code=403, detail="Erişim reddedildi")
    return {"access": "granted"}


@router.get("/stories/{story_id}/access-logs")
async def get_access_logs(story_id: str, limit: int = 50):
    return {"logs": story_security_service.get_access_logs(story_id, limit)}


@router.post("/security/2fa/enable")
async def enable_two_factor_auth(user_id: str):
    return security_privacy_advanced_service.enable_two_factor_auth(user_id)


@router.post("/security/2fa/verify")
async def verify_two_factor_code(user_id: str, code: str):
    return {"verified": security_privacy_advanced_service.verify_two_factor_code(user_id, code)}


@router.put("/privacy/{user_id}")
async def set_privacy_settings(user_id: str, settings: Dict):
    return security_privacy_advanced_service.set_privacy_settings(user_id, settings)


# ========== Mobil Özellikler ==========
@router.post("/mobile/offline/{user_id}")
async def mark_story_for_offline(user_id: str, story_id: str):
    return mobile_features_service.mark_story_for_offline(user_id, story_id)


@router.get("/mobile/notifications/{user_id}")
async def get_user_notifications(user_id: str, unread_only: bool = False):
    return {"notifications": mobile_features_service.get_user_notifications(user_id, unread_only)}


# ========== Oyunlaştırma (Temel & Advanced) ==========
class BadgeCheckRequest(BaseModel):
    user_id: str
    action_type: str
    action_data: Dict


@router.post("/gamification/check-badge")
async def check_and_award_badge(request: BadgeCheckRequest):
    return await story_gamification_badges_service.check_and_award_badge(
        request.user_id, request.action_type, request.action_data
    )


@router.get("/gamification/badges/{user_id}")
async def get_user_badges(user_id: str):
    return await story_gamification_badges_service.get_user_badges(user_id)


class CustomBadgeRequest(BaseModel):
    badge_name: str
    description: str
    criteria: Dict
    icon: str = "🏆"


@router.post("/gamification/create-badge")
async def create_custom_badge(request: CustomBadgeRequest):
    return await story_gamification_badges_service.create_custom_badge(
        request.badge_name, request.description, request.criteria, request.icon
    )


class BadgeRequest(BaseModel):
    badge_name: str
    description: str
    criteria: Dict
    icon_url: Optional[str] = None


@router.post("/gamification/dynamic-badge")
async def create_dynamic_badge(request: BadgeRequest):
    return ai_gamification_advanced_service.create_dynamic_badge(
        request.badge_name, request.description, request.criteria, request.icon_url
    )


@router.get("/users/{user_id}/level/{system_id}")
async def get_user_level(user_id: str, system_id: str, user_xp: int):
    return ai_gamification_advanced_service.calculate_user_level(user_id, system_id, user_xp)


# ========== İnteraktif Oyunlaştırma ==========
class ChoicePointRequest(BaseModel):
    position: int
    choices: List[Dict]


@router.post("/stories/{story_id}/choice-point")
async def add_choice_point(story_id: str, request: ChoicePointRequest):
    return interactive_gamification_service.add_choice_point(story_id, request.position, request.choices)


@router.post("/choices/{choice_id}/record")
async def record_choice(choice_id: str, user_id: str, selected_choice: int):
    return interactive_gamification_service.record_choice(choice_id, user_id, selected_choice)


@router.get("/stories/{story_id}/score/{user_id}")
async def get_story_score(story_id: str, user_id: str):
    return interactive_gamification_service.calculate_story_score(story_id, user_id)


# ========== Ruh Haline Göre Öneriler ==========
@router.get("/recommendations/mood/{user_id}")
async def get_mood_recs(user_id: str, mood: str, limit: int = 10):
    return {"recommendations": await mood_recommendation_service.get_mood_based_recommendations(user_id, mood, limit)}


# ========== Küratörlü Koleksiyonlar ==========
@router.post("/curated-collections")
async def create_curated(title: str, description: str, curator_id: str, is_featured: bool = False):
    return curated_collections_service.create_curated_collection(title, description, curator_id, is_featured)


@router.get("/curated-collections/featured")
async def get_featured_collections(limit: int = 10):
    return {"collections": curated_collections_service.get_featured_collections(limit)}
