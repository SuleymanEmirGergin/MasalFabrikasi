from sqlalchemy.orm import Session
from app.models import InteractiveStory, StorySegment, StoryChoice
from typing import List, Optional

class InteractiveStoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_story(self, user_id: str, title: str, theme: str, character_name: str) -> InteractiveStory:
        story = InteractiveStory(
            user_id=user_id,
            title=title,
            theme=theme,
            character_name=character_name,
            status="active"
        )
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)
        return story

    def get_story(self, story_id: str) -> Optional[InteractiveStory]:
        return self.db.query(InteractiveStory).filter(InteractiveStory.id == story_id).first()

    def add_segment(self, story_id: str, content: str, step_number: int, is_ending: bool = False, image_url: str = None) -> StorySegment:
        segment = StorySegment(
            story_id=story_id,
            content=content,
            step_number=step_number,
            is_ending=is_ending,
            image_url=image_url
        )
        self.db.add(segment)
        self.db.commit()
        self.db.refresh(segment)
        return segment

    def get_segment(self, segment_id: str) -> Optional[StorySegment]:
        return self.db.query(StorySegment).filter(StorySegment.id == segment_id).first()

    def add_choices(self, segment_id: str, choices: List[str]) -> List[StoryChoice]:
        choice_objs = []
        for text in choices:
            choice = StoryChoice(
                segment_id=segment_id,
                choice_text=text
            )
            self.db.add(choice)
            choice_objs.append(choice)
        
        self.db.commit()
        # Refresh all
        for c in choice_objs:
            self.db.refresh(c)
        return choice_objs

    def select_choice(self, choice_id: str, next_segment_id: str) -> Optional[StoryChoice]:
        choice = self.db.query(StoryChoice).filter(StoryChoice.id == choice_id).first()
        if choice:
            choice.is_selected = True
            choice.next_segment_id = next_segment_id
            self.db.commit()
            self.db.refresh(choice)
        return choice
