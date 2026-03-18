from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.services.advanced_export_service import AdvancedExportService
from app.services.platform_integration_service import PlatformIntegrationService
from app.services.api_webhook_service import APIWebhookService
from app.services.performance_optimization_service import PerformanceOptimizationService
from app.services.integrations_service import IntegrationsService
from app.services.export_advanced_service import ExportAdvancedService
from app.services.filter_service import FilterService
from app.services.search_filters_service import SearchFiltersService
from app.services.story_storage import StoryStorage

router = APIRouter()

advanced_export_service = AdvancedExportService()
platform_integration_service = PlatformIntegrationService()
api_webhook_service = APIWebhookService()
performance_optimization_service = PerformanceOptimizationService()
integrations_service = IntegrationsService()
export_advanced_service = ExportAdvancedService()
filter_service = FilterService()
search_filters_service = SearchFiltersService()
story_storage = StoryStorage()


# ========== Gelişmiş Dışa Aktarma ==========
@router.post("/stories/{story_id}/export/word")
async def export_word(story_id: str, title: Optional[str] = None):
    try:
        return advanced_export_service.export_to_word(story_id, title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stories/{story_id}/export/markdown")
async def export_markdown(story_id: str):
    try:
        return advanced_export_service.export_to_markdown(story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/integrations/ebook-platform")
async def export_to_ebook_platform(story_id: str, platform: str, credentials: Dict):
    return integrations_service.export_to_ebook_platform(story_id, platform, credentials)


# ========== Platform Entegrasyonları ==========
@router.post("/integrations/wordpress")
async def connect_wp(user_id: str, site_url: str, api_key: str):
    return platform_integration_service.connect_wordpress(user_id, site_url, api_key)


@router.post("/integrations/social-media")
async def publish_to_social_media(story_id: str, platform: str, access_token: str):
    return integrations_service.publish_to_social_media(story_id, platform, access_token)


# ========== Webhooklar ==========
class WebhookRequest(BaseModel):
    url: str
    events: List[str]
    secret: Optional[str] = None


@router.post("/webhooks")
async def create_webhook(user_id: str, request: WebhookRequest):
    return api_webhook_service.create_webhook(user_id, request.url, request.events, request.secret)


# ========== Performans Optimizasyonu ==========
@router.post("/stories/{story_id}/cache")
async def cache_story(story_id: str, ttl: int = 3600):
    story = story_storage.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    performance_optimization_service.cache_story_data(story_id, story, ttl)
    return {"message": "Hikâye önbelleğe alındı"}


@router.get("/stories/{story_id}/lazy-load")
async def lazy_load_story(story_id: str, load_images: bool = False, load_audio: bool = False):
    return performance_optimization_service.lazy_load_story(story_id, load_images, load_audio)


# ========== Filtreleme ==========
@router.post("/stories/filter")
async def filter_stories(filters: Dict, sort_by: str = "created_at", sort_order: str = "desc", limit: int = 50):
    return {"stories": filter_service.filter_stories(filters, sort_by, sort_order, limit)}


@router.get("/stories/filter-options")
async def get_filter_options():
    return filter_service.get_filter_options()
