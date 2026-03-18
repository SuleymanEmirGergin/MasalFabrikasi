from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class StoryFeedbackService:
    """Hikaye yorumları ve geri bildirim sistemi"""
    
    def __init__(self):
        self.feedback_file = os.path.join(settings.STORAGE_PATH, "story_feedback.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_feedback(
        self,
        story_id: str,
        user_id: str,
        feedback_type: str,  # "comment", "suggestion", "rating", "bug_report"
        content: str,
        rating: Optional[int] = None
    ) -> Dict:
        """Geri bildirim ekler."""
        feedback_id = str(uuid.uuid4())
        feedback = {
            "feedback_id": feedback_id,
            "story_id": story_id,
            "user_id": user_id,
            "feedback_type": feedback_type,
            "content": content,
            "rating": rating,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "likes": 0,
            "replies": []
        }
        
        feedbacks = self._load_feedbacks()
        feedbacks.append(feedback)
        self._save_feedbacks(feedbacks)
        
        return {
            "feedback_id": feedback_id,
            "message": "Geri bildirim eklendi"
        }
    
    async def reply_to_feedback(
        self,
        feedback_id: str,
        user_id: str,
        reply_content: str
    ) -> Dict:
        """Geri bildirime yanıt verir."""
        feedbacks = self._load_feedbacks()
        feedback = next((f for f in feedbacks if f["feedback_id"] == feedback_id), None)
        
        if not feedback:
            raise ValueError("Geri bildirim bulunamadı")
        
        reply = {
            "reply_id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": reply_content,
            "created_at": datetime.now().isoformat()
        }
        
        feedback["replies"].append(reply)
        feedback["updated_at"] = datetime.now().isoformat()
        self._save_feedbacks(feedbacks)
        
        return {
            "reply_id": reply["reply_id"],
            "message": "Yanıt eklendi"
        }
    
    async def like_feedback(
        self,
        feedback_id: str,
        user_id: str
    ) -> Dict:
        """Geri bildirimi beğenir."""
        feedbacks = self._load_feedbacks()
        feedback = next((f for f in feedbacks if f["feedback_id"] == feedback_id), None)
        
        if not feedback:
            raise ValueError("Geri bildirim bulunamadı")
        
        if "liked_by" not in feedback:
            feedback["liked_by"] = []
        
        if user_id not in feedback["liked_by"]:
            feedback["liked_by"].append(user_id)
            feedback["likes"] = len(feedback["liked_by"])
            feedback["updated_at"] = datetime.now().isoformat()
            self._save_feedbacks(feedbacks)
            return {"message": "Beğenildi", "likes": feedback["likes"]}
        else:
            return {"message": "Zaten beğenilmiş"}
    
    async def get_story_feedback(
        self,
        story_id: str,
        feedback_type: Optional[str] = None
    ) -> List[Dict]:
        """Hikaye geri bildirimlerini getirir."""
        feedbacks = self._load_feedbacks()
        story_feedbacks = [f for f in feedbacks if f["story_id"] == story_id]
        
        if feedback_type:
            story_feedbacks = [f for f in story_feedbacks if f["feedback_type"] == feedback_type]
        
        # Tarihe göre sırala
        story_feedbacks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return story_feedbacks
    
    async def get_feedback_stats(self, story_id: str) -> Dict:
        """Hikaye geri bildirim istatistiklerini getirir."""
        feedbacks = self._load_feedbacks()
        story_feedbacks = [f for f in feedbacks if f["story_id"] == story_id]
        
        ratings = [f["rating"] for f in story_feedbacks if f.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "total_feedback": len(story_feedbacks),
            "comments": len([f for f in story_feedbacks if f["feedback_type"] == "comment"]),
            "suggestions": len([f for f in story_feedbacks if f["feedback_type"] == "suggestion"]),
            "bug_reports": len([f for f in story_feedbacks if f["feedback_type"] == "bug_report"]),
            "average_rating": round(avg_rating, 2),
            "total_likes": sum(f.get("likes", 0) for f in story_feedbacks)
        }
    
    def _load_feedbacks(self) -> List[Dict]:
        """Geri bildirimleri yükler."""
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_feedbacks(self, feedbacks: List[Dict]):
        """Geri bildirimleri kaydeder."""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

