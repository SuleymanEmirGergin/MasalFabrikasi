from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SoundscapeRequest(BaseModel):
    type: str  # rain, white_noise, piano
    volume: float = 0.5

@router.get("/soundscapes")
async def get_soundscapes():
    """
    Get available bedtime soundscapes.
    """
    return {
        "soundscapes": [
            {
                "id": "rain",
                "name": "Yağmur Sesi",
                "url": "https://cdn.masalfabrikasi.app/sounds/rain.mp3"
            },
            {
                "id": "white_noise",
                "name": "Beyaz Gürültü",
                "url": "https://cdn.masalfabrikasi.app/sounds/white_noise.mp3"
            },
            {
                "id": "piano",
                "name": "Sakin Piyano",
                "url": "https://cdn.masalfabrikasi.app/sounds/piano.mp3"
            }
        ]
    }
