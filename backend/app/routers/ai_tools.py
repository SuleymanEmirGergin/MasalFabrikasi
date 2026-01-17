from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.services.ai_chatbot_service import AIChatbotService
from app.services.advanced_translation_service import AdvancedTranslationService
from app.services.story_ai_character_chat_advanced_service import StoryAiCharacterChatAdvancedService
from app.services.story_translation_advanced_service import StoryTranslationAdvancedService
from app.services.multilang_service import MultilangService
from app.services.multilang_enhanced_service import MultilangEnhancedService
from app.services.ai_editor_service import AIEditorService
from app.services.story_enhancement_service import StoryEnhancementService
from app.services.ai_editor_enhanced_service import AIEditorEnhancedService
from app.services.ai_assistant_service import AIAssistantService
from app.services.ai_analysis_advanced_service import AIAnalysisAdvancedService
from app.services.ai_recommendations_advanced_service import AIRecommendationsAdvancedService
from app.services.ai_improvement_advanced_service import AIImprovementAdvancedService
from app.services.ai_moderation_advanced_service import AIModerationAdvancedService
from app.services.content_moderation_service import ContentModerationService
from app.services.story_storage import StoryStorage
from app.services.ai_features_advanced_service import AIFeaturesAdvancedService

router = APIRouter()

ai_chatbot_service = AIChatbotService()
advanced_translation_service = AdvancedTranslationService()
story_ai_character_chat_advanced_service = StoryAiCharacterChatAdvancedService()
story_translation_advanced_service = StoryTranslationAdvancedService()
multilang_service = MultilangService()
multilang_enhanced_service = MultilangEnhancedService()
ai_editor_service = AIEditorService()
story_enhancement_service = StoryEnhancementService()
ai_editor_enhanced_service = AIEditorEnhancedService()
ai_assistant_service = AIAssistantService()
ai_analysis_advanced_service = AIAnalysisAdvancedService()
ai_recommendations_advanced_service = AIRecommendationsAdvancedService()
ai_improvement_advanced_service = AIImprovementAdvancedService()
ai_moderation_advanced_service = AIModerationAdvancedService()
content_moderation_service = ContentModerationService()
story_storage = StoryStorage()
ai_features_advanced_service = AIFeaturesAdvancedService()


# ========== AI Karakter Sohbeti (Temel) ==========
class ChatRequest(BaseModel):
    user_message: str
    conversation_id: Optional[str] = None


class StateRequest(BaseModel):
    state_type: str
    data: Optional[Dict] = None


@router.post("/chatbot/conversations/{conversation_id}/state")
async def set_conversation_state(conversation_id: str, request: StateRequest):
    success = ai_chatbot_service.set_pending_state(conversation_id, request.state_type, request.data)
    if not success:
        raise HTTPException(status_code=404, detail="Konuşma bulunamadı")
    return {"message": "Durum güncellendi", "state": request.state_type}


@router.get("/chatbot/conversations/{conversation_id}/state")
async def get_conversation_state(conversation_id: str):
    state = ai_chatbot_service.get_pending_state(conversation_id)
    return {"pending_state": state}


@router.delete("/chatbot/conversations/{conversation_id}/state")
async def clear_conversation_state(conversation_id: str):
    ai_chatbot_service.clear_pending_state(conversation_id)
    return {"message": "Durum temizlendi"}


