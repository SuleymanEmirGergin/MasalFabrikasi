"""
Sample Unit Tests for StoryService
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.story_service import StoryService


@pytest.mark.unit
class TestStoryService:
    """Unit tests for StoryService"""
    
    def test_create_prompt_turkish(self):
        """Test Turkish prompt creation"""
        service = StoryService()
        
        prompt = service._create_prompt(
            theme="Uzayda kaybolmuş bir kedi",
            language="tr",
            story_type="masal"
        )
        
        assert "masal tarzında" in prompt
        assert "Uzayda kaybolmuş bir kedi" in prompt
        assert "Tema:" in prompt
    
    def test_create_prompt_english(self):
        """Test English prompt creation"""
        service = StoryService()
        
        prompt = service._create_prompt(
            theme="A lost cat in space",
            language="en",
            story_type="masal"
        )
        
        assert "fairy tale style" in prompt
        assert "A lost cat in space" in prompt
        assert "Theme:" in prompt
    
    def test_enhance_bedtime_theme(self):
        """Test bedtime theme enhancement"""
        service = StoryService()
        
        enhanced = service._enhance_bedtime_theme(
            theme="Yıldızlar",
            language="tr",
            age_group="3-6"
        )
        
        assert "Yıldızlar" in enhanced
        assert "sakinleştirici" in enhanced
        assert "rahatlatıcı" in enhanced


@pytest.mark.unit
@pytest.mark.asyncio
class TestStoryServiceWiro:
    """Tests for generate_story Wiro path (mocked)."""

    @patch("app.services.story_service.settings")
    @patch("app.services.story_service.wiro_client")
    async def test_generate_story_uses_wiro_for_gpt_oss(self, mock_wiro, mock_settings):
        mock_settings.GPT_MODEL = "openai/gpt-oss-20b"
        mock_settings.GPT_API_KEY = "key"
        mock_settings.GPT_BASE_URL = "https://api.wiro.ai/v1"
        mock_settings.GEMINI_API_KEY = ""
        mock_wiro.run_and_wait = AsyncMock(
            return_value={
                "detail": {
                    "tasklist": [{"debugoutput": "Mock story text from gpt-oss"}]
                }
            }
        )
        service = StoryService()
        result = await service.generate_story(theme="Test theme", language="tr")
        assert result == "Mock story text from gpt-oss"
        mock_wiro.run_and_wait.assert_called_once()
        call_kw = mock_wiro.run_and_wait.call_args
        assert call_kw[0][0] == "openai"
        assert call_kw[0][1] == "gpt-oss-20b"
        assert call_kw[1]["is_json"] is True

    @patch("app.services.story_service.settings")
    @patch("app.services.story_service.wiro_client")
    async def test_generate_story_uses_wiro_for_gpt_5_nano(self, mock_wiro, mock_settings):
        mock_settings.GPT_MODEL = "openai/gpt-5-nano"
        mock_settings.GPT_API_KEY = "key"
        mock_settings.GPT_BASE_URL = "https://api.wiro.ai/v1"
        mock_settings.GEMINI_API_KEY = ""
        mock_wiro.run_and_wait = AsyncMock(
            return_value={
                "detail": {
                    "tasklist": [{"debugoutput": "Mock story from gpt-5-nano"}]
                }
            }
        )
        service = StoryService()
        result = await service.generate_story(theme="Test", language="tr")
        assert result == "Mock story from gpt-5-nano"
        mock_wiro.run_and_wait.assert_called_once()
        call_kw = mock_wiro.run_and_wait.call_args
        assert call_kw[0][0] == "openai"
        assert call_kw[0][1] == "gpt-5-nano"
        assert call_kw[1]["is_json"] is False
        inputs = call_kw[0][2]
        assert "prompt" in inputs
        assert inputs.get("reasoning") == "medium"
        assert inputs.get("verbosity") == "medium"
