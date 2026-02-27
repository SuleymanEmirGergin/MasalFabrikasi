from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.character_service import CharacterService

router = APIRouter()
character_service = CharacterService()


class CharacterCreateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    age: Optional[int] = None
    personality: Optional[str] = None
    appearance: Optional[str] = None
    character_type: str = "hero"
    language: str = "tr"


class CharacterUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    age: Optional[int] = None
    personality: Optional[str] = None
    appearance: Optional[str] = None
    character_type: Optional[str] = None


@router.post("/characters/create")
async def create_character(request: CharacterCreateRequest):
    """
    Yeni bir karakter oluşturur.
    """
    try:
        character = await character_service.create_character(
            name=request.name,
            description=request.description,
            age=request.age,
            personality=request.personality,
            appearance=request.appearance,
            character_type=request.character_type,
            language=request.language
        )
        return character
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Karakter oluşturulurken hata oluştu: {str(e)}")


@router.get("/characters")
async def get_characters(user_id: Optional[str] = None):
    """
    Kullanıcının karakterlerini listeler.
    """
    try:
        characters = character_service.get_all_characters(user_id=user_id)
        return {"characters": characters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Karakterler yüklenirken hata oluştu: {str(e)}")


@router.get("/characters/{character_id}")
async def get_character(character_id: str):
    """
    Belirli bir karakteri getirir.
    """
    try:
        character = character_service.get_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Karakter bulunamadı")
        return character
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Karakter yüklenirken hata oluştu: {str(e)}")


@router.put("/characters/{character_id}")
async def update_character(character_id: str, request: CharacterUpdateRequest):
    """
    Karakteri günceller.
    """
    try:
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.age is not None:
            updates['age'] = request.age
        if request.personality is not None:
            updates['personality'] = request.personality
        if request.appearance is not None:
            updates['appearance'] = request.appearance
        if request.character_type is not None:
            updates['character_type'] = request.character_type
        
        character = character_service.update_character(character_id, updates)
        if not character:
            raise HTTPException(status_code=404, detail="Karakter bulunamadı")
        return character
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Karakter güncellenirken hata oluştu: {str(e)}")


@router.delete("/characters/{character_id}")
async def delete_character(character_id: str):
    """
    Karakteri siler.
    """
    try:
        success = character_service.delete_character(character_id)
        if not success:
            raise HTTPException(status_code=404, detail="Karakter bulunamadı")
        return {"message": "Karakter silindi", "character_id": character_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Karakter silinirken hata oluştu: {str(e)}")

