import asyncio
from celery import shared_task
from celery.utils.log import get_task_logger
from app.core.database import SessionLocal
from app.repositories.story_repository import StoryRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository
from app.models import JobStatus, JobType
from app.services.story_service import StoryService
from app.services.image_service import ImageService
from app.services.tts_service import TTSService
from app.services.search_service import SearchService
from app.services.supabase_job_service import supabase_job_service
import uuid

logger = get_task_logger(__name__)

# Initialize services
# Note: Services might need to be initialized inside tasks if they use db sessions or async loops differently
# But usually they are stateless or handle their own connections.

@shared_task(bind=True, name="app.tasks.story_tasks.generate_full_story", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def generate_full_story_task(self, job_id: str):
    """
    Orchestrates the full story generation process:
    1. Text Generation
    2. Image Generation
    3. Audio Generation
    4. Finalize
    """
    job_repo = JobRepository()
    story_repo = StoryRepository()
    
    # Initialize Socket.IO Redis Manager for emitting events from worker
    # Note: We use the synchronous RedisManager here because Celery task is sync wrapper
    import socketio
    socket_mgr = socketio.RedisManager('redis://localhost:6379/0', write_only=True)
    
    def emit_progress(job_id, percent, step, data=None):
        """Helper to emit progress to specific job room"""
        payload = {
            "job_id": str(job_id),
            "status": "RUNNING" if percent < 100 else "SUCCEEDED",
            "percent": percent,
            "message": step,
            "data": data
        }
        socket_mgr.emit('job_progress', payload, room=str(job_id))

    # Get or create event loop safely (fixes "RuntimeError: no running event loop")
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        # Update Job Status -> Running
        job = job_repo.update_job_status(
            uuid.UUID(job_id), 
            JobStatus.RUNNING, 
            celery_task_id=self.request.id,
            percent=0,
            error_message=None
        )
        
        # Sync with Supabase for Realtime Tracking
        supabase_job_service.upsert_job(
            job_id=job_id,
            user_id=str(job.user_id) if hasattr(job, 'user_id') else "anon",
            status="processing",
            progress=0,
            message="Başlatılıyor..."
        )
        
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        input_data = job.input_data
        user_id = job.user_id
        
        # --- Step 1: Text Generation ---
        job_repo.update_job_status(uuid.UUID(job_id), JobStatus.RUNNING, percent=10, step="Hikaye yazılıyor...")
        emit_progress(job_id, 10, "Hikaye yazılıyor...")
        supabase_job_service.update_progress(job_id, 10, "Hikaye yazılıyor...")
        
        story_service = StoryService()
        story_text = loop.run_until_complete(story_service.generate_story(
            theme=input_data.get('theme'),
            language=input_data.get('language', 'tr'),
            story_type=input_data.get('story_type', 'masal'),
            creativity=input_data.get('creativity', 0.8),
            pacing=input_data.get('pacing', 'medium'),
            perspective=input_data.get('perspective', 'third'),
            vocabulary=input_data.get('vocabulary', 'normal'),
            age_group=input_data.get('age_group', '3-6'),
            pedagogical_theme=input_data.get('pedagogical_theme')
        ))
        
        # Create partial story in DB
        story_id = uuid.uuid4()
        story_data = {
            'story_id': str(story_id),
            'theme': input_data.get('theme'),
            'story_text': story_text,
            'language': input_data.get('language', 'tr'),
            'story_type': input_data.get('story_type', 'masal'),
            # Placeholders
            'image_url': None,
            'audio_url': None
        }
        
        story = story_repo.create_story(story_data, user_id)
        
        # Link story to job
        # Link story to job
        job.story_id = story_id
        job_repo.update_job_status(uuid.UUID(job_id), JobStatus.RUNNING, percent=30, step="Görsel üretiliyor...")
        emit_progress(job_id, 30, "Görsel üretiliyor...", data={"story_text_preview": story_text[:100] + "..."})
        supabase_job_service.update_progress(job_id, 30, "Görsel üretiliyor...")
        
        # --- Step 2: Image Generation ---
        image_service = ImageService()
        image_url = loop.run_until_complete(image_service.generate_image(
            story_text=story_text,
            theme=input_data.get('theme'),
            image_style=input_data.get('image_style', 'fantasy'),
            image_size=input_data.get('image_size', '1024x1024')
        ))
        
        # Update story with image
        story_repo.update_story(story_id, {'image_url': image_url})
        job_repo.update_job_status(uuid.UUID(job_id), JobStatus.RUNNING, percent=60, step="Seslendiriliyor...")
        emit_progress(job_id, 60, "Seslendiriliyor...", data={"image_url": image_url})
        supabase_job_service.update_progress(job_id, 60, "Seslendirme yapılıyor...")
        
        # --- Step 3: Audio Generation ---
        tts_service = TTSService()
        audio_url = loop.run_until_complete(tts_service.generate_speech(
            text=story_text,
            language=input_data.get('language', 'tr'),
            story_id=str(story_id),
            audio_speed=input_data.get('audio_speed', 1.0),
            audio_slow=input_data.get('audio_slow', False)
        ))
        
        # Update story with audio
        story_repo.update_story(story_id, {'audio_url': audio_url})
        
        # --- Step 4: Semantic Embedding ---
        job_repo.update_job_status(uuid.UUID(job_id), JobStatus.RUNNING, percent=90, step="İndeksleme yapılıyor...")
        emit_progress(job_id, 90, "İndeksleme yapılıyor...")
        supabase_job_service.update_progress(job_id, 95, "Son dokunuşlar...")
        
        db = SessionLocal()
        try:
            search_service = SearchService(db)
            search_service.update_story_embedding(str(story_id))
        except Exception as e:
            logger.error(f"Embedding error: {e}")
        finally:
            db.close()
        
        # --- Finalize ---
        # User XP update or credit deduction could happen here
        
        # Complete Job
        result_data = {
            "story_id": str(story_id),
            "image_url": image_url,
            "audio_url": audio_url
        }
        
        job_repo.update_job_status(
            uuid.UUID(job_id), 
            JobStatus.SUCCEEDED, 
            result_data=result_data,
            percent=100,
            step="Tamamlandı"
        )
        emit_progress(job_id, 100, "Tamamlandı", data=result_data)
        supabase_job_service.update_progress(job_id, 100, "Tamamlandı", status="completed")
        
        logger.info(f"Job {job_id} completed successfully.")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job_repo.update_job_status(
            uuid.UUID(job_id), 
            JobStatus.FAILED, 
            error_message=str(e),
            step="Hata oluştu"
        )
        socket_mgr.emit('job_progress', 
            {"job_id": str(job_id), "status": "FAILED", "message": str(e)}, 
            room=str(job_id)
        )
        supabase_job_service.update_progress(job_id, 0, f"Hata: {str(e)}", status="failed")
        raise  # Re-raise for Celery retry mechanism
    finally:
        # Cleanup: Close database connections and event loop to prevent resource leaks
        try:
            job_repo.close()
            story_repo.close()
        except Exception as cleanup_error:
            logger.warning(f"Cleanup error for job {job_id}: {cleanup_error}")
        finally:
            loop.close()
