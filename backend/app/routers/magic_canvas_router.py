from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
from app.services.image_service import ImageService
from app.services.cloud_storage_service import cloud_storage_service
import shutil
import os
import uuid

router = APIRouter()
image_service = ImageService()

@router.post("/magic-canvas/generate")
async def magic_canvas_generate(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    """
    Takes a sketch file and a prompt, returns a professional illustration.
    """
    temp_path = f"temp_{uuid.uuid4()}.png"
    try:
        # 1. Save upload temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Upload to Cloudinary to get public URL (Replicate needs URL)
        # Using a folder for temporary inputs
        sketch_url = await cloud_storage_service.upload_image(temp_path, folder="sketches")
        
        # 3. Generate with Img2Img
        generated_url = await image_service.generate_from_sketch(prompt, sketch_url)
        
        return {
            "original_sketch": sketch_url,
            "generated_image": generated_url,
            "prompt": prompt
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
