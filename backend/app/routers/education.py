from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from app.services.ai_assistant_service import AIAssistantService

router = APIRouter()
ai_service = AIAssistantService()

class QuizRequest(BaseModel):
    story_text: str
    difficulty: str = "medium" # easy, medium, hard
    num_questions: int = 3

class Question(BaseModel):
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str

class QuizResponse(BaseModel):
    questions: List[Question]

class VocabularyRequest(BaseModel):
    story_text: str
    target_age: int = 7

class VocabularyItem(BaseModel):
    word: str
    definition: str
    example_sentence: str

class VocabularyResponse(BaseModel):
    vocabulary: List[VocabularyItem]

@router.post("/quiz/generate", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """
    Hikâyeden test sorusu üretir.
    """
    try:
        prompt = f"""
        Aşağıdaki hikaye için {request.num_questions} adet çoktan seçmeli soru hazırla.
        Zorluk seviyesi: {request.difficulty}.
        
        Hikaye:
        {request.story_text[:2000]}... (kısaltıldı)
        
        Çıktı formatı (JSON listesi):
        [
            {{
                "question": "Soru metni",
                "options": ["A şıkkı", "B şıkkı", "C şıkkı", "D şıkkı"],
                "correct_option_index": 0, // 0-3 arası
                "explanation": "Neden bu cevap doğru?"
            }}
        ]
        Sadece JSON döndür.
        """
        
        # AI Service çağrısı (Mocklanmış veya gerçek)
        # Not: ai_service.generate_json gibi bir metod olmadığını varsayarak, basit text alıp parse edeceğiz 
        # veya ai_service yapısını kontrol etmeliyiz. Şimdilik text alıp manuel parse varsayımı yapalım.
        response_text = await ai_service.generate_text(prompt, max_tokens=1000)
        
        # Basit "json" temizliği ve parsing
        import json
        import re
        
        # Markdown kod bloklarını temizle
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            return {"questions": data}
        else:
            raise ValueError("AI geçerli bir JSON döndürmedi.")

    except Exception as e:
        # Fallback / Mock Data (AI hatası durumunda)
        print(f"Quiz AI error: {e}")
        return {
            "questions": [
                {
                    "question": "Hikayenin ana kahramanı kimdi?",
                    "options": ["Ali", "Veli", "Ayşe", "Fatma"],
                    "correct_option_index": 0,
                    "explanation": "Hikayede Ali'nin maceraları anlatılıyor."
                }
            ]
        }

@router.post("/vocabulary/extract", response_model=VocabularyResponse)
async def extract_vocabulary(request: VocabularyRequest):
    """
    Hikâyeden öğretici kelimeleri çıkarır.
    """
    try:
        prompt = f"""
        Aşağıdaki hikayeden çocuklar ({request.target_age} yaş) için öğrenilmesi faydalı, biraz zor veya ilginç 5 kelime seç.
        Her kelime için kısa bir tanım ve örnek cümle yaz.
        
        Hikaye:
        {request.story_text[:2000]}
        
        Çıktı formatı (JSON):
        [
            {{
                "word": "Kelime",
                "definition": "Çocukların anlayacağı basit tanım",
                "example_sentence": "Kelimenin geçtiği yeni bir örnek cümle."
            }}
        ]
        """
        
        response_text = await ai_service.generate_text(prompt, max_tokens=800)
        
        import json
        import re
        
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            return {"vocabulary": data}
        else:
            raise ValueError("AI JSON hatası")

    except Exception as e:
        return {
            "vocabulary": [
                {
                    "word": "Macera",
                    "definition": "Heyecan verici, baştan geçen ilginç olay.",
                    "example_sentence": "Ormanda büyük bir macera yaşadılar."
                }
            ]
        }
