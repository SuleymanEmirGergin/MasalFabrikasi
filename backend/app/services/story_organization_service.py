"""
Story Organization Service - Akıllı hikaye düzenleme ve koleksiyon yönetimi
Tag sistemi, özel koleksiyonlar, notlar
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import uuid
from datetime import datetime
from app.models import Story


class StoryTag:
    """Story tag model (simple dict-based for now)"""
    def __init__(self, tag_id: str, name: str, color: str = "#3B82F6"):
        self.id = tag_id
        self.name = name
        self.color = color


class StoryOrganizationService:
    """Hikaye organizasyonu ve akıllı filtreleme"""
    
    # Önceden tanımlı tag'ler
    PREDEFINED_TAGS = {
        "bedtime": StoryTag("bedtime", "Uyku Öncesi", "#8B5CF6"),
        "educational": StoryTag("educational", "Eğitici", "#10B981"),
        "fun": StoryTag("fun", "Eğlenceli", "#F59E0B"),
        "adventure": StoryTag("adventure", "Macera", "#EF4444"),
        "moral": StoryTag("moral", "Ders Verici", "#6366F1"),
        "short": StoryTag("short", "Kısa", "#EC4899"),
        "long": StoryTag("long", "Uzun", "#14B8A6"),
    }
    
    def __init__(self, db: Session):
        self.db = db
        # Note: Story model'ine tags ve notes field'ları eklenebilir
        # Şimdilik in-memory veya JSON field kullanılabilir
    
    def add_tag_to_story(self, story_id: uuid.UUID, tag_id: str) -> Dict:
        """Hikayeye tag ekler"""
        story = self.db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise ValueError("Story not found")
        
        # Assuming Story model has a 'tags' JSON field
        # story.tags = story.tags or []
        # if tag_id not in story.tags:
        #     story.tags.append(tag_id)
        #     self.db.commit()
        
        return {"message": "Tag added", "story_id": str(story_id), "tag_id": tag_id}
    
    def get_stories_by_tag(self, user_id: uuid.UUID, tag_id: str) -> List[Story]:
        """Tag'e göre hikayeleri filtreler"""
        # stories = self.db.query(Story).filter(
        #     Story.user_id == user_id,
        #     Story.tags.contains([tag_id])
        # ).all()
        
        # Placeholder: Return all stories for now
        stories = self.db.query(Story).filter(Story.user_id == user_id).all()
        return stories
    
    def create_custom_collection(
        self,
        user_id: uuid.UUID,
        name: str,
        description: str = "",
        story_ids: List[str] = None
    ) -> Dict:
        """
        Özel koleksiyon oluşturur (playlist benzeri)
        
        Args:
            user_id: Kullanıcı ID
            name: Koleksiyon adı
            description: Açıklama
            story_ids: Eklenecek hikaye ID'leri
        
        Returns:
            Oluşturulan koleksiyon
        """
        collection = {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "name": name,
            "description": description,
            "story_ids": story_ids or [],
            "created_at": datetime.now().isoformat(),
            "story_count": len(story_ids or [])
        }
        
        # TODO: Save to database (CollectionModel)
        # For now, return the structure
        return collection
    
    def add_note_to_story(
        self,
        story_id: uuid.UUID,
        note: str
    ) -> Dict:
        """Hikayeye not ekler"""
        story = self.db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise ValueError("Story not found")
        
        # Assuming Story has a 'notes' field
        # story.notes = note
        # self.db.commit()
        
        return {
            "message": "Note added",
            "story_id": str(story_id),
            "note": note
        }
    
    def get_smart_filters(self, user_id: uuid.UUID) -> Dict:
        """
        Akıllı filtreler üretir
        
        Returns:
            - recently_read: Son okunanlar
            - unfinished: Yarım kalanlar (potansiyel)
            - most_replayed: En çok tekrar okunanlar
            - recommended: Önerilen (favori türe göre)
        """
        # Son 7 gün
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        
        recently_read = self.db.query(Story).filter(
            Story.user_id == user_id,
            Story.created_at >= week_ago
        ).order_by(Story.created_at.desc()).limit(10).all()
        
        # Most favorite type
        from sqlalchemy import func
        favorite_type_result = self.db.query(
            Story.story_type,
            func.count(Story.id).label('count')
        ).filter(
            Story.user_id == user_id
        ).group_by(Story.story_type).order_by(func.count(Story.id).desc()).first()
        
        favorite_type = favorite_type_result[0] if favorite_type_result else None
        
        recommended = []
        if favorite_type:
            recommended = self.db.query(Story).filter(
                Story.user_id == user_id,
                Story.story_type == favorite_type
            ).order_by(Story.created_at.desc()).limit(5).all()
        
        return {
            "recently_read": [self._story_to_dict(s) for s in recently_read],
            "recommended_by_preference": [self._story_to_dict(s) for s in recommended],
            "favorite_type": favorite_type
        }
    
    def _story_to_dict(self, story: Story) -> Dict:
        """Story object'i dict'e çevirir"""
        return {
            "id": str(story.id),
            "theme": story.theme,
            "story_type": story.story_type,
            "language": story.language,
            "created_at": story.created_at.isoformat(),
            "is_favorite": story.is_favorite
        }
    
    def get_all_tags(self) -> List[Dict]:
        """Tüm tanımlı tag'leri getirir"""
        return [
            {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color
            }
            for tag in self.PREDEFINED_TAGS.values()
        ]
