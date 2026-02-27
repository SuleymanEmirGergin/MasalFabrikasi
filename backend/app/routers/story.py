from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Optional, List, Union, Dict, Any
import uuid
import os
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from app.core.database import get_db

from app.services.story_service import StoryService
from app.services.image_service import ImageService
from app.services.tts_service import TTSService
from app.services.story_storage import StoryStorage
from app.core.cache import cache
from app.core.rate_limiter import limiter
from app.core.auth_dependencies import get_current_user
from fastapi import Request
from app.repositories.job_repository import JobRepository
from app.repositories.story_repository import StoryRepository
from app.models import JobStatus, JobType
from app.tasks.story_tasks import generate_full_story_task
from app.services.story_editor import StoryEditor
from app.services.multi_image_service import MultiImageService
from app.services.statistics_service import StatisticsService
from app.services.template_service import TemplateService
from app.services.collection_service import CollectionService
from app.services.export_service import ExportService
from app.services.interactive_story_service import InteractiveStoryService
from app.services.translation_service import TranslationService
from app.services.user_profile_service import UserProfileService
from app.services.dialogue_service import DialogueService
from app.services.character_service import CharacterService
from app.services.story_outline_service import StoryOutlineService
from app.services.comment_service import CommentService
from app.services.like_service import LikeService
from app.services.collaboration_service import CollaborationService
from app.services.voice_acting_service import VoiceActingService
from app.services.sound_effect_service import SoundEffectService
from app.services.story_versioning_service import StoryVersioningService
from app.services.story_analysis_service import StoryAnalysisService
from app.services.recommendation_service import RecommendationService
from app.services.music_service import MusicService
from app.services.story_comparison_service import StoryComparisonService
from app.services.community_service import CommunityService
from app.services.search_service import SearchService
from app.services.analytics_service import AnalyticsService
from app.services.story_series_service import StorySeriesService
from app.services.story_improvement_service import StoryImprovementService
from app.services.parental_control_service import ParentalControlService
from app.services.audio_recording_service import AudioRecordingService
from app.services.sharing_service import SharingService
from app.services.ebook_service import EbookService
from app.services.performance_metrics_service import PerformanceMetricsService
from app.services.ai_chatbot_service import AIChatbotService
from app.services.advanced_translation_service import AdvancedTranslationService
from app.services.voice_command_service import VoiceCommandService
from app.services.marketplace_service import MarketplaceService
from app.services.realtime_collaboration_service import RealtimeCollaborationService
from app.services.advanced_analytics_service import AdvancedAnalyticsService
from app.services.social_features_service import SocialFeaturesService
from app.services.story_scheduler_service import StorySchedulerService
from app.services.content_moderation_service import ContentModerationService
from app.services.plagiarism_service import PlagiarismService
from app.services.story_rating_service import StoryRatingService
from app.services.curated_collections_service import CuratedCollectionsService
from app.services.reading_goals_service import ReadingGoalsService
from app.services.mood_recommendation_service import MoodRecommendationService
from app.services.advanced_export_service import AdvancedExportService
from app.services.platform_integration_service import PlatformIntegrationService
from app.services.api_webhook_service import APIWebhookService
from app.services.template_marketplace_service import TemplateMarketplaceService
from app.services.voice_story_creation_service import VoiceStoryCreationService
from app.services.ar_vr_service import ARVRService
from app.services.timeline_service import TimelineService
from app.services.geolocation_service import GeolocationService
from app.services.backup_sync_service import BackupSyncService
from app.services.filter_service import FilterService
from app.services.reporting_service import ReportingService
from app.services.offline_service import OfflineService
from app.core.config import settings
from fastapi.responses import JSONResponse, FileResponse

router = APIRouter()
story_service = StoryService()
image_service = ImageService()
tts_service = TTSService()
story_storage = StoryStorage()
story_editor = StoryEditor()
multi_image_service = MultiImageService()
statistics_service = StatisticsService()
template_service = TemplateService()
collection_service = CollectionService()
export_service = ExportService()
interactive_story_service = InteractiveStoryService()
translation_service = TranslationService()
user_profile_service = UserProfileService()
dialogue_service = DialogueService()
character_service = CharacterService()
story_outline_service = StoryOutlineService()
comment_service = CommentService()
like_service = LikeService()
collaboration_service = CollaborationService()
voice_acting_service = VoiceActingService()
sound_effect_service = SoundEffectService()
story_versioning_service = StoryVersioningService()
story_analysis_service = StoryAnalysisService()
recommendation_service = RecommendationService()
music_service = MusicService()
story_comparison_service = StoryComparisonService()
community_service = CommunityService()
# search_service = SearchService() # Requires DB session, instantiated in endpoints
analytics_service = AnalyticsService()
story_series_service = StorySeriesService()
story_improvement_service = StoryImprovementService()
parental_control_service = ParentalControlService()
audio_recording_service = AudioRecordingService()
sharing_service = SharingService()
ebook_service = EbookService()
performance_metrics_service = PerformanceMetricsService()
ai_chatbot_service = AIChatbotService()
advanced_translation_service = AdvancedTranslationService()
voice_command_service = VoiceCommandService()
marketplace_service = MarketplaceService()
realtime_collaboration_service = RealtimeCollaborationService()
advanced_analytics_service = AdvancedAnalyticsService()
social_features_service = SocialFeaturesService()
# story_scheduler_service = StorySchedulerService() # Requires DB session
content_moderation_service = ContentModerationService()
plagiarism_service = PlagiarismService()
story_rating_service = StoryRatingService()
curated_collections_service = CuratedCollectionsService()
reading_goals_service = ReadingGoalsService()
mood_recommendation_service = MoodRecommendationService()
advanced_export_service = AdvancedExportService()
platform_integration_service = PlatformIntegrationService()
api_webhook_service = APIWebhookService()
template_marketplace_service = TemplateMarketplaceService()
voice_story_creation_service = VoiceStoryCreationService()
ar_vr_service = ARVRService()
timeline_service = TimelineService()
geolocation_service = GeolocationService()
backup_sync_service = BackupSyncService()
filter_service = FilterService()
reporting_service = ReportingService()
offline_service = OfflineService()


class StoryRequest(BaseModel):
    theme: str
    language: str = "tr"  # Türkçe varsayılan
    story_type: str = "masal"  # Hikâye türü
    save: bool = True  # Otomatik kaydet
    image_style: str = "fantasy"  # Görsel stili
    image_size: str = "1024x1024"  # Görsel boyutu
    audio_speed: float = 1.0  # Ses hızı (0.5 - 2.0)
    audio_slow: bool = False  # Yavaş konuşma (gTTS için)
    use_async: bool = True  # Asenkron üretim (Job Queue)
    
    # Advanced Settings
    creativity: float = 0.8 # 0.0 - 1.0
    pacing: str = "medium" # slow, medium, fast
    perspective: str = "third" # first, third
    vocabulary: str = "normal" # simple, normal, complex


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    position: Optional[int] = 0


class StoryResponse(BaseModel):
    story_id: str
    story_text: str
    image_url: str
    audio_url: str
    created_at: str
    theme: Optional[str] = None
    language: Optional[str] = None
    story_type: Optional[str] = None
    is_favorite: Optional[bool] = False
    # Gamification
    xp_gained: int = 0
    new_level: Optional[int] = None
    leveled_up: bool = False
    level_message: Optional[str] = None


class StoryListItem(BaseModel):
    story_id: str
    theme: str
    story_text: str
    image_url: str
    created_at: str
    story_type: str
    is_favorite: bool


