from sqlalchemy.orm import Session
from app.models import InteractiveStory, StorySegment
from app.repositories.interactive_repository import InteractiveStoryRepository
from openai import AsyncOpenAI
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class InteractiveStoryService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    async def start_interactive_story(self, db: Session, user_id: str, theme: str, character_name: str) -> tuple[InteractiveStory, StorySegment]:
        """
        Starts a new interactive story. Creates the main story record and the first segment.
        """
        repository = InteractiveStoryRepository(db)
        
        # 1. Create Story Record
        story = repository.create_story(user_id, f"{character_name} - {theme}", theme, character_name)

        # 2. Generate First Segment
        prompt = f"""
        Bir çocuk masalı başlat. (İnteraktif Hikaye)
        Kahraman: {character_name}
        Tema: {theme}
        
        Hikayenin giriş kısmını yaz (maksimum 100 kelime). Çok heyecanlı bir noktada bırak.
        Sonunda kahramanın yapması gereken kritik bir seçim sun.
        
        Yanıtı geçerli bir JSON objesi olarak ver:
        {{
            "content": "Hikaye metni...",
            "choices": ["Seçenek 1", "Seçenek 2"]
        }}
        Sadece JSON ver, başka bir şey yazma.
        """
        
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen yaratıcı bir çocuk masalı yazarsın. Çıktıların daima geçerli JSON formatında olmalı."},
                    {"role": "user", "content": prompt}
                ],
                model="gpt-4", # Or explicit model if needed
                response_format={"type": "json_object"}
            )
            
            response_content = chat_completion.choices[0].message.content
            data = json.loads(response_content)
            
            story_text = data.get("content", "Hikaye başlatılamadı.")
            choices_list = data.get("choices", ["Devam et", "Sonlandır"])

            # 3. Save Segment
            segment = repository.add_segment(story.id, story_text, 1)

            # 4. Save Choices
            repository.add_choices(segment.id, choices_list)
            
            return story, segment

        except Exception as e:
            logger.error(f"Error generating story start: {e}")
            # Fallback mechanism
            segment = repository.add_segment(story.id, "Bir hata oluştu ama macera devam edecek...", 1)
            repository.add_choices(segment.id, ["Yeniden Dene"])
            return story, segment

    async def make_choice(self, db: Session, segment_id: str, choice_id: str) -> StorySegment:
        """
        Process user choice and generate the next segment.
        """
        repository = InteractiveStoryRepository(db)
        
        # 1. Get Previous Context
        prev_segment = repository.get_segment(segment_id)
        if not prev_segment:
            raise ValueError("Segment not found")
            
        story = repository.get_story(prev_segment.story_id)
        
        # 2. Process Selection
        # Note: In a real recursive model we'd link segments.
        # Here we just mark the choice and generate a NEW segment.
        # But `select_choice` updates next_segment_id. We need the new segment ID first.
        # Let's interact with AI first.
        
        choice = repository.select_choice(choice_id, None) # Get choice text first
        if not choice:
             raise ValueError("Choice not found")

        # 3. Generate Next Segment
        prompt = f"""
        Mevcut Hikaye: {prev_segment.content}
        Yapılan Seçim: {choice.choice_text}
        Tema: {story.theme}
        Kahraman: {story.character_name}
        
        Bu seçime göre hikayeyi devam ettir (maksimum 100 kelime).
        Eğer hikaye bitmediyse yeni bir dilemma/seçim sun. 
        Eğer hikaye güzel bir sona ulaştıysa "is_ending": true yap ve choices listesini boş bırak.
        
        Yanıtı geçerli bir JSON objesi olarak ver:
        {{
            "content": "Hikaye metni...",
            "is_ending": false,
            "choices": ["Seçenek A", "Seçenek B"]
        }}
        """
        
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen yaratıcı bir çocuk masalı yazarsın. Çıktıların daima geçerli JSON formatında olmalı."},
                    {"role": "user", "content": prompt}
                ],
                model="gpt-4",
                response_format={"type": "json_object"}
            )
            
            response_content = chat_completion.choices[0].message.content
            data = json.loads(response_content)
            
            next_text = data.get("content", "Hikaye devam ediyor...")
            is_ending = data.get("is_ending", False)
            choices_list = data.get("choices", [])
            
            # 4. Save New Segment
            new_step = prev_segment.step_number + 1
            new_segment = repository.add_segment(story.id, next_text, new_step, is_ending=is_ending)
            
            # 5. Save Choices
            if not is_ending and choices_list:
                repository.add_choices(new_segment.id, choices_list)
                
            # 6. Link Checkpoint (Update previous choice with next segment id)
            repository.select_choice(choice_id, new_segment.id)
            
            return new_segment
            
        except Exception as e:
            logger.error(f"Error generating story continuation: {e}")
            new_segment = repository.add_segment(story.id, "Bir hata oluştu.", prev_segment.step_number + 1, is_ending=True)
            return new_segment

interactive_story_service = InteractiveStoryService()
