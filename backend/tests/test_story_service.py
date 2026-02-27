"""
Sample Unit Tests for StoryService
"""
import pytest
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
