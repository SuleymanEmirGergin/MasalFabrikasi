from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class StoryRatingService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.ratings_file = os.path.join(settings.STORAGE_PATH, "story_ratings.json")
        self.reviews_file = os.path.join(settings.STORAGE_PATH, "story_reviews.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.ratings_file, self.reviews_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def rate_story(self, story_id: str, user_id: str, rating: float) -> Dict:
        if rating < 1 or rating > 5:
            raise ValueError("Puan 1-5 arası olmalı")
        
        with open(self.ratings_file, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
        
        existing = next((r for r in ratings if r.get('story_id') == story_id and r.get('user_id') == user_id), None)
        if existing:
            existing['rating'] = rating
            existing['updated_at'] = datetime.now().isoformat()
        else:
            ratings.append({
                "rating_id": str(uuid.uuid4()),
                "story_id": story_id,
                "user_id": user_id,
                "rating": rating,
                "created_at": datetime.now().isoformat()
            })
        
        with open(self.ratings_file, 'w', encoding='utf-8') as f:
            json.dump(ratings, f, ensure_ascii=False, indent=2)
        
        return {"story_id": story_id, "user_id": user_id, "rating": rating}
    
    def get_story_rating(self, story_id: str) -> Dict:
        with open(self.ratings_file, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
        
        story_ratings = [r for r in ratings if r.get('story_id') == story_id]
        if not story_ratings:
            return {"average_rating": 0, "total_ratings": 0, "rating_distribution": {}}
        
        avg = sum(r.get('rating', 0) for r in story_ratings) / len(story_ratings)
        distribution = {i: sum(1 for r in story_ratings if r.get('rating') == i) for i in range(1, 6)}
        
        return {
            "average_rating": round(avg, 2),
            "total_ratings": len(story_ratings),
            "rating_distribution": distribution
        }
    
    def add_review(self, story_id: str, user_id: str, rating: float, review_text: str) -> Dict:
        review = {
            "review_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "rating": rating,
            "review_text": review_text,
            "created_at": datetime.now().isoformat(),
            "likes": 0
        }
        
        with open(self.reviews_file, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        reviews.append(review)
        with open(self.reviews_file, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        
        self.rate_story(story_id, user_id, rating)
        return review
    
    def get_story_reviews(self, story_id: str, limit: int = 10) -> List[Dict]:
        with open(self.reviews_file, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        
        story_reviews = [r for r in reviews if r.get('story_id') == story_id]
        return sorted(story_reviews, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]

