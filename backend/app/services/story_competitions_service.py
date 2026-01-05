from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime, timedelta


class StoryCompetitionsService:
    """Hikaye yarışmaları ve etkinlikler servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.competitions_file = os.path.join(settings.STORAGE_PATH, "story_competitions.json")
        self.submissions_file = os.path.join(settings.STORAGE_PATH, "competition_submissions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.competitions_file):
            with open(self.competitions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.submissions_file):
            with open(self.submissions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_competition(
        self,
        organizer_id: str,
        title: str,
        description: str,
        theme: str,
        rules: List[str],
        start_date: str,
        end_date: str,
        prizes: Optional[List[Dict]] = None,
        max_story_length: Optional[int] = None
    ) -> Dict:
        """Yeni yarışma oluşturur."""
        competition_id = str(uuid.uuid4())
        competition = {
            "competition_id": competition_id,
            "organizer_id": organizer_id,
            "title": title,
            "description": description,
            "theme": theme,
            "rules": rules,
            "start_date": start_date,
            "end_date": end_date,
            "prizes": prizes or [],
            "max_story_length": max_story_length,
            "submissions": [],
            "winners": [],
            "status": "upcoming",
            "created_at": datetime.now().isoformat()
        }
        
        competitions = self._load_competitions()
        competitions.append(competition)
        self._save_competitions(competitions)
        
        return {
            "competition_id": competition_id,
            "message": "Yarışma oluşturuldu"
        }
    
    async def submit_story(
        self,
        competition_id: str,
        story_id: str,
        user_id: str,
        story_text: str
    ) -> Dict:
        """Yarışmaya hikaye gönderir."""
        competitions = self._load_competitions()
        competition = next((c for c in competitions if c["competition_id"] == competition_id), None)
        
        if not competition:
            raise ValueError("Yarışma bulunamadı")
        
        # Tarih kontrolü
        now = datetime.now()
        start_date = datetime.fromisoformat(competition["start_date"])
        end_date = datetime.fromisoformat(competition["end_date"])
        
        if now < start_date:
            raise ValueError("Yarışma henüz başlamadı")
        if now > end_date:
            raise ValueError("Yarışma sona erdi")
        
        # Uzunluk kontrolü
        if competition.get("max_story_length") and len(story_text) > competition["max_story_length"]:
            raise ValueError(f"Hikaye çok uzun. Maksimum: {competition['max_story_length']} karakter")
        
        submission = {
            "submission_id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "story_id": story_id,
            "user_id": user_id,
            "story_text": story_text,
            "submitted_at": datetime.now().isoformat(),
            "score": 0,
            "judge_comments": []
        }
        
        submissions = self._load_submissions()
        submissions.append(submission)
        self._save_submissions(submissions)
        
        competition["submissions"].append(submission["submission_id"])
        self._save_competitions(competitions)
        
        return {
            "submission_id": submission["submission_id"],
            "message": "Hikaye yarışmaya gönderildi"
        }
    
    async def judge_submission(
        self,
        submission_id: str,
        judge_id: str,
        score: float,
        comments: str
    ) -> Dict:
        """Gönderimi değerlendirir."""
        submissions = self._load_submissions()
        submission = next((s for s in submissions if s["submission_id"] == submission_id), None)
        
        if not submission:
            raise ValueError("Gönderim bulunamadı")
        
        judge_comment = {
            "judge_id": judge_id,
            "score": score,
            "comments": comments,
            "judged_at": datetime.now().isoformat()
        }
        
        submission["judge_comments"].append(judge_comment)
        submission["score"] = sum(c["score"] for c in submission["judge_comments"]) / len(submission["judge_comments"])
        
        self._save_submissions(submissions)
        
        return {"message": "Değerlendirme kaydedildi"}
    
    async def get_competitions(
        self,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Yarışmaları getirir."""
        competitions = self._load_competitions()
        
        if status:
            competitions = [c for c in competitions if c["status"] == status]
        
        # Tarihe göre sırala
        competitions.sort(key=lambda x: x.get("start_date", ""))
        
        return competitions
    
    async def get_competition_leaderboard(
        self,
        competition_id: str
    ) -> List[Dict]:
        """Yarışma liderlik tablosunu getirir."""
        submissions = self._load_submissions()
        competition_submissions = [
            s for s in submissions if s["competition_id"] == competition_id
        ]
        
        # Skora göre sırala
        competition_submissions.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return competition_submissions
    
    def _load_competitions(self) -> List[Dict]:
        """Yarışmaları yükler."""
        try:
            with open(self.competitions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_competitions(self, competitions: List[Dict]):
        """Yarışmaları kaydeder."""
        with open(self.competitions_file, 'w', encoding='utf-8') as f:
            json.dump(competitions, f, ensure_ascii=False, indent=2)
    
    def _load_submissions(self) -> List[Dict]:
        """Gönderimleri yükler."""
        try:
            with open(self.submissions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_submissions(self, submissions: List[Dict]):
        """Gönderimleri kaydeder."""
        with open(self.submissions_file, 'w', encoding='utf-8') as f:
            json.dump(submissions, f, ensure_ascii=False, indent=2)

