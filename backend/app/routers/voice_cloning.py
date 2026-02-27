from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import shutil
from app.services.voice_cloning_service import voice_cloning_service
from app.core.config import settings

router = APIRouter()

class VoiceResponse(BaseModel):
    voice_id: str
    name: str

class ClonedVoice(BaseModel):
    id: str
    name: str
    preview_url: Optional[str] = None

@router.post("/clone", response_model=Dict[str, str])
async def clone_voice(name: str = Form(...), files: List[UploadFile] = File(...)):
    """
    Ses örnekleri yükleyerek yeni bir ses klonlar (ElevenLabs Instant Voice Cloning).
    """
    temp_files = []
    try:
        # Geçici dosyaları kaydet
        for file in files:
            temp_path = f"{settings.STORAGE_PATH}/temp/{file.filename}"
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(temp_path)
            
        # Servisi çağır
        result = await voice_cloning_service.clone_voice(name, temp_files)
        
        return {
            "voice_id": result["voice_id"],
            "name": name,
            "message": "Ses başarıyla klonlandı! Artık hikayelerde kullanabilirsiniz."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Geçici dosyaları temizle
        for path in temp_files:
            try:
                os.remove(path)
            except:
                pass

@router.get("/list", response_model=List[ClonedVoice])
async def list_cloned_voices():
    """
    Kullanıcının klonlanmış seslerini listeler.
    """
    try:
        return await voice_cloning_service.get_cloned_voices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{voice_id}")
async def delete_cloned_voice(voice_id: str):
    """
    Klonlanmış sesi siler.
    """
    try:
        success = await voice_cloning_service.delete_voice(voice_id)
        if not success:
             raise HTTPException(status_code=404, detail="Voice not found or could not be deleted")
        return {"message": "Voice deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