@router.post("/characters/{character_id}/chat")
async def chat_with_character_basic(character_id: str, user_id: str, request: ChatRequest):
    try:
        return await ai_chatbot_service.chat_with_character(character_id, request.user_message, request.conversation_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== AI Karakter Sohbetleri (Advanced) ==========
class CharacterChatbotRequest(BaseModel):
    story_id: str
    character_name: str
    character_background: str
    personality_traits: List[str]


@router.post("/character-chat/create")
async def create_character_chatbot(request: CharacterChatbotRequest):
    return await story_ai_character_chat_advanced_service.create_character_chatbot(
        request.story_id, request.character_name, request.character_background, request.personality_traits
    )


class ChatRequestAdvanced(BaseModel):
    chatbot_id: str
    user_message: str
    user_id: Optional[str] = None


@router.post("/character-chat/chat")
async def chat_with_character_advanced(request: ChatRequestAdvanced):
    return await story_ai_character_chat_advanced_service.chat_with_character(
        request.chatbot_id, request.user_message, request.user_id
    )


class GroupChatRequest(BaseModel):
    story_id: str
    character_ids: List[str]


@router.post("/character-chat/group")
async def create_group_chat(request: GroupChatRequest):
    return await story_ai_character_chat_advanced_service.create_group_chat(
        request.story_id, request.character_ids
    )


# ========== Gelişmiş Çeviri (Temel & Advanced) ==========
class TranslateRequest(BaseModel):
    target_language: str
    source_language: str = "tr"
    preserve_tone: bool = True


@router.post("/stories/{story_id}/translate-advanced")
async def translate_advanced(story_id: str, request: TranslateRequest):
    story = story_storage.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    return await advanced_translation_service.translate_story_realtime(
        story.get('story_text', ''), request.target_language, request.source_language, request.preserve_tone
    )


class TranslationAdvancedRequest(BaseModel):
    story_id: str
    story_text: str
    target_language: str
    cultural_adaptation: bool = True
    preserve_style: bool = True


@router.post("/translation/translate-with-context")
async def translate_with_context(request: TranslationAdvancedRequest):
    return await story_translation_advanced_service.translate_with_context(
        request.story_id, request.story_text, request.target_language,
        request.cultural_adaptation, request.preserve_style
    )


@router.post("/stories/{story_id}/multilang")
async def create_multilang(story_id: str, target_languages: List[str]):
    try:
        return await multilang_service.create_multilang_story(story_id, target_languages)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stories/{story_id}/multilang")
async def get_multilang(story_id: str):
    multilang = multilang_service.get_multilang_story(story_id)
    if not multilang:
        raise HTTPException(status_code=404, detail="Çoklu dil hikâyesi bulunamadı")
    return multilang


@router.post("/stories/{story_id}/translate")
async def auto_translate(story_id: str, target_language: str):
    try:
        return await ai_features_advanced_service.auto_translate(story_id, target_language)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stories/{story_id}/multilang-enhanced")
async def create_multilingual_story_enhanced(story_id: str, target_languages: List[str]):
    try:
        return await multilang_enhanced_service.create_multilingual_story(story_id, target_languages)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stories/{story_id}/compare-languages")
async def get_comparison_mode(story_id: str, languages: List[str]):
    try:
        return multilang_enhanced_service.get_comparison_mode(story_id, languages)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== AI Editör (Basic, Advanced, Enhanced) ==========
@router.post("/ai-editor/spell-check")
async def spell_check(text: str, language: str = "tr"):
    return await ai_editor_service.realtime_spell_check(text, language)


@router.post("/ai-editor/style-suggestions")
async def get_style_suggestions(text: str):
    return {"suggestions": await ai_editor_service.get_style_suggestions(text)}


@router.get("/ai-editor/readability")
async def get_readability(text: str):
    return ai_editor_service.calculate_readability_score(text)


class EditStoryRequest(BaseModel):
    story_id: str
    story_text: str
    edit_instruction: str
    edit_type: str = "general"


@router.post("/ai-editor/edit")
async def edit_story(request: EditStoryRequest):
    return await story_enhancement_service.process(
        "ai-editor-advanced",
        request.story_text,
        edit_instruction=request.edit_instruction
    )


class ImproveFlowRequest(BaseModel):
    story_id: str
    story_text: str


@router.post("/ai-editor/improve-flow")
async def improve_flow(request: ImproveFlowRequest):
    return await story_enhancement_service.process(
        "ai-editor-advanced",
        request.story_text,
        edit_instruction="Hikayenin akışını iyileştir, geçişleri yumuşat."
    )


@router.post("/ai-editor/enhance-dialogue")
async def enhance_dialogue(request: ImproveFlowRequest):
    return await story_enhancement_service.process(
        "ai-editor-advanced",
        request.story_text,
        edit_instruction="Diyalogları daha doğal ve etkileyici hale getir."
    )


@router.post("/editor/spell-check-enhanced")
async def realtime_spell_check_enhanced(text: str, language: str = "tr"):
    return {"suggestions": await ai_editor_enhanced_service.realtime_spell_check(text, language)}


@router.post("/editor/auto-correct")
async def auto_correct(text: str, corrections: List[Dict]):
    return {"corrected_text": await ai_editor_enhanced_service.auto_correct(text, corrections)}


@router.post("/editor/style-suggestions-enhanced")
async def get_style_suggestions_enhanced(text: str, language: str = "tr"):
    return {"suggestions": await ai_editor_enhanced_service.get_style_suggestions(text, language)}


@router.post("/editor/readability-enhanced")
async def calculate_readability_score_enhanced(text: str, language: str = "tr"):
    return await ai_editor_enhanced_service.calculate_readability_score(text, language)


# ========== AI Asistan ==========
@router.post("/ai-assistant/realtime-suggestions")
async def get_realtime_suggestions(story_text: str, cursor_position: int, context: Optional[str] = None):
    return {"suggestions": await ai_assistant_service.get_realtime_suggestions(story_text, cursor_position, context)}


@router.post("/ai-assistant/auto-complete")
async def auto_complete(partial_text: str, context: Optional[str] = None):
    return {"completed_text": await ai_assistant_service.auto_complete(partial_text, context)}


@router.post("/ai-assistant/ask")
async def ask_question(question: str, story_context: Optional[str] = None, conversation_id: Optional[str] = None):
    return await ai_assistant_service.ask_question(question, story_context, conversation_id)


@router.get("/ai-assistant/writing-tips")
async def get_writing_tips(story_type: str, language: str = "tr"):
    return {"tips": await ai_assistant_service.get_writing_tips(story_type, language)}


# ========== Gelişmiş AI Analiz ==========
@router.get("/stories/{story_id}/analysis/emotion-chart")
async def get_emotion_chart(story_id: str):
    try:
        return await ai_analysis_advanced_service.generate_emotion_chart_data(story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stories/{story_id}/analysis/character-chart")
async def get_character_chart(story_id: str):
    try:
        return await ai_analysis_advanced_service.generate_character_chart_data(story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stories/{story_id}/characters/analyze")
async def analyze_characters(story_id: str):
    try:
        return await ai_features_advanced_service.analyze_characters(story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/ai/themes/suggest")
async def suggest_themes(user_id: Optional[str] = None, limit: int = 5):
    return {"themes": await ai_features_advanced_service.suggest_themes(user_id, limit)}


# ========== Gelişmiş AI Öneriler ==========
@router.get("/recommendations/realtime/{user_id}")
async def get_realtime_recommendations(user_id: str, current_story_id: Optional[str] = None, user_action: Optional[str] = None):
    return {"recommendations": await ai_recommendations_advanced_service.get_realtime_recommendations(user_id, current_story_id, user_action)}


@router.post("/recommendations/record-interaction")
async def record_interaction(user_id: str, story_id: str, interaction_type: str, rating: Optional[float] = None):
    ai_recommendations_advanced_service.record_user_interaction(user_id, story_id, interaction_type, rating)
    return {"message": "Etkileşim kaydedildi"}


# ========== Gelişmiş AI İyileştirme ==========
@router.post("/ai-improvement/realtime-suggestions")
async def get_improvement_suggestions(text: str, cursor_position: int, context: Optional[str] = None):
    return {"suggestions": await ai_improvement_advanced_service.get_realtime_suggestions(text, cursor_position, context)}


# ========== Gelişmiş AI Moderasyon ==========
@router.post("/moderation/realtime-check")
async def realtime_content_check(text: str, content_type: str = "story"):
    return await ai_moderation_advanced_service.realtime_content_check(text, content_type)


@router.post("/moderate-content")
async def moderate(text: str, content_type: str = "story"):
    return await content_moderation_service.moderate_content(text, content_type)
