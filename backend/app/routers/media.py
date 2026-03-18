from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.services.voice_command_service import VoiceCommandService
from app.services.voice_story_creation_service import VoiceStoryCreationService
from app.services.ar_vr_service import ARVRService
from app.services.media_search_service import MediaSearchService
from app.services.audio_music_advanced_service import AudioMusicAdvancedService
from app.services.visual_media_advanced_service import VisualMediaAdvancedService
from app.services.story_ai_visualization_service import StoryAiVisualizationService
from app.services.story_voice_commands_service import StoryVoiceCommandsService
from app.services.story_vr_experience_service import StoryVrExperienceService
from app.services.story_multimedia_format_service import StoryMultimediaFormatService

router = APIRouter()

voice_command_service = VoiceCommandService()
voice_story_creation_service = VoiceStoryCreationService()
ar_vr_service = ARVRService()
media_search_service = MediaSearchService()
audio_music_advanced_service = AudioMusicAdvancedService()
visual_media_advanced_service = VisualMediaAdvancedService()
story_ai_visualization_service = StoryAiVisualizationService()
story_voice_commands_service = StoryVoiceCommandsService()
story_vr_experience_service = StoryVrExperienceService()
story_multimedia_format_service = StoryMultimediaFormatService()


# ========== Sesli Komutlar (Temel) ==========
@router.post("/voice/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """Ses dosyasını metne çevirir"""
    try:
        # OpenAI API expects (filename, file_content) tuple for format detection
        return {"text": await voice_command_service.transcribe_audio((file.filename, file.file))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-commands/process")
async def process_voice_command(audio_transcript: str, user_id: Optional[str] = None):
    return await voice_command_service.process_voice_command(audio_transcript, user_id)


# ========== Sesli Komutlar (Gelişmiş) ==========
class VoiceCommandRequest(BaseModel):
    user_id: str
    audio_text: str
    context: Optional[Dict] = None


@router.post("/voice/process-command")
async def process_story_voice_command(request: VoiceCommandRequest):
    return await story_voice_commands_service.process_voice_command(
        request.user_id, request.audio_text, request.context
    )


# ========== Sesli Hikâye Oluşturma ==========
@router.post("/stories/create-from-voice")
async def create_from_voice(audio_transcript: str, language: str = "tr"):
    return await voice_story_creation_service.create_story_from_voice(audio_transcript, language)


# ========== Audio & Music Advanced ==========
@router.post("/characters/{character_id}/save-voice")
async def save_character_voice(character_id: str, audio_file_path: str, voice_name: str, description: Optional[str] = None):
    return audio_music_advanced_service.save_character_voice(character_id, audio_file_path, voice_name, description)


@router.get("/characters/{character_id}/voices")
async def get_character_voices(character_id: str):
    return {"voices": audio_music_advanced_service.get_character_voices(character_id)}


@router.post("/music/generate")
async def generate_music(description: str, mood: str = "calm", duration: int = 30):
    return await audio_music_advanced_service.generate_music(description, mood, duration)


@router.get("/sound-effects/suggestions")
async def get_sound_effect_suggestions(story_text: str, scene_description: Optional[str] = None):
    return {"suggestions": audio_music_advanced_service.get_sound_effect_suggestions(story_text, scene_description)}


# ========== AR/VR Standard ==========
@router.post("/stories/{story_id}/ar-scene")
async def create_ar(story_id: str, scene_data: Dict):
    try:
        return ar_vr_service.create_ar_scene(story_id, scene_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== Sanal Gerçeklik (Advanced) ==========
class VRSceneRequest(BaseModel):
    story_id: str
    scene_description: str
    scene_type: str = "environment"


@router.post("/vr/create-scene")
async def create_vr_scene(request: VRSceneRequest):
    return await story_vr_experience_service.create_vr_scene(
        request.story_id, request.scene_description, request.scene_type
    )


class ImmersiveStoryRequest(BaseModel):
    story_id: str
    story_text: str


@router.post("/vr/create-immersive")
async def create_immersive_story(request: ImmersiveStoryRequest):
    return await story_vr_experience_service.create_immersive_story(
        request.story_id, request.story_text
    )


class VRInteractionRequest(BaseModel):
    scene_id: str
    interaction_type: str
    interaction_data: Dict


@router.post("/vr/add-interaction")
async def add_vr_interaction(request: VRInteractionRequest):
    return await story_vr_experience_service.add_interaction(
        request.scene_id, request.interaction_type, request.interaction_data
    )


# ========== Visual Media Advanced ==========
@router.post("/stories/{story_id}/create-video")
async def create_video_story(story_id: str, images: List[str], audio_url: Optional[str] = None, transition_style: str = "fade"):
    return await visual_media_advanced_service.create_video_story(story_id, images, audio_url, transition_style)


class VideoGenerationRequest(BaseModel):
    prompt: str
    image_url: Optional[str] = None
    seconds: int = 4
    resolution: str = "720p"


@router.post("/video/wiro-generate")
async def generate_video_wiro(request: VideoGenerationRequest):
    """Wiro AI Sora-2 ile video üretir"""
    return await visual_media_advanced_service.generate_video_wiro(
        prompt=request.prompt,
        image_url=request.image_url,
        seconds=request.seconds,
        resolution=request.resolution
    )


@router.post("/stories/{story_id}/create-animation")
async def create_animated_story(story_id: str, animation_style: str = "2d", frame_count: int = 60):
    return await visual_media_advanced_service.create_animated_story(story_id, animation_style, frame_count)


@router.post("/visualization/3d")
async def generate_3d_visualization(story_text: str, scene_description: str):
    return await visual_media_advanced_service.generate_3d_visualization(story_text, scene_description)


# ========== AI Görselleştirme ==========
class VisualizationRequest(BaseModel):
    story_id: str
    story_text: str
    visualization_type: str = "scene"


@router.post("/visualization/create")
async def create_story_visualization(request: VisualizationRequest):
    return await story_ai_visualization_service.create_story_visualization(
        request.story_id, request.story_text, request.visualization_type
    )


class CharacterVisualizationRequest(BaseModel):
    character_description: str
    character_name: str


@router.post("/visualization/character")
async def create_character_visualization(request: CharacterVisualizationRequest):
    return await story_ai_visualization_service.create_character_visualization(
        request.character_description, request.character_name
    )


class StoryboardRequest(BaseModel):
    story_id: str
    story_text: str
    num_panels: int = 6


@router.post("/visualization/storyboard")
async def create_storyboard(request: StoryboardRequest):
    return await story_ai_visualization_service.create_storyboard(
        request.story_id, request.story_text, request.num_panels
    )


# ========== Çoklu Medya Formatları ==========
class MultimediaStoryRequest(BaseModel):
    story_id: str
    story_text: str
    media_types: List[str] = ["text", "image", "audio"]


@router.post("/multimedia/create")
async def create_multimedia_story(request: MultimediaStoryRequest):
    return await story_multimedia_format_service.create_multimedia_story(
        request.story_id, request.story_text, request.media_types
    )


class RichMediaRequest(BaseModel):
    story_id: str
    story_text: str
    presentation_style: str = "modern"


@router.post("/multimedia/rich-presentation")
async def create_rich_media_presentation(request: RichMediaRequest):
    return await story_multimedia_format_service.create_rich_media_presentation(
        request.story_id, request.story_text, request.presentation_style
    )


# ========== Medya Arama ==========
@router.get("/search/by-image")
async def search_by_image(image_description: str, limit: int = 10):
    return {"stories": await media_search_service.search_by_image(image_description, limit)}


@router.get("/search/by-voice")
async def search_by_voice(voice_description: str, limit: int = 10):
    return {"stories": await media_search_service.search_by_voice_tone(voice_description, limit)}
