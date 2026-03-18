from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os

router = APIRouter()

class VisionAnalysisResponse(BaseModel):
    description: str
    suggested_theme: str
    keywords: List[str]

@router.post("/analyze-image", response_model=VisionAnalysisResponse)
async def analyze_image_from_file(file: UploadFile = File(...)):
    """
    Yüklenen görseli analiz eder ve bir hikaye teması çıkarır.
    Gerçek senaryoda burada OpenAI Vision API veya benzeri bir model kullanılır.
    Şu an mock bir analiz döndüreceğiz.
    """
    try:
        # Dosyayı geçici olarak (veya storage'a) kaydedebiliriz, 
        # şimdilik sadece ismine göre basit logic kuruyoruz.
        
        # Mock Vision Logic
        # Gerçekte: ai_service.analyze_image(file_content)
        
        filename = file.filename.lower()
        
        description = "Görselde sevimli bir karakter ve renkli bir dünya görünüyor."
        suggested_theme = "Bilinmeyen Diyarlarda Macera"
        keywords = ["macera", "renkli", "gizem"]

        if "kedi" in filename or "cat" in filename:
            description = "Resimde sevimli bir kedi var."
            suggested_theme = "Uzaycı Kedi Mırnav"
            keywords = ["kedi", "uzay", "süt"]
        elif "köpek" in filename or "dog" in filename:
            description = "Resimde neşeli bir köpek oynuyor."
            suggested_theme = "Kayıp Kemik Peşinde"
            keywords = ["köpek", "park", "arkadaşlık"]
        elif "robot" in filename:
            description = "Metalik bir robot görünüyor."
            suggested_theme = "Duygusal Robotun Yolculuğu"
            keywords = ["robot", "teknoloji", "gelecek"]
        elif "ejderha" in filename or "dragon" in filename:
             description = "Büyük, dost canlısı bir ejderha."
             suggested_theme = "Ejderha ile Çay Saati"
             keywords = ["ejderha", "büyü", "prenses"]
            
        return {
            "description": description,
            "suggested_theme": suggested_theme,
            "keywords": keywords
        }

    except Exception as e:
        print(f"Vision error: {e}")
        raise HTTPException(status_code=500, detail="Görsel analiz hatası.")
