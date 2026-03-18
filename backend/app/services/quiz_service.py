from typing import List, Dict, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime
from app.services.story_storage import StoryStorage


class QuizService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
        self.quizzes_file = os.path.join(settings.STORAGE_PATH, "quizzes.json")
        self.quiz_results_file = os.path.join(settings.STORAGE_PATH, "quiz_results.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Quiz dosyalarını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.quizzes_file):
            with open(self.quizzes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.quiz_results_file):
            with open(self.quiz_results_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def generate_quiz(
        self,
        story_id: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> Dict:
        """
        Hikâyeden quiz soruları üretir.
        
        Args:
            story_id: Hikâye ID'si
            num_questions: Soru sayısı
            difficulty: Zorluk seviyesi (easy, medium, hard)
        
        Returns:
            Quiz objesi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        theme = story.get('theme', '')
        language = story.get('language', 'tr')
        
        # AI ile sorular üret
        prompt = self._create_quiz_prompt(story_text, theme, num_questions, difficulty, language)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir eğitim uzmanısın. Hikâyelerden anlama soruları üretiyorsun."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        quiz_data = json.loads(response.choices[0].message.content)
        
        # Quiz'i kaydet
        quiz = {
            "quiz_id": str(uuid.uuid4()),
            "story_id": story_id,
            "questions": quiz_data.get("questions", []),
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_quiz(quiz)
        
        return quiz
    
    def _create_quiz_prompt(
        self,
        story_text: str,
        theme: str,
        num_questions: int,
        difficulty: str,
        language: str
    ) -> str:
        """Quiz prompt'u oluşturur."""
        difficulty_map = {
            "easy": "Kolay - Metinde doğrudan geçen bilgiler",
            "medium": "Orta - Biraz çıkarım gerektiren sorular",
            "hard": "Zor - Analiz ve yorum gerektiren sorular"
        }
        
        prompt = f"""
Aşağıdaki hikâyeden {num_questions} adet quiz sorusu üret. Zorluk seviyesi: {difficulty_map.get(difficulty, 'Orta')}

Hikâye Teması: {theme}
Hikâye Metni:
{story_text}

Soru tipleri:
1. Çoktan seçmeli (multiple_choice): 4 seçenek, 1 doğru cevap
2. Doğru/Yanlış (true_false): Doğru veya Yanlış
3. Boşluk doldurma (fill_blank): Cevap tek kelime veya kısa cümle

Her soru için:
- question: Soru metni
- type: Soru tipi (multiple_choice, true_false, fill_blank)
- options: Seçenekler (sadece multiple_choice için)
- correct_answer: Doğru cevap
- explanation: Neden bu cevap doğru? (kısa açıklama)
- points: Puan (kolay: 10, orta: 15, zor: 20)

JSON formatında döndür:
{{
  "questions": [
    {{
      "question": "Soru metni",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "Açıklama",
      "points": 10
    }}
  ]
}}
"""
        return prompt
    
    def _save_quiz(self, quiz: Dict):
        """Quiz'i kaydeder."""
        with open(self.quizzes_file, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
        
        quizzes.append(quiz)
        
        with open(self.quizzes_file, 'w', encoding='utf-8') as f:
            json.dump(quizzes, f, ensure_ascii=False, indent=2)
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        """Quiz'i getirir."""
        with open(self.quizzes_file, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
        
        return next((q for q in quizzes if q.get('quiz_id') == quiz_id), None)
    
    def get_quiz_by_story(self, story_id: str) -> Optional[Dict]:
        """Hikâyeye ait quiz'i getirir."""
        with open(self.quizzes_file, 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
        
        return next((q for q in quizzes if q.get('story_id') == story_id), None)
    
    def submit_quiz_answer(
        self,
        quiz_id: str,
        user_id: str,
        answers: List[Dict]
    ) -> Dict:
        """
        Quiz cevaplarını kaydeder ve skor hesaplar.
        
        Args:
            quiz_id: Quiz ID'si
            user_id: Kullanıcı ID'si
            answers: Cevaplar [{"question_index": 0, "answer": "A"}, ...]
        
        Returns:
            Sonuç: skor, toplam_puan, doğru_yanlış
        """
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            raise ValueError("Quiz bulunamadı")
        
        questions = quiz.get('questions', [])
        total_points = 0
        earned_points = 0
        correct_count = 0
        results = []
        
        for i, question in enumerate(questions):
            points = question.get('points', 10)
            total_points += points
            
            user_answer = next(
                (a.get('answer') for a in answers if a.get('question_index') == i),
                None
            )
            
            correct_answer = question.get('correct_answer', '').lower().strip()
            user_answer_clean = str(user_answer).lower().strip() if user_answer else ''
            
            is_correct = correct_answer == user_answer_clean
            
            if is_correct:
                earned_points += points
                correct_count += 1
            
            results.append({
                "question_index": i,
                "question": question.get('question'),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get('explanation', ''),
                "points_earned": points if is_correct else 0
            })
        
        # Sonucu kaydet
        result = {
            "result_id": str(uuid.uuid4()),
            "quiz_id": quiz_id,
            "story_id": quiz.get('story_id'),
            "user_id": user_id,
            "total_points": total_points,
            "earned_points": earned_points,
            "correct_count": correct_count,
            "total_questions": len(questions),
            "results": results,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_quiz_result(result)
        
        return result
    
    def _save_quiz_result(self, result: Dict):
        """Quiz sonucunu kaydeder."""
        with open(self.quiz_results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        results.append(result)
        
        with open(self.quiz_results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def get_user_quiz_results(self, user_id: str) -> List[Dict]:
        """Kullanıcının quiz sonuçlarını getirir."""
        with open(self.quiz_results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return [r for r in results if r.get('user_id') == user_id]
    
    def get_quiz_statistics(self, quiz_id: str) -> Dict:
        """Quiz istatistiklerini getirir."""
        with open(self.quiz_results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        quiz_results = [r for r in results if r.get('quiz_id') == quiz_id]
        
        if not quiz_results:
            return {
                "total_attempts": 0,
                "average_score": 0,
                "perfect_scores": 0
            }
        
        total_attempts = len(quiz_results)
        total_points = sum(r.get('earned_points', 0) for r in quiz_results)
        max_points = quiz_results[0].get('total_points', 100) if quiz_results else 100
        perfect_scores = sum(1 for r in quiz_results if r.get('earned_points') == max_points)
        
        return {
            "total_attempts": total_attempts,
            "average_score": round(total_points / total_attempts, 2) if total_attempts > 0 else 0,
            "perfect_scores": perfect_scores,
            "average_percentage": round((total_points / (max_points * total_attempts)) * 100, 2) if total_attempts > 0 else 0
        }

