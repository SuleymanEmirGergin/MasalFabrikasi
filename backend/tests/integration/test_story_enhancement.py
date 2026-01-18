import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.story_enhancement_service import StoryEnhancementService
from app.models import Story

@pytest.mark.asyncio
async def test_process_enhancement_success():
    # Setup mocks
    mock_openai_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Enhanced Story Content"))]
    mock_openai_client.chat.completions.create.return_value = mock_response

    mock_session = AsyncMock()
    mock_story = Story(id="story-123", story_text="Original Content", meta_data={})

    # Mock DB execution to return the story
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_story
    mock_session.execute.return_value = mock_result

    # Mock get_db_context
    mock_db_context = AsyncMock()
    mock_db_context.__aenter__.return_value = mock_session
    mock_db_context.__aexit__.return_value = None

    with patch("app.services.story_enhancement_service.StoryEnhancementService._load_config", return_value={"joy": {"model": "gpt-4", "system_role": "sys", "prompt_template": "Joy {text}", "temperature": 0.7}}), \
         patch("app.services.story_enhancement_service.settings") as mock_settings, \
         patch("app.services.story_enhancement_service.AsyncOpenAI", return_value=mock_openai_client), \
         patch("app.services.story_enhancement_service.get_db_context", return_value=mock_db_context):

        service = StoryEnhancementService()
        # Override client because __init__ is called before we can patch the instance attribute easily if not careful,
        # but here we patched the class AsyncOpenAI, so service.client should be our mock.
        # Actually, let's just force set it to be sure.
        service.client = mock_openai_client

        result = await service.process_enhancement("story-123", "joy", "Original Content")

        # Verify OpenAI call
        mock_openai_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4"
        assert call_kwargs["messages"][1]["content"] == "Joy Original Content"

        # Verify DB Update
        # We expect session.execute to be called twice: once for select, once for update
        assert mock_session.execute.call_count == 2
        assert mock_session.commit.call_count == 1

        assert result["enhanced_text"] == "Enhanced Story Content"
        assert result["enhancement_type"] == "joy"

@pytest.mark.asyncio
async def test_process_enhancement_invalid_type():
    with patch("app.services.story_enhancement_service.StoryEnhancementService._load_config", return_value={}):
        service = StoryEnhancementService()
        with pytest.raises(ValueError, match="Enhancement type 'invalid' not supported"):
            await service.process_enhancement("story-123", "invalid", "text")