@router.post("/generate-story", response_model=Union[StoryResponse, JobResponse])
@limiter.limit("5/minute")
async def generate_story(
    request: Request, # Required for limiter
    story_request: StoryRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Kullanıcının verdiği temaya göre hikâye, görsel ve ses üretir.
    Varsayılan olarak asenkron çalışır (Job Queue).
    """
    try:
        user_id = current_user.get("id")

        if request.use_async:
            # --- ASYNC JOB FLOW ---
            job_repo = JobRepository(db)
            
            job_data = {
                "user_id": user_id,
                "job_type": JobType.COMPLETE_STORY,
                "input_data": story_request.dict(exclude={"save", "use_async"})
            }
            
            job = job_repo.create_job(job_data)
            
            # Celery task'ı başlat
            task = generate_full_story_task.delay(str(job.id))
            
            # Update job with celery task id (async)
            # job_repo.update_job_status(job.id, JobStatus.QUEUED, celery_task_id=task.id)
            # Yukarıdaki create_job sonrası update yerine, worker içinde update ediyoruz 
            # veya burada yapabiliriz ama db session sorun olmasın diye worker'a bırakalım
            
            return JobResponse(
                job_id=str(job.id),
                status="queued",
                message="Hikaye oluşturma işlemi sıraya alındı.",
                position=1
            )
            
        else:
            # --- SYNC FLOW (Legacy) ---
            story_id = str(uuid.uuid4())
            
            # 1. Hikâye metni üretimi
            story_text = await story_service.generate_story(
                story_request.theme, 
                story_request.language,
                story_request.story_type,
                creativity=story_request.creativity,
                pacing=story_request.pacing,
                perspective=story_request.perspective,
                vocabulary=story_request.vocabulary
            )
            
            # 2. Görsel üretimi
            image_url = await image_service.generate_image(
                story_text, 
                story_request.theme,
                image_style=story_request.image_style,
                image_size=story_request.image_size
            )
            
            # 3. Seslendirme
            audio_url = await tts_service.generate_speech(
                story_text, 
                story_request.language, 
                story_id,
                audio_speed=story_request.audio_speed,
                audio_slow=story_request.audio_slow
            )
            
            created_at = datetime.now().isoformat()
            
            # Hikâyeyi kaydet
            story_data = {
                'story_id': story_id,
                'story_text': story_text,
                'image_url': image_url,
                'audio_url': audio_url,
                'theme': story_request.theme,
                'language': story_request.language,
                'story_type': story_request.story_type,
                'created_at': created_at,
            }
            
            if story_request.save:
                saved_story = story_storage.save_story(story_data)
                story_data['is_favorite'] = saved_story.get('is_favorite', False)
            
            # Gamification: Award XP
            xp_result = user_profile_service.add_xp(50)  # 50 XP per story
            
            return StoryResponse(
                story_id=story_id,
                story_text=story_text,
                image_url=image_url,
                audio_url=audio_url,
                created_at=created_at,
                theme=story_request.theme,
                language=story_request.language,
                story_type=story_request.story_type,
                is_favorite=story_data.get('is_favorite', False),
                # Gamification info
                xp_gained=xp_result['xp_gained'],
                new_level=xp_result['level'],
                leveled_up=xp_result['leveled_up'],
                level_message=xp_result['message']
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye üretilirken hata oluştu: {str(e)}")


@router.get("/jobs/{job_id}", response_model=Union[JobResponse, StoryResponse])
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Job durumunu sorgular. Job tamamlanmışsa sonucu döndürür.
    """
    try:
        job_repo = JobRepository(db)
        job = job_repo.get_job_by_id(uuid.UUID(job_id))
        
        if not job:
            raise HTTPException(status_code=404, detail="İşlem bulunamadı")
            
        if job.status == JobStatus.SUCCEEDED:
            # Sonuç verisini döndür
            result = job.result_data
            return StoryResponse(
                story_id=result.get("story_id"),
                story_text="Hikaye tamamlandı", # Detaylı veriyi story endpointinden çekmek gerekebilir
                image_url=result.get("image_url"),
                audio_url=result.get("audio_url"),
                created_at=str(job.completed_at),
                is_favorite=False
            )
            
        return JobResponse(
            job_id=str(job.id),
            status=job.status,
            message=f"{job.current_step} (%{job.progress_percent})",
            position=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stories", response_model=List[StoryListItem])
@cache(expire_seconds=60)
async def get_stories(
    limit: Optional[int] = Query(None, ge=1, le=100),
    favorite_only: bool = Query(False),
    search: Optional[str] = Query(None),
    story_type: Optional[str] = Query(None),
    sort_by: str = Query("date_desc")
):
    """
    Tüm hikâyeleri listeler (arama ve filtreleme ile).
    """
    try:
        stories = story_storage.get_all_stories(
            limit=limit,
            favorite_only=favorite_only,
            search_query=search,
            story_type=story_type,
            sort_by=sort_by
        )
        return stories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâyeler yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}", response_model=StoryResponse)
@cache(expire_seconds=300)
async def get_story(story_id: str):
    """
    Belirli bir hikâyeyi getirir.
    """
    story = story_storage.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    return story


@router.post("/stories/{story_id}/favorite")
async def toggle_favorite(story_id: str):
    """
    Hikâyeyi favorilere ekler/çıkarır.
    """
    story = story_storage.toggle_favorite(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    return {"story_id": story_id, "is_favorite": story.get('is_favorite', False)}


@router.delete("/stories/{story_id}")
async def delete_story(story_id: str):
    """
    Bir hikâyeyi siler.
    """
    success = story_storage.delete_story(story_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    return {"message": "Hikâye silindi", "story_id": story_id}


@router.get("/stories/stats/summary")
@cache(expire_seconds=300)
async def get_statistics():
    """
    Hikâye istatistiklerini getirir (basit).
    """
    try:
        stats = story_storage.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistikler yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/stats/detailed")
@cache(expire_seconds=300)
async def get_detailed_statistics():
    """
    Detaylı hikâye istatistiklerini getirir.
    """
    try:
        stats = statistics_service.get_detailed_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detaylı istatistikler yüklenirken hata oluştu: {str(e)}")


@router.get("/templates")
@cache(expire_seconds=3600)
async def get_templates(category: Optional[str] = Query(None)):
    """
    Hikâye şablonlarını getirir.
    """
    try:
        templates = template_service.get_all_templates(category=category)
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Şablonlar yüklenirken hata oluştu: {str(e)}")


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Belirli bir şablonu getirir.
    """
    try:
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Şablon bulunamadı")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Şablon yüklenirken hata oluştu: {str(e)}")


@router.get("/templates/categories/list")
async def get_template_categories():
    """
    Şablon kategorilerini getirir.
    """
    try:
        categories = template_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kategoriler yüklenirken hata oluştu: {str(e)}")


class CollectionRequest(BaseModel):
    name: str
    description: str = ""


@router.post("/collections")
async def create_collection(request: CollectionRequest):
    """
    Yeni bir koleksiyon oluşturur.
    """
    try:
        collection = collection_service.create_collection(request.name, request.description)
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon oluşturulurken hata oluştu: {str(e)}")


@router.get("/collections")
async def get_all_collections():
    """
    Tüm koleksiyonları getirir.
    """
    try:
        collections = collection_service.get_all_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyonlar yüklenirken hata oluştu: {str(e)}")


@router.get("/collections/{collection_id}")
async def get_collection(collection_id: str):
    """
    Belirli bir koleksiyonu getirir.
    """
    try:
        collection = collection_service.get_collection(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Koleksiyon bulunamadı")
        
        # Hikâyeleri de getir
        stories = collection_service.get_collection_stories(collection_id, story_storage)
        collection['stories'] = stories
        
        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon yüklenirken hata oluştu: {str(e)}")


@router.put("/collections/{collection_id}")
async def update_collection(collection_id: str, request: CollectionRequest):
    """
    Koleksiyonu günceller.
    """
    try:
        collection = collection_service.update_collection(
            collection_id,
            name=request.name,
            description=request.description
        )
        if not collection:
            raise HTTPException(status_code=404, detail="Koleksiyon bulunamadı")
        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon güncellenirken hata oluştu: {str(e)}")


@router.delete("/collections/{collection_id}")
async def delete_collection(collection_id: str):
    """
    Bir koleksiyonu siler.
    """
    try:
        success = collection_service.delete_collection(collection_id)
        if not success:
            raise HTTPException(status_code=404, detail="Koleksiyon bulunamadı")
        return {"message": "Koleksiyon silindi", "collection_id": collection_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon silinirken hata oluştu: {str(e)}")


@router.post("/collections/{collection_id}/stories/{story_id}")
async def add_story_to_collection(collection_id: str, story_id: str):
    """
    Koleksiyona hikâye ekler.
    """
    try:
        collection = collection_service.add_story_to_collection(collection_id, story_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Koleksiyon bulunamadı")
        return {"message": "Hikâye koleksiyona eklendi", "collection": collection}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye eklenirken hata oluştu: {str(e)}")


@router.delete("/collections/{collection_id}/stories/{story_id}")
async def remove_story_from_collection(collection_id: str, story_id: str):
    """
    Koleksiyondan hikâye çıkarır.
    """
    try:
        collection = collection_service.remove_story_from_collection(collection_id, story_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Koleksiyon bulunamadı")
        return {"message": "Hikâye koleksiyondan çıkarıldı", "collection": collection}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye çıkarılırken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/export/pdf")
async def export_story_to_pdf(story_id: str):
    """
    Hikâyeyi PDF formatında dışa aktarır.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        pdf_path = await export_service.export_to_pdf(story)
        full_path = f"{settings.STORAGE_PATH}{pdf_path}"
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=500, detail="PDF oluşturulamadı")
        
        return FileResponse(
            full_path,
            media_type='application/pdf',
            filename=f"hikaye_{story_id}.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF dışa aktarma hatası: {str(e)}")


@router.get("/stories/{story_id}/export/epub")
async def export_story_to_epub(story_id: str):
    """
    Hikâyeyi EPUB formatında dışa aktarır.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        epub_path = await export_service.export_to_epub(story)
        full_path = f"{settings.STORAGE_PATH}{epub_path}"
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=500, detail="EPUB oluşturulamadı")
        
        return FileResponse(
            full_path,
            media_type='application/epub+zip',
            filename=f"hikaye_{story_id}.epub"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EPUB dışa aktarma hatası: {str(e)}")


class InteractiveStoryRequest(BaseModel):
    theme: str
    language: str = "tr"
    story_type: str = "masal"
    num_choices: int = 2


class InteractiveStoryResponse(BaseModel):
    story_id: Optional[str] = None
    current_part: str
    choices: List[dict]
    image_url: str
    theme: str
    language: str
    story_type: str
    story_path: List[str]
    choice_history: List[int]
    is_complete: bool = False


@router.post("/interactive-story/generate", response_model=InteractiveStoryResponse)
async def generate_interactive_story(request: InteractiveStoryRequest):
    """
    Etkileşimli hikâye oluşturur.
    """
    try:
        story = await interactive_story_service.generate_interactive_story(
            request.theme,
            request.language,
            request.story_type,
            request.num_choices
        )
        return InteractiveStoryResponse(**story)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Etkileşimli hikâye oluşturulurken hata oluştu: {str(e)}")


class ContinueStoryRequest(BaseModel):
    current_story: dict
    choice_index: int


@router.post("/interactive-story/continue", response_model=InteractiveStoryResponse)
async def continue_interactive_story(request: ContinueStoryRequest):
    """
    Etkileşimli hikâyeyi devam ettirir.
    """
    try:
        story = await interactive_story_service.continue_story(
            request.current_story,
            request.choice_index
        )
        return InteractiveStoryResponse(**story)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye devam ettirilirken hata oluştu: {str(e)}")


@router.get("/languages")
async def get_supported_languages():
    """
    Desteklenen dilleri getirir.
    """
    try:
        languages = translation_service.get_supported_languages()
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diller yüklenirken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/translate")
async def translate_story(story_id: str, target_language: str):
    """
    Hikâyeyi belirtilen dile çevirir.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        translated_story = await translation_service.translate_story(story, target_language)
        
        # Çevrilmiş hikâyeyi yeni bir hikâye olarak kaydet
        import uuid
        translated_story['story_id'] = str(uuid.uuid4())
        translated_story['created_at'] = datetime.now().isoformat()
        translated_story['is_translation'] = True
        translated_story['original_story_id'] = story_id
        
        saved_story = story_storage.save_story(translated_story)
        
        return StoryResponse(
            story_id=saved_story.get('story_id'),
            story_text=saved_story.get('story_text'),
            image_url=saved_story.get('image_url'),
            audio_url=saved_story.get('audio_url'),
            created_at=saved_story.get('created_at'),
            theme=saved_story.get('theme'),
            language=saved_story.get('language'),
            story_type=saved_story.get('story_type'),
            is_favorite=saved_story.get('is_favorite', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye çevrilirken hata oluştu: {str(e)}")


@router.get("/user/profile")
async def get_user_profile():
    """
    Kullanıcı profilini getirir.
    """
    try:
        profile = user_profile_service.get_profile()
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profil yüklenirken hata oluştu: {str(e)}")


class PreferencesRequest(BaseModel):
    default_language: Optional[str] = None
    default_story_type: Optional[str] = None
    default_image_style: Optional[str] = None
    default_image_size: Optional[str] = None
    default_audio_speed: Optional[float] = None
    theme: Optional[str] = None


@router.put("/user/preferences")
async def update_user_preferences(request: PreferencesRequest):
    """
    Kullanıcı tercihlerini günceller.
    """
    try:
        preferences = {}
        if request.default_language is not None:
            preferences['default_language'] = request.default_language
        if request.default_story_type is not None:
            preferences['default_story_type'] = request.default_story_type
        if request.default_image_style is not None:
            preferences['default_image_style'] = request.default_image_style
        if request.default_image_size is not None:
            preferences['default_image_size'] = request.default_image_size
        if request.default_audio_speed is not None:
            preferences['default_audio_speed'] = request.default_audio_speed
        if request.theme is not None:
            preferences['theme'] = request.theme
            
        updated_profile = user_profile_service.update_preferences(preferences)
        return {"message": "Tercihler güncellendi", "preferences": updated_profile.get('preferences')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tercihler güncellenirken hata oluştu: {str(e)}")


@router.get("/stories/search/semantic", response_model=List[StoryListItem])
def search_stories_semantic(
    q: str, 
    limit: int = 5, 
    db: Session = Depends(get_db)
):
    """
    Semantic search for stories using vector embeddings (OpenAI & pgvector).
    """
    from app.services.search_service import SearchService
    service = SearchService(db)
    results = service.search_stories(q, limit)

    # Convert to StoryListItem
    return [
        StoryListItem(
            story_id=str(story.id),
            theme=story.theme,
            story_text=story.story_text[:200] + "...", # Preview
            image_url=story.image_url or "",
            created_at=str(story.created_at),
            story_type=story.story_type,
            is_favorite=story.is_favorite
        ) for story in results
    ]


@router.get("/user/statistics")
async def get_user_statistics():
    """
    Kullanıcı istatistiklerini getirir.
    """
    try:
        stats = user_profile_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistikler yüklenirken hata oluştu: {str(e)}")


class DialogueRequest(BaseModel):
    character_ids: List[str]
    context: str
    dialogue_type: str = "conversation"
    position: str = "middle"  # beginning, middle, end


@router.post("/stories/{story_id}/add-dialogue")
async def add_dialogue_to_story(story_id: str, request: DialogueRequest):
    """
    Hikâyeye diyalog ekler.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        # Karakterleri getir
        characters = []
        for char_id in request.character_ids:
            character = character_service.get_character(char_id)
            if character:
                characters.append(character)
        
        if len(characters) < 2:
            raise HTTPException(status_code=400, detail="En az 2 karakter gerekli")
        
        # Diyalog üret
        dialogues = await dialogue_service.generate_dialogue(
            characters,
            request.context or story.get('story_text', ''),
            request.dialogue_type,
            story.get('language', 'tr')
        )
        
        # Hikâyeye diyalog ekle
        updated_story_text = await dialogue_service.add_dialogue_to_story(
            story.get('story_text', ''),
            dialogues,
            request.position
        )
        
        # Hikâyeyi güncelle
        story['story_text'] = updated_story_text
        story['dialogues'] = story.get('dialogues', []) + dialogues
        story['updated_at'] = datetime.now().isoformat()
        
        updated_story = story_storage.save_story(story)
        
        return {
            "story_id": story_id,
            "dialogues": dialogues,
            "updated_story_text": updated_story_text,
            "story": updated_story
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diyalog eklenirken hata oluştu: {str(e)}")


class GenerateWithDialogueRequest(BaseModel):
    theme: str
    character_ids: List[str]
    language: str = "tr"
    story_type: str = "masal"
    dialogue_type: str = "conversation"
    save: bool = True


@router.post("/stories/generate-with-dialogue", response_model=StoryResponse)
async def generate_story_with_dialogue(request: GenerateWithDialogueRequest, background_tasks: BackgroundTasks):
    """
    Diyaloglu hikâye üretir.
    """
    try:
        story_id = str(uuid.uuid4())
        
        # Karakterleri getir
        characters = []
        for char_id in request.character_ids:
            character = character_service.get_character(char_id)
            if character:
                characters.append(character)
        
        if len(characters) < 2:
            raise HTTPException(status_code=400, detail="En az 2 karakter gerekli")
        
        # Hikâye metni üret
        story_text = await story_service.generate_story(
            request.theme,
            request.language,
            request.story_type
        )
        
        # Diyalog üret
        dialogues = await dialogue_service.generate_dialogue(
            characters,
            story_text,
            request.dialogue_type,
            request.language
        )
        
        # Hikâyeye diyalog ekle
        story_with_dialogue = await dialogue_service.add_dialogue_to_story(
            story_text,
            dialogues,
            "middle"
        )
        
        # Görsel üret
        image_url = await image_service.generate_image(
            story_with_dialogue,
            request.theme,
            image_style="fantasy",
            image_size="1024x1024"
        )
        
        # Ses üret
        audio_url = await tts_service.generate_speech(
            story_with_dialogue,
            request.language,
            story_id,
            audio_speed=1.0,
            audio_slow=False
        )
        
        created_at = datetime.now().isoformat()
        
        story_data = {
            'story_id': story_id,
            'story_text': story_with_dialogue,
            'image_url': image_url,
            'audio_url': audio_url,
            'theme': request.theme,
            'language': request.language,
            'story_type': request.story_type,
            'dialogues': dialogues,
            'character_ids': request.character_ids,
            'created_at': created_at,
        }
        
        if request.save:
            saved_story = story_storage.save_story(story_data)
            story_data['is_favorite'] = saved_story.get('is_favorite', False)
        
        background_tasks.add_task(cleanup_files, story_id)
        
        return StoryResponse(
            story_id=story_id,
            story_text=story_with_dialogue,
            image_url=image_url,
            audio_url=audio_url,
            created_at=created_at,
            theme=request.theme,
            language=request.language,
            story_type=request.story_type,
            is_favorite=story_data.get('is_favorite', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diyaloglu hikâye üretilirken hata oluştu: {str(e)}")


class OutlineRequest(BaseModel):
    theme: str
    language: str = "tr"
    story_type: str = "masal"
    include_characters: bool = True


@router.post("/stories/generate-outline")
async def generate_story_outline(request: OutlineRequest):
    """
    Tema için hikâye özeti/planı oluşturur.
    """
    try:
        outline = await story_outline_service.generate_outline(
            request.theme,
            request.language,
            request.story_type,
            request.include_characters
        )
        return outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye planı oluşturulurken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/outline")
async def get_story_outline(story_id: str):
    """
    Hikâye özetini getirir (eğer kaydedilmişse).
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        # Eğer outline kaydedilmişse döndür
        if story.get('outline'):
            return story.get('outline')
        
        # Yoksa yeni outline oluştur
        outline = await story_outline_service.generate_outline(
            story.get('theme', ''),
            story.get('language', 'tr'),
            story.get('story_type', 'masal'),
            True
        )
        
        # Outline'ı hikâyeye kaydet
        story['outline'] = outline
        story_storage.save_story(story)
        
        return outline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye planı yüklenirken hata oluştu: {str(e)}")


class PlotTwistRequest(BaseModel):
    position: str = "end"  # beginning, middle, end


@router.post("/stories/{story_id}/add-plot-twist")
async def add_plot_twist(story_id: str, request: PlotTwistRequest):
    """
    Hikâyeye plot twist ekler.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        # Plot twist üret
        plot_twist_text = await story_service.generate_plot_twist(
            story.get('story_text', ''),
            story.get('language', 'tr')
        )
        
        # Hikâyeyi güncelle
        story['story_text'] = plot_twist_text
        story['has_plot_twist'] = True
        story['updated_at'] = datetime.now().isoformat()
        
        # Görseli yeniden üret (plot twist'e uygun)
        story['image_url'] = await image_service.generate_image(
            plot_twist_text,
            story.get('theme', ''),
            image_style=story.get('image_style', 'fantasy'),
            image_size=story.get('image_size', '1024x1024')
        )
        
        # Sesi yeniden üret
        story['audio_url'] = await tts_service.generate_speech(
            plot_twist_text,
            story.get('language', 'tr'),
            story_id,
            audio_speed=story.get('audio_speed', 1.0),
            audio_slow=story.get('audio_slow', False)
        )
        
        updated_story = story_storage.save_story(story)
        
        return {
            "message": "Plot twist eklendi",
            "story": updated_story
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plot twist eklenirken hata oluştu: {str(e)}")


class AlternativeEndingRequest(BaseModel):
    ending_type: str = "surprise"  # surprise, happy, sad, open


class ContinueStoryRequest(BaseModel):
    continuation_length: str = "medium"  # short, medium, long


@router.post("/stories/{story_id}/generate-alternative-ending")
async def generate_alternative_ending(story_id: str, request: AlternativeEndingRequest):
    """
    Hikâye için alternatif son üretir.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        # Alternatif son üret
        alternative_ending = await story_service.generate_alternative_ending(
            story.get('story_text', ''),
            request.ending_type,
            story.get('language', 'tr')
        )
        
        # Alternatif sonları kaydet
        if 'alternative_endings' not in story:
            story['alternative_endings'] = []
        
        story['alternative_endings'].append({
            'ending_type': request.ending_type,
            'text': alternative_ending,
            'created_at': datetime.now().isoformat(),
        })
        
        story['updated_at'] = datetime.now().isoformat()
        updated_story = story_storage.save_story(story)
        
        return {
            "message": "Alternatif son oluşturuldu",
            "ending": alternative_ending,
            "ending_type": request.ending_type,
            "story": updated_story
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alternatif son oluşturulurken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/continue")
async def continue_story(story_id: str, request: ContinueStoryRequest):
    """
    Hikâyeyi devam ettirir.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        # Hikâyeyi devam ettir
        continued_story_text = await story_service.continue_story(
            story.get('story_text', ''),
            request.continuation_length,
            story.get('language', 'tr')
        )
        
        # Hikâyeyi güncelle
        story['story_text'] = continued_story_text
        story['is_continued'] = True
        story['updated_at'] = datetime.now().isoformat()
        
        # Görseli yeniden üret
        story['image_url'] = await image_service.generate_image(
            continued_story_text,
            story.get('theme', ''),
            image_style=story.get('image_style', 'fantasy'),
            image_size=story.get('image_size', '1024x1024')
        )
        
        # Sesi yeniden üret
        story['audio_url'] = await tts_service.generate_speech(
            continued_story_text,
            story.get('language', 'tr'),
            story_id,
            audio_speed=story.get('audio_speed', 1.0),
            audio_slow=story.get('audio_slow', False)
        )
        
        updated_story = story_storage.save_story(story)
        
        return StoryResponse(
            story_id=updated_story.get('story_id'),
            story_text=updated_story.get('story_text'),
            image_url=updated_story.get('image_url'),
            audio_url=updated_story.get('audio_url'),
            created_at=updated_story.get('created_at'),
            theme=updated_story.get('theme'),
            language=updated_story.get('language'),
            story_type=updated_story.get('story_type'),
            is_favorite=updated_story.get('is_favorite', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye devam ettirilirken hata oluştu: {str(e)}")


class CommentRequest(BaseModel):
    user_id: str
    text: str


@router.post("/stories/{story_id}/comments")
async def add_comment(story_id: str, request: CommentRequest):
    """
    Hikâyeye yorum ekler.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        comment = comment_service.add_comment(story_id, request.user_id, request.text)
        return comment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum eklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/comments")
async def get_story_comments(story_id: str):
    """
    Hikâyenin yorumlarını getirir.
    """
    try:
        comments = comment_service.get_story_comments(story_id)
        return {"comments": comments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorumlar yüklenirken hata oluştu: {str(e)}")


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, user_id: str = Query(...)):
    """
    Yorumu siler.
    """
    try:
        success = comment_service.delete_comment(comment_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı veya yetkiniz yok")
        return {"message": "Yorum silindi"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum silinirken hata oluştu: {str(e)}")


@router.post("/comments/{comment_id}/like")
async def like_comment(comment_id: str, user_id: str = Query(...)):
    """
    Yorumu beğenir veya beğeniyi kaldırır.
    """
    try:
        result = comment_service.like_comment(comment_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum beğenilirken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/like")
async def like_story(story_id: str, user_id: str = Query(...)):
    """
    Hikâyeyi beğenir veya beğeniyi kaldırır.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        result = like_service.like_story(story_id, user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye beğenilirken hata oluştu: {str(e)}")


@router.delete("/stories/{story_id}/like")
async def unlike_story(story_id: str, user_id: str = Query(...)):
    """
    Hikâye beğenisini kaldırır.
    """
    try:
        result = like_service.like_story(story_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beğeni kaldırılırken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/likes")
async def get_story_likes(story_id: str):
    """
    Hikâyenin beğeni sayısını getirir.
    """
    try:
        result = like_service.get_story_likes(story_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beğeniler yüklenirken hata oluştu: {str(e)}")


@router.put("/stories/{story_id}/visibility")
async def set_story_visibility(story_id: str, is_public: bool = Query(...)):
    """
    Hikâyenin görünürlüğünü ayarlar.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        story['is_public'] = is_public
        story['updated_at'] = datetime.now().isoformat()
        updated_story = story_storage.save_story(story)
        
        return {"message": "Görünürlük güncellendi", "is_public": is_public}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görünürlük güncellenirken hata oluştu: {str(e)}")


@router.get("/stories/public")
async def get_public_stories(skip: int = 0, limit: int = 20):
    """
    Herkese açık hikâyeleri getirir.
    """
    try:
        all_stories = story_storage.get_all_stories()
        public_stories = [s for s in all_stories if s.get('is_public', False)]
        # En yeni önce
        public_stories.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return {"stories": public_stories[skip:skip+limit], "total": len(public_stories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Public hikâyeler yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/trending")
async def get_trending_stories(limit: int = 10):
    """
    Trend hikâyeleri getirir (beğeni sayısına göre).
    """
    try:
        all_stories = story_storage.get_all_stories()
        public_stories = [s for s in all_stories if s.get('is_public', False)]
        
        # Her hikâye için beğeni sayısını al
        for story in public_stories:
            likes_data = like_service.get_story_likes(story.get('story_id'))
            story['like_count'] = likes_data.get('like_count', 0)
        
        # Beğeni sayısına göre sırala
        public_stories.sort(key=lambda x: x.get('like_count', 0), reverse=True)
        
        return {"stories": public_stories[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend hikâyeler yüklenirken hata oluştu: {str(e)}")


class AddCollaboratorRequest(BaseModel):
    user_id: str
    role: str = "writer"


class AddSectionRequest(BaseModel):
    user_id: str
    section_text: str
    section_index: Optional[int] = None


@router.post("/stories/{story_id}/collaborators")
async def add_collaborator(story_id: str, request: AddCollaboratorRequest):
    """
    Hikâyeye yazar ekler.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        result = collaboration_service.add_collaborator(story_id, request.user_id, request.role)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yazar eklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/collaborators")
async def get_collaborators(story_id: str):
    """
    Hikâyenin yazarlarını listeler.
    """
    try:
        collaborators = collaboration_service.get_collaborators(story_id)
        return {"collaborators": collaborators}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yazarlar yüklenirken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/add-section")
async def add_section(story_id: str, request: AddSectionRequest):
    """
    Hikâyeye bölüm ekler.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        section = collaboration_service.add_section(
            story_id,
            request.user_id,
            request.section_text,
            request.section_index
        )
        
        # Hikâye metnini güncelle
        story['story_text'] = f"{story.get('story_text', '')}\n\n{request.section_text}"
        story['updated_at'] = datetime.now().isoformat()
        story_storage.save_story(story)
        
        return section
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bölüm eklenirken hata oluştu: {str(e)}")


class CharacterVoiceRequest(BaseModel):
    character_id: str
    text: str
    language: str = "tr"
    emotion: Optional[str] = None
    audio_speed: float = 1.0


class DialogueVoiceRequest(BaseModel):
    dialogues: List[dict]
    language: str = "tr"
    audio_speed: float = 1.0


@router.post("/voice/character")
async def generate_character_voice(request: CharacterVoiceRequest):
    """
    Karakter için ses üretir.
    """
    try:
        audio_url = await voice_acting_service.generate_character_voice(
            request.text,
            request.character_id,
            request.language,
            request.emotion,
            request.audio_speed
        )
        return {"audio_url": audio_url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses üretilirken hata oluştu: {str(e)}")


@router.post("/voice/dialogue")
async def generate_dialogue_voices(request: DialogueVoiceRequest):
    """
    Diyaloglar için karakter bazlı sesler üretir.
    """
    try:
        dialogues_with_voices = await voice_acting_service.generate_dialogue_with_voices(
            request.dialogues,
            request.language,
            request.audio_speed
        )
        return {"dialogues": dialogues_with_voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diyalog sesleri üretilirken hata oluştu: {str(e)}")


@router.get("/voice/options")
async def get_voice_options():
    """
    Kullanılabilir ses seçeneklerini getirir.
    """
    try:
        voices = voice_acting_service.get_voice_options()
        emotions = voice_acting_service.get_emotion_options()
        return {"voices": voices, "emotions": emotions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses seçenekleri yüklenirken hata oluştu: {str(e)}")


class AddSoundEffectRequest(BaseModel):
    effect_type: str
    effect_name: str
    position: float = 0.0
    volume: float = 0.5
    fade_in: float = 0.0
    fade_out: float = 0.0


class AddMultipleSoundEffectsRequest(BaseModel):
    effects: List[dict]


@router.post("/stories/{story_id}/add-sound-effect")
async def add_sound_effect_to_story(story_id: str, request: AddSoundEffectRequest):
    """
    Hikâyeye ses efekti ekler.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        if not story.get('audio_url'):
            raise HTTPException(status_code=400, detail="Hikâyenin ses dosyası bulunamadı")
        
        # Ses dosyası yolunu al
        audio_path = os.path.join(
            settings.STORAGE_PATH,
            story['audio_url'].replace('/storage/audio/', 'audio/')
        )
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Ses dosyası bulunamadı")
        
        # Ses efektini ekle
        new_audio_url = await sound_effect_service.add_sound_effect_to_audio(
            audio_path,
            request.effect_type,
            request.effect_name,
            request.position,
            request.volume,
            request.fade_in,
            request.fade_out
        )
        
        # Hikâyeyi güncelle
        story['audio_url'] = new_audio_url
        story['updated_at'] = datetime.now().isoformat()
        story_storage.save_story(story)
        
        return {"message": "Ses efekti eklendi", "audio_url": new_audio_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses efekti eklenirken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/add-multiple-sound-effects")
async def add_multiple_sound_effects_to_story(story_id: str, request: AddMultipleSoundEffectsRequest):
    """
    Hikâyeye birden fazla ses efekti ekler.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        if not story.get('audio_url'):
            raise HTTPException(status_code=400, detail="Hikâyenin ses dosyası bulunamadı")
        
        # Ses dosyası yolunu al
        audio_path = os.path.join(
            settings.STORAGE_PATH,
            story['audio_url'].replace('/storage/audio/', 'audio/')
        )
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Ses dosyası bulunamadı")
        
        # Ses efektlerini ekle
        new_audio_url = await sound_effect_service.add_multiple_sound_effects(
            audio_path,
            request.effects
        )
        
        # Hikâyeyi güncelle
        story['audio_url'] = new_audio_url
        story['updated_at'] = datetime.now().isoformat()
        story_storage.save_story(story)
        
        return {"message": "Ses efektleri eklendi", "audio_url": new_audio_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses efektleri eklenirken hata oluştu: {str(e)}")


@router.get("/sound-effects/available")
async def get_available_sound_effects():
    """
    Kullanılabilir ses efektlerini getirir.
    """
    try:
        effects = sound_effect_service.get_available_effects()
        return {"effects": effects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses efektleri yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/sound-effect-suggestions")
async def get_sound_effect_suggestions(story_id: str):
    """
    Hikâye için ses efekti önerileri getirir.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        suggestions = sound_effect_service.get_effect_suggestions(
            story.get('story_text', ''),
            story.get('theme', '')
        )
        
        return {"suggestions": suggestions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Öneriler yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/share")
async def get_share_data(story_id: str):
    """
    Hikâye paylaşım verilerini getirir (metin, görsel URL, vb.)
    """
    story = story_storage.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    
    # Paylaşım için formatlanmış veri
    story_preview = story.get('story_text', '')
    if len(story_preview) > 200:
        story_preview = story_preview[:200] + "..."
    
    share_text = f"🎭 {story.get('theme', 'Hikâye')}\n\n{story_preview}\n\n#MasalFabrikasıAI"
    
    # Paylaşım URL'i (production'da gerçek URL olmalı)
    base_url = f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}"
    if settings.BACKEND_HOST == "0.0.0.0":
        base_url = "http://localhost:8000"  # Development için
    
    share_url = f"{base_url}/stories/{story_id}"
    
    # Görsel URL'ini tam yap

class StoryEditRequest(BaseModel):
    story_text: Optional[str] = None
    regenerate_image: bool = False
    regenerate_audio: bool = False
    new_story_type: Optional[str] = None
    image_style: Optional[str] = None
    image_size: Optional[str] = None
    audio_speed: Optional[float] = None
    audio_slow: Optional[bool] = None
    voice: Optional[str] = None
    emotion: Optional[str] = None


@router.put("/stories/{story_id}/edit", response_model=StoryResponse)
async def edit_story(story_id: str, request: StoryEditRequest):
    """
    Hikâyeyi düzenler veya yeniden üretir.
    """
    try:
        if request.new_story_type:
            # Hikâyeyi farklı türde yeniden yaz
            updated_story = await story_editor.regenerate_story_type(
                story_id,
                request.new_story_type
            )
        elif request.story_text:
            # Metni düzenle
            updated_story = await story_editor.update_story_text(
                story_id,
                request.story_text,
                regenerate_image=request.regenerate_image,
                regenerate_audio=request.regenerate_audio,
                voice=request.voice,
                emotion=request.emotion
            )
        elif request.regenerate_image:
            # Sadece görseli yeniden üret
            updated_story = await story_editor.regenerate_image(
                story_id,
                image_style=request.image_style,
                image_size=request.image_size
            )
        elif request.regenerate_audio:
            # Sadece sesi yeniden üret
            updated_story = await story_editor.regenerate_audio(
                story_id,
                audio_speed=request.audio_speed,
                audio_slow=request.audio_slow
            )
        else:
            raise HTTPException(status_code=400, detail="En az bir düzenleme parametresi gerekli")
        
        return StoryResponse(
            story_id=updated_story.get('story_id'),
            story_text=updated_story.get('story_text'),
            image_url=updated_story.get('image_url'),
            audio_url=updated_story.get('audio_url'),
            created_at=updated_story.get('created_at'),
            theme=updated_story.get('theme'),
            language=updated_story.get('language'),
            story_type=updated_story.get('story_type'),
            is_favorite=updated_story.get('is_favorite', False)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye düzenlenirken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/regenerate-image")
async def regenerate_image_only(story_id: str, image_style: Optional[str] = None, image_size: Optional[str] = None):
    """
    Sadece görseli yeniden üretir.
    """
    try:
        updated_story = await story_editor.regenerate_image(
            story_id,
            image_style=image_style,
            image_size=image_size
        )
        return {"message": "Görsel yeniden üretildi", "image_url": updated_story.get('image_url')}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görsel yeniden üretilirken hata oluştu: {str(e)}")


class RegenerateAudioRequest(BaseModel):
    audio_speed: Optional[float] = None
    audio_slow: Optional[bool] = None
    voice: Optional[str] = None
    emotion: Optional[str] = None


@router.post("/stories/{story_id}/regenerate-audio")
async def regenerate_audio_only(
    story_id: str,
    request: RegenerateAudioRequest
):
    """
    Sadece sesi yeniden üretir.
    """
    try:
        updated_story = await story_editor.regenerate_audio(
            story_id,
            audio_speed=request.audio_speed,
            audio_slow=request.audio_slow,
            voice=request.voice,
            emotion=request.emotion
        )
        return {"message": "Ses yeniden üretildi", "audio_url": updated_story.get('audio_url')}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses yeniden üretilirken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/regenerate-type")
async def regenerate_story_type(story_id: str, new_story_type: str):
    """
    Hikâyeyi farklı türde yeniden yazar.
    """
    try:
        updated_story = await story_editor.regenerate_story_type(
            story_id,
            new_story_type
        )
        return StoryResponse(
            story_id=updated_story.get('story_id'),
            story_text=updated_story.get('story_text'),
            image_url=updated_story.get('image_url'),
            audio_url=updated_story.get('audio_url'),
            created_at=updated_story.get('created_at'),
            theme=updated_story.get('theme'),
            language=updated_story.get('language'),
            story_type=updated_story.get('story_type'),
            is_favorite=updated_story.get('is_favorite', False)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye türü değiştirilirken hata oluştu: {str(e)}")


class MultiImageRequest(BaseModel):
    story_id: str
    mode: str = "paragraph"  # "paragraph", "sentence", "scene"
    image_style: str = "fantasy"
    image_size: str = "1024x1024"
    max_images: int = 5


@router.post("/stories/{story_id}/multi-images")
async def generate_multi_images(story_id: str, request: MultiImageRequest):
    """
    Hikâye için birden fazla görsel üretir.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        image_urls = await multi_image_service.generate_images_for_story(
            story.get('story_text', ''),
            story.get('theme', ''),
            mode=request.mode,
            image_style=request.image_style,
            image_size=request.image_size,
            max_images=request.max_images
        )
        
        # Görselleri hikâyeye kaydet (opsiyonel - yeni bir alan olarak)
        story['multi_images'] = image_urls
        story_storage.save_story(story)
        
        return {
            "story_id": story_id,
            "images": image_urls,
            "count": len(image_urls),
            "mode": request.mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çoklu görsel üretilirken hata oluştu: {str(e)}")


async def cleanup_files(story_id: str):
    """
    Geçici dosyaları temizler (opsiyonel - belirli bir süre sonra)
    """
    # Bu fonksiyon daha sonra geliştirilebilir
    pass


# Hikâye Karşılaştırma Endpoint'leri
@router.get("/stories/{story_id_1}/compare/{story_id_2}")
async def compare_stories(story_id_1: str, story_id_2: str):
    """
    İki hikâyeyi karşılaştırır.
    """
    try:
        comparison = await story_comparison_service.compare_stories(story_id_1, story_id_2)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Karşılaştırma yapılırken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/similar-stories")
async def find_similar_stories(story_id: str, threshold: float = 0.3, limit: int = 5):
    """
    Benzer hikâyeler bulur.
    """
    try:
        similar = await story_comparison_service.find_similar_stories(story_id, threshold, limit)
        return {"similar_stories": similar}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benzer hikâyeler bulunurken hata oluştu: {str(e)}")


# Topluluk Özellikleri Endpoint'leri
class CreateContestRequest(BaseModel):
    title: str
    description: str
    theme: str
    start_date: str
    end_date: str


@router.post("/contests")
async def create_contest(request: CreateContestRequest, user_id: str):
    """
    Yeni bir yarışma oluşturur.
    """
    try:
        contest = community_service.create_contest(
            request.title,
            request.description,
            request.theme,
            request.start_date,
            request.end_date,
            user_id
        )
        return contest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yarışma oluşturulurken hata oluştu: {str(e)}")


@router.get("/contests/active")
async def get_active_contests():
    """
    Aktif yarışmaları getirir.
    """
    try:
        contests = community_service.get_active_contests()
        return {"contests": contests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yarışmalar yüklenirken hata oluştu: {str(e)}")


@router.post("/contests/{contest_id}/submit")
async def submit_to_contest(contest_id: str, story_id: str, user_id: str):
    """
    Yarışmaya hikâye gönderir.
    """
    try:
        submission = community_service.submit_to_contest(contest_id, story_id, user_id)
        return submission
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gönderim yapılırken hata oluştu: {str(e)}")


@router.get("/community/themes")
async def get_community_themes():
    """
    Topluluk temalarını getirir.
    """
    try:
        themes = community_service.get_community_themes()
        return {"themes": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Temalar yüklenirken hata oluştu: {str(e)}")


@router.get("/community/themes/weekly")
async def get_weekly_themes():
    """
    Haftalık popüler temaları getirir.
    """
    try:
        themes = community_service.get_weekly_themes()
        return {"themes": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Temalar yüklenirken hata oluştu: {str(e)}")


# Gelişmiş Arama Endpoint'leri
@router.get("/search")
async def ai_search(query: str, language: Optional[str] = None, limit: int = 10):
    """
    AI destekli arama yapar.
    """
    try:
        results = await search_service.ai_search(query, language, limit)
        return {"results": results, "query": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arama yapılırken hata oluştu: {str(e)}")


@router.get("/search/semantic")
async def semantic_search(query: str, limit: int = 10):
    """
    Anlamsal arama yapar.
    """
    try:
        results = await search_service.semantic_search(query, limit)
        return {"results": results, "query": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arama yapılırken hata oluştu: {str(e)}")


# Analytics Dashboard Endpoint'leri
@router.get("/analytics/dashboard")
async def get_dashboard_statistics(user_id: Optional[str] = None):
    """
    Dashboard istatistiklerini getirir.
    """
    try:
        stats = analytics_service.get_dashboard_statistics(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistikler yüklenirken hata oluştu: {str(e)}")


@router.get("/analytics/users/{user_id}")
async def get_user_analytics(user_id: str):
    """
    Kullanıcı analitiklerini getirir.
    """
    try:
        analytics = analytics_service.get_user_analytics(user_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analitikler yüklenirken hata oluştu: {str(e)}")


@router.get("/analytics/trending")
async def get_trending_analysis(days: int = 7):
    """
    Trend analizi yapar.
    """
    try:
        analysis = analytics_service.get_trending_analysis(days)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analizi yapılırken hata oluştu: {str(e)}")


# Hikâye Serileri Endpoint'leri
class CreateSeriesRequest(BaseModel):
    title: str
    description: Optional[str] = None


@router.post("/series")
async def create_series(request: CreateSeriesRequest, user_id: str):
    """
    Yeni bir hikâye serisi oluşturur.
    """
    try:
        series = story_series_service.create_series(
            request.title,
            request.description,
            user_id
        )
        return series
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seri oluşturulurken hata oluştu: {str(e)}")


@router.post("/series/{series_id}/add-story")
async def add_story_to_series(series_id: str, story_id: str, chapter_number: Optional[int] = None):
    """
    Seriye hikâye ekler.
    """
    try:
        series = story_series_service.add_story_to_series(series_id, story_id, chapter_number)
        return series
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye eklenirken hata oluştu: {str(e)}")


@router.get("/series/{series_id}")
async def get_series(series_id: str):
    """
    Seriyi getirir.
    """
    try:
        series = story_series_service.get_series(series_id)
        if not series:
            raise HTTPException(status_code=404, detail="Seri bulunamadı")
        return series
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seri yüklenirken hata oluştu: {str(e)}")


@router.get("/series/{series_id}/stories")
async def get_series_stories(series_id: str):
    """
    Serideki hikâyeleri getirir.
    """
    try:
        stories = story_series_service.get_series_stories(series_id)
        return {"stories": stories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâyeler yüklenirken hata oluştu: {str(e)}")


# Hikâye İyileştirme Endpoint'leri
@router.post("/stories/{story_id}/analyze-quality")
async def analyze_story_quality(story_id: str):
    """
    Hikâye kalitesini analiz eder ve iyileştirme önerileri sunar.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        analysis = await story_improvement_service.analyze_story_quality(
            story.get('story_text', ''),
            story.get('language', 'tr')
        )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz yapılırken hata oluştu: {str(e)}")


class ImproveStoryRequest(BaseModel):
    improvement_type: str  # flow, vocabulary, structure, description, dialogue


@router.post("/stories/{story_id}/improve")
async def improve_story(story_id: str, request: ImproveStoryRequest):
    """
    Hikâyenin iyileştirilmiş versiyonunu üretir.
    """
    try:
        story = story_storage.get_story(story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
        
        improved_text = await story_improvement_service.get_improved_version(
            story.get('story_text', ''),
            request.improvement_type,
            story.get('language', 'tr')
        )
        
        return {
            "original_text": story.get('story_text', ''),
            "improved_text": improved_text,
            "improvement_type": request.improvement_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye iyileştirilirken hata oluştu: {str(e)}")


# Ebeveyn Kontrolü Endpoint'leri
class ParentalControlRequest(BaseModel):
    child_age: int
    allowed_themes: Optional[List[str]] = None
    blocked_themes: Optional[List[str]] = None
    max_story_length: Optional[int] = None
    require_approval: bool = False


@router.post("/users/{user_id}/parental-controls")
async def set_parental_controls(user_id: str, request: ParentalControlRequest):
    """
    Ebeveyn kontrolü ayarlarını yapar.
    """
    try:
        controls = parental_control_service.set_parental_controls(
            user_id,
            request.child_age,
            request.allowed_themes,
            request.blocked_themes,
            request.max_story_length,
            request.require_approval
        )
        return controls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ayarlar kaydedilirken hata oluştu: {str(e)}")


@router.get("/users/{user_id}/parental-controls")
async def get_parental_controls(user_id: str):
    """
    Ebeveyn kontrolü ayarlarını getirir.
    """
    try:
        controls = parental_control_service.get_parental_controls(user_id)
        if not controls:
            return {"controls_set": False}
        return controls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ayarlar yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/check-appropriateness")
async def check_story_appropriateness(story_id: str, user_id: str):
    """
    Hikâyenin çocuk için uygun olup olmadığını kontrol eder.
    """
    try:
        result = await parental_control_service.check_story_appropriateness(story_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kontrol yapılırken hata oluştu: {str(e)}")


@router.get("/users/{user_id}/parental-dashboard")
async def get_parental_dashboard(user_id: str):
    """
    Ebeveyn dashboard'unu getirir.
    """
    try:
        dashboard = parental_control_service.get_parent_dashboard(user_id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard yüklenirken hata oluştu: {str(e)}")


# Ses Kayıt Endpoint'leri
@router.post("/recordings")
async def save_recording(
    user_id: str,
    recording_name: str,
    character_id: Optional[str] = None,
    story_id: Optional[str] = None,
    audio_data: bytes = None
):
    """
    Ses kaydını kaydeder.
    """
    try:
        recording = audio_recording_service.save_recording(
            audio_data,
            user_id,
            recording_name,
            character_id,
            story_id
        )
        return recording
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kayıt kaydedilirken hata oluştu: {str(e)}")


@router.get("/users/{user_id}/recordings")
async def get_user_recordings(user_id: str):
    """
    Kullanıcının kayıtlarını getirir.
    """
    try:
        recordings = audio_recording_service.get_user_recordings(user_id)
        return {"recordings": recordings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kayıtlar yüklenirken hata oluştu: {str(e)}")


class EditRecordingRequest(BaseModel):
    trim_start: Optional[float] = None
    trim_end: Optional[float] = None
    volume_adjust: Optional[float] = None
    fade_in: Optional[float] = None
    fade_out: Optional[float] = None


@router.post("/recordings/{recording_id}/edit")
async def edit_recording(recording_id: str, request: EditRecordingRequest):
    """
    Ses kaydını düzenler.
    """
    try:
        edited = await audio_recording_service.edit_recording(
            recording_id,
            request.trim_start,
            request.trim_end,
            request.volume_adjust,
            request.fade_in,
            request.fade_out
        )
        return edited
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kayıt düzenlenirken hata oluştu: {str(e)}")


# Paylaşım Endpoint'leri
@router.get("/stories/{story_id}/qr-code")
async def generate_qr_code(story_id: str, base_url: str = "https://masalfabrikasi.com"):
    """
    Hikâye için QR kod oluşturur.
    """
    try:
        qr_data = sharing_service.generate_qr_code(story_id, base_url)
        return qr_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR kod oluşturulurken hata oluştu: {str(e)}")


class CreateShareLinkRequest(BaseModel):
    custom_slug: Optional[str] = None
    expires_in_days: Optional[int] = None


@router.post("/stories/{story_id}/share-link")
async def create_share_link(story_id: str, request: CreateShareLinkRequest):
    """
    Özel paylaşım linki oluşturur.
    """
    try:
        link = sharing_service.create_share_link(
            story_id,
            request.custom_slug,
            request.expires_in_days
        )
        return link
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Link oluşturulurken hata oluştu: {str(e)}")


@router.get("/share/{slug}")
async def get_story_from_share_link(slug: str):
    """
    Paylaşım linkinden hikâyeyi getirir.
    """
    try:
        story = sharing_service.get_story_from_share_link(slug)
        if not story:
            raise HTTPException(status_code=404, detail="Link geçersiz veya süresi dolmuş")
        return story
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hikâye yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/embed-code")
async def get_embed_code(story_id: str, width: int = 600, height: int = 400):
    """
    Hikâye için embed kodu oluşturur.
    """
    try:
        embed_code = sharing_service.generate_embed_code(story_id, width, height)
        return {"embed_code": embed_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embed kodu oluşturulurken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/social-preview")
async def get_social_media_preview(story_id: str):
    """
    Sosyal medya paylaşımı için önizleme verileri oluşturur.
    """
    try:
        preview = sharing_service.get_social_media_preview(story_id)
        return preview
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Önizleme oluşturulurken hata oluştu: {str(e)}")


# E-kitap Endpoint'leri
@router.post("/stories/{story_id}/export/epub")
async def export_story_epub(story_id: str, title: Optional[str] = None, author: Optional[str] = None):
    """
    Hikâyeyi EPUB formatında oluşturur.
    """
    try:
        ebook = ebook_service.create_epub(story_id, title, author)
        return ebook
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EPUB oluşturulurken hata oluştu: {str(e)}")


@router.post("/stories/{story_id}/export/mobi")
async def export_story_mobi(story_id: str, title: Optional[str] = None, author: Optional[str] = None):
    """
    Hikâyeyi MOBI formatında oluşturur.
    """
    try:
        ebook = ebook_service.create_mobi(story_id, title, author)
        return ebook
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MOBI oluşturulurken hata oluştu: {str(e)}")


class CreateCollectionEbookRequest(BaseModel):
    story_ids: List[str]
    collection_title: str
    author: Optional[str] = None


@router.post("/export/collection-epub")
async def export_collection_epub(request: CreateCollectionEbookRequest):
    """
    Birden fazla hikâyeyi bir e-kitap olarak birleştirir.
    """
    try:
        ebook = ebook_service.create_collection_ebook(
            request.story_ids,
            request.collection_title,
            request.author
        )
        return ebook
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon e-kitabı oluşturulurken hata oluştu: {str(e)}")


# Performans Metrikleri Endpoint'leri
@router.post("/stories/{story_id}/record-view")
async def record_story_view(story_id: str, user_id: Optional[str] = None, duration: Optional[float] = None):
    """
    Hikâye görüntüleme kaydı yapar.
    """
    try:
        performance_metrics_service.record_story_view(story_id, user_id, duration)
        return {"message": "Görüntüleme kaydedildi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kayıt yapılırken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/metrics")
async def get_story_metrics(story_id: str):
    """
    Hikâye performans metriklerini getirir.
    """
    try:
        metrics = performance_metrics_service.get_story_metrics(story_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrikler yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/reading-progress/{user_id}")
async def get_reading_progress(story_id: str, user_id: str):
    """
    Kullanıcının hikâye okuma ilerlemesini getirir.
    """
    try:
        progress = performance_metrics_service.get_reading_progress(story_id, user_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İlerleme yüklenirken hata oluştu: {str(e)}")


@router.get("/stories/trending")
async def get_trending_stories(days: int = 7, limit: int = 10):
    """
    Trend hikâyeleri getirir.
    """
    try:
        trending = performance_metrics_service.get_trending_stories(days, limit)
        return {"trending_stories": trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend hikâyeler yüklenirken hata oluştu: {str(e)}")
