from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
from datetime import datetime

from app.models import Story, UserProfile
from app.core.database import SessionLocal

class StoryRepository:
    def __init__(self, db_session: Session = None):
        self.db = db_session if db_session else SessionLocal()

    def create_story(self, story_data: Dict[str, Any], user_id: UUID) -> Story:
        """Create a new story in the database."""
        try:
            story = Story(
                id=UUID(story_data.get('story_id')) if story_data.get('story_id') else None,
                user_id=user_id,
                theme=story_data.get('theme', ''),
                story_text=story_data.get('story_text', ''),
                language=story_data.get('language', 'tr'),
                story_type=story_data.get('story_type', 'masal'),
                image_url=story_data.get('image_url'),
                image_public_id=story_data.get('image_public_id'),
                audio_url=story_data.get('audio_url'),
                audio_public_id=story_data.get('audio_public_id'),
                is_favorite=story_data.get('is_favorite', False),
                metadata=story_data.get('metadata', {})
            )
            self.db.add(story)
            self.db.commit()
            self.db.refresh(story)
            return story
        except Exception as e:
            self.db.rollback()
            raise e

    def get_story_by_id(self, story_id: UUID) -> Optional[Story]:
        """Get a story by its ID."""
        return self.db.query(Story).filter(Story.id == story_id).first()

    def get_user_stories(
        self, 
        user_id: UUID, 
        limit: int = 20, 
        offset: int = 0,
        favorite_only: bool = False,
        search_query: str = None
    ) -> List[Story]:
        """Get stories for a specific user with filtering. Uses eager loading to prevent N+1 queries."""
        query = self.db.query(Story).options(joinedload(Story.user)).filter(Story.user_id == user_id)
        
        if favorite_only:
            query = query.filter(Story.is_favorite == True)
        
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                (Story.theme.ilike(search)) | 
                (Story.story_text.ilike(search))
            )
            
        return query.order_by(desc(Story.created_at)).offset(offset).limit(limit).all()

    def update_story(self, story_id: UUID, updates: Dict[str, Any]) -> Optional[Story]:
        """Update a story."""
        story = self.get_story_by_id(story_id)
        if not story:
            return None
            
        for key, value in updates.items():
            if hasattr(story, key):
                setattr(story, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(story)
            return story
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_story(self, story_id: UUID) -> bool:
        """Delete a story."""
        story = self.get_story_by_id(story_id)
        if not story:
            return False
            
        try:
            self.db.delete(story)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def toggle_favorite(self, story_id: UUID) -> Optional[Story]:
        """Toggle favorite status."""
        story = self.get_story_by_id(story_id)
        if not story:
            return None
            
        story.is_favorite = not story.is_favorite
        self.db.commit()
        self.db.refresh(story)
        return story

    def close(self):
        """Close the database session."""
        self.db.close()
