from typing import Optional
from datetime import datetime
from app.services.story_service import StoryService
from app.services.image_service import ImageService
from app.services.tts_service import TTSService
from app.services.story_storage import StoryStorage
from app.core.config import settings


class StoryEditor:
    def __init__(self):
        self.story_service = StoryService()
        self.image_service = ImageService()
        self.tts_service = TTSService()
        self.story_storage = StoryStorage()
    
    async def update_story_text(
        self, 
        story_id: str, 
        new_text: str,
        regenerate_image: bool = False,
        regenerate_audio: bool = True,
        voice: Optional[str] = None,
        emotion: Optional[str] = None
    ) -> dict:
        """
        Hikâye metnini günceller ve isteğe bağlı olarak görsel/ses yeniden üretir.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Metni güncelle
        story['story_text'] = new_text
        story['updated_at'] = datetime.now().isoformat()
        
        # Görseli yeniden üret (isteğe bağlı)
        if regenerate_image:
            story['image_url'] = await self.image_service.generate_image(
                new_text,
                story.get('theme', ''),
                image_style=story.get('image_style', 'fantasy'),
                image_size=story.get('image_size', '1024x1024')
            )
        
        # Sesi yeniden üret (isteğe bağlı)
        if regenerate_audio:
            voice = voice or story.get('voice', None)
            emotion = emotion or story.get('emotion', None)
            story['audio_url'] = await self.tts_service.generate_speech(
                new_text,
                story.get('language', 'tr'),
                story_id,
                audio_speed=story.get('audio_speed', 1.0),
                audio_slow=story.get('audio_slow', False),
                voice=voice,
                emotion=emotion
            )
            if voice:
                story['voice'] = voice
            if emotion:
                story['emotion'] = emotion
        
        # Güncellenmiş hikâyeyi kaydet
        updated_story = self.story_storage.save_story(story)
        return updated_story
    
    async def regenerate_image(
        self,
        story_id: str,
        image_style: Optional[str] = None,
        image_size: Optional[str] = None
    ) -> dict:
        """
        Sadece görseli yeniden üretir.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        image_style = image_style or story.get('image_style', 'fantasy')
        image_size = image_size or story.get('image_size', '1024x1024')
        
        # Yeni görsel üret
        new_image_url = await self.image_service.generate_image(
            story.get('story_text', ''),
            story.get('theme', ''),
            image_style=image_style,
            image_size=image_size
        )
        
        # Görseli güncelle
        story['image_url'] = new_image_url
        story['image_style'] = image_style
        story['image_size'] = image_size
        story['updated_at'] = datetime.now().isoformat()
        
        updated_story = self.story_storage.save_story(story)
        return updated_story
    
    async def regenerate_audio(
        self,
        story_id: str,
        audio_speed: Optional[float] = None,
        audio_slow: Optional[bool] = None,
        voice: Optional[str] = None,
        emotion: Optional[str] = None
    ) -> dict:
        """
        Sadece sesi yeniden üretir.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        audio_speed = audio_speed if audio_speed is not None else story.get('audio_speed', 1.0)
        audio_slow = audio_slow if audio_slow is not None else story.get('audio_slow', False)
        voice = voice or story.get('voice', None)
        emotion = emotion or story.get('emotion', None)
        
        # Yeni ses üret
        new_audio_url = await self.tts_service.generate_speech(
            story.get('story_text', ''),
            story.get('language', 'tr'),
            story_id,
            audio_speed=audio_speed,
            audio_slow=audio_slow,
            voice=voice,
            emotion=emotion
        )
        
        # Sesi güncelle
        story['audio_url'] = new_audio_url
        story['audio_speed'] = audio_speed
        story['audio_slow'] = audio_slow
        if voice:
            story['voice'] = voice
        if emotion:
            story['emotion'] = emotion
        story['updated_at'] = datetime.now().isoformat()
        
        updated_story = self.story_storage.save_story(story)
        return updated_story
    
    async def regenerate_story_type(
        self,
        story_id: str,
        new_story_type: str
    ) -> dict:
        """
        Hikâyeyi farklı türde yeniden yazar.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Yeni türde hikâye üret
        new_story_text = await self.story_service.generate_story(
            story.get('theme', ''),
            story.get('language', 'tr'),
            new_story_type
        )
        
        # Hikâyeyi güncelle
        story['story_text'] = new_story_text
        story['story_type'] = new_story_type
        story['updated_at'] = datetime.now().isoformat()
        
        # Görseli de yeniden üret (yeni türe uygun)
        story['image_url'] = await self.image_service.generate_image(
            new_story_text,
            story.get('theme', ''),
            image_style=story.get('image_style', 'fantasy'),
            image_size=story.get('image_size', '1024x1024')
        )
        
        # Sesi yeniden üret
        story['audio_url'] = await self.tts_service.generate_speech(
            new_story_text,
            story.get('language', 'tr'),
            story_id,
            audio_speed=story.get('audio_speed', 1.0),
            audio_slow=story.get('audio_slow', False)
        )
        
        updated_story = self.story_storage.save_story(story)
        return updated_story

