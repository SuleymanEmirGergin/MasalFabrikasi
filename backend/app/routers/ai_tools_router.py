from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
import shutil
import os
import uuid
from app.services.voice_cloning_service import voice_cloning_service
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models import UserProfile

router = APIRouter()

@router.post("/clone")
async def clone_voice(
    name: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an audio sample to clone a voice.
    Returns the new voice_id.
    """
    # 1. Save temp file
    temp_filename = f"temp_{uuid.uuid4()}.mp3"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Call Service
        result = await voice_cloning_service.clone_voice(name, description, temp_filename)
        
        # 3. Cleanup
        os.remove(temp_filename)
        
        return result
        
    except Exception as e:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/styles")
def get_art_styles():
    """
    Returns available art styles for image generation.
    """
    return [
        {"id": "pixar", "name": "3D Animasyon (Pixar Tarzı)", "prompt_suffix": "3d render, pixar style, disney animation, 8k, cute, vibrant"},
        {"id": "watercolor", "name": "Sulu Boya", "prompt_suffix": "watercolor painting, artistic, soft colors, dreamy"},
        {"id": "pixel", "name": "Piksel Sanatı", "prompt_suffix": "pixel art, 16-bit, retro game style"},
        {"id": "realistic", "name": "Gerçekçi", "prompt_suffix": "photorealistic, 8k, cinematic lighting, detailed"},
        {"id": "anime", "name": "Anime", "prompt_suffix": "anime style, studio ghibli, celestial, vivid colors"}
    ]
