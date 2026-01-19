import pytest
from app.celery_app import celery_app
from app.tasks.story_tasks import generate_full_story_task
from unittest.mock import patch, MagicMock, AsyncMock
import uuid
import asyncio

@pytest.fixture(scope="module")
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,
    }

def test_celery_task_registration():
    """Test that tasks are registered correctly."""
    # Check against the actual name used in @shared_task(name=...)
    assert "app.tasks.story_tasks.generate_full_story" in celery_app.tasks

@patch("app.tasks.story_tasks.JobRepository")
@patch("app.tasks.story_tasks.StoryRepository")
@patch("app.tasks.story_tasks.StoryService")
@patch("app.tasks.story_tasks.ImageService")
@patch("app.tasks.story_tasks.TTSService")
@patch("app.tasks.story_tasks.SearchService")
@patch("app.tasks.story_tasks.supabase_job_service")
@patch("app.tasks.story_tasks.socketio.RedisManager")
def test_generate_full_story_task_execution(
    mock_redis_manager, mock_supabase, mock_search, mock_tts, mock_image, mock_story, mock_story_repo, mock_job_repo
):
    """Test that the task executes (eagerly)."""
    # Setup mocks
    job_id = str(uuid.uuid4())
    mock_job = MagicMock()
    mock_job.input_data = {"theme": "test", "language": "tr"}
    mock_job.user_id = "user123"

    # Mock Repositories
    mock_job_repo_instance = mock_job_repo.return_value
    mock_job_repo_instance.update_job_status.return_value = mock_job

    mock_story_repo_instance = mock_story_repo.return_value
    mock_story_repo_instance.create_story.return_value = MagicMock(id="story123")

    # Mock Services (Async)
    mock_story_service_instance = mock_story.return_value
    # AsyncMock for awaitable methods
    mock_story_service_instance.generate_story = AsyncMock(return_value="Generated Story Content")

    mock_image_service_instance = mock_image.return_value
    mock_image_service_instance.generate_image = AsyncMock(return_value="http://image.url")

    mock_tts_service_instance = mock_tts.return_value
    mock_tts_service_instance.generate_speech = AsyncMock(return_value="http://audio.url")

    # Run task eagerly
    celery_app.conf.update(task_always_eager=True)

    # Execute
    # Since it's eager, .apply() executes locally
    result = generate_full_story_task.apply(args=[job_id])

    # Verify execution
    assert result.status == "SUCCESS"

    # Verify logic flow
    mock_job_repo_instance.update_job_status.assert_called()
    mock_story_service_instance.generate_story.assert_called()
    mock_image_service_instance.generate_image.assert_called()
    mock_tts_service_instance.generate_speech.assert_called()
