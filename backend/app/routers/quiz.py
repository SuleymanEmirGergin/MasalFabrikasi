from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.quiz_service import QuizService

router = APIRouter()
quiz_service = QuizService()


class GenerateQuizRequest(BaseModel):
    num_questions: int = 5
    difficulty: str = "medium"


class SubmitQuizRequest(BaseModel):
    answers: List[Dict]  # [{"question_index": 0, "answer": "A"}, ...]


@router.post("/stories/{story_id}/generate-quiz")
async def generate_quiz(story_id: str, request: GenerateQuizRequest):
    """
    Hikâye için quiz üretir.
    """
    try:
        quiz = await quiz_service.generate_quiz(
            story_id,
            request.num_questions,
            request.difficulty
        )
        return quiz
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz üretilirken hata oluştu: {str(e)}")


@router.get("/stories/{story_id}/quiz")
async def get_story_quiz(story_id: str):
    """
    Hikâyeye ait quiz'i getirir.
    """
    try:
        quiz = quiz_service.get_quiz_by_story(story_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz bulunamadı")
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz yüklenirken hata oluştu: {str(e)}")


@router.post("/quizzes/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, user_id: str, request: SubmitQuizRequest):
    """
    Quiz cevaplarını gönderir ve skor hesaplar.
    """
    try:
        result = quiz_service.submit_quiz_answer(
            quiz_id,
            user_id,
            request.answers
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz gönderilirken hata oluştu: {str(e)}")


@router.get("/users/{user_id}/quiz-results")
async def get_user_quiz_results(user_id: str):
    """
    Kullanıcının quiz sonuçlarını getirir.
    """
    try:
        results = quiz_service.get_user_quiz_results(user_id)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sonuçlar yüklenirken hata oluştu: {str(e)}")


@router.get("/quizzes/{quiz_id}/statistics")
async def get_quiz_statistics(quiz_id: str):
    """
    Quiz istatistiklerini getirir.
    """
    try:
        stats = quiz_service.get_quiz_statistics(quiz_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistikler yüklenirken hata oluştu: {str(e)}")

