from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.services.education_learning_service import EducationLearningService
from app.services.story_scheduler_service import StorySchedulerService
from app.services.story_automation_service import StoryAutomationService
from app.services.ai_story_creation_advanced_service import AIStoryCreationAdvancedService
from app.services.timeline_service import TimelineService
from app.services.geolocation_service import GeolocationService
from app.services.offline_service import OfflineService
from app.services.story_smart_scheduling_service import StorySmartSchedulingService
from app.services.story_auto_categorization_service import StoryAutoCategorizationService
from app.services.story_content_verification_service import StoryContentVerificationService
from app.services.story_smart_tagging_service import StorySmartTaggingService
from app.services.story_version_control_service import StoryVersionControlService
from app.services.story_content_enrichment_service import StoryContentEnrichmentService
from app.services.story_auto_title_service import StoryAutoTitleService
from app.services.story_content_expansion_service import StoryContentExpansionService
from app.services.story_content_compression_service import StoryContentCompressionService
from app.services.story_resolution_adder_service import StoryResolutionAdderService
from app.services.story_moral_adder_service import StoryMoralAdderService
from app.services.story_entertainment_adder_service import StoryEntertainmentAdderService
from app.services.story_excitement_adder_service import StoryExcitementAdderService
from app.services.story_mystery_adder_service import StoryMysteryAdderService
from app.services.story_romance_adder_service import StoryRomanceAdderService
from app.services.story_ai_rewriter_service import StoryAiRewriterService
from app.services.story_plagiarism_checker_service import StoryPlagiarismCheckerService
from app.services.story_quality_scorer_service import StoryQualityScorerService
from app.services.story_language_simplifier_service import StoryLanguageSimplifierService
from app.services.story_vocabulary_enhancer_service import StoryVocabularyEnhancerService
from app.services.story_rhythm_enhancer_service import StoryRhythmEnhancerService
from app.services.story_pacing_optimizer_service import StoryPacingOptimizerService
from app.services.story_climax_enhancer_service import StoryClimaxEnhancerService
from app.services.story_foreshadowing_adder_service import StoryForeshadowingAdderService
from app.services.story_symbolism_adder_service import StorySymbolismAdderService
from app.services.story_metaphor_enhancer_service import StoryMetaphorEnhancerService
from app.services.story_alliteration_enhancer_service import StoryAlliterationEnhancerService
from app.services.story_repetition_optimizer_service import StoryRepetitionOptimizerService
from app.services.story_transition_enhancer_service import StoryTransitionEnhancerService
from app.services.story_hook_creator_service import StoryHookCreatorService
from app.services.story_theme_enhancer_service import StoryThemeEnhancerService
from app.services.story_imagery_enhancer_service import StoryImageryEnhancerService
from app.services.story_voice_enhancer_service import StoryVoiceEnhancerService
from app.services.story_dialogue_balance_service import StoryDialogueBalanceService
from app.services.story_storage import StoryStorage
from app.services.plagiarism_service import PlagiarismService

router = APIRouter()

education_learning_service = EducationLearningService()
story_scheduler_service = StorySchedulerService()
story_automation_service = StoryAutomationService()
ai_story_creation_advanced_service = AIStoryCreationAdvancedService()
timeline_service = TimelineService()
geolocation_service = GeolocationService()
offline_service = OfflineService()
story_smart_scheduling_service = StorySmartSchedulingService()
story_auto_categorization_service = StoryAutoCategorizationService()
story_content_verification_service = StoryContentVerificationService()
story_smart_tagging_service = StorySmartTaggingService()
story_version_control_service = StoryVersionControlService()
story_content_enrichment_service = StoryContentEnrichmentService()
story_auto_title_service = StoryAutoTitleService()
story_content_expansion_service = StoryContentExpansionService()
story_content_compression_service = StoryContentCompressionService()
story_resolution_adder_service = StoryResolutionAdderService()
story_moral_adder_service = StoryMoralAdderService()
story_entertainment_adder_service = StoryEntertainmentAdderService()
story_excitement_adder_service = StoryExcitementAdderService()
story_mystery_adder_service = StoryMysteryAdderService()
story_romance_adder_service = StoryRomanceAdderService()
story_ai_rewriter_service = StoryAiRewriterService()
story_plagiarism_checker_service = StoryPlagiarismCheckerService()
story_quality_scorer_service = StoryQualityScorerService()
story_language_simplifier_service = StoryLanguageSimplifierService()
story_vocabulary_enhancer_service = StoryVocabularyEnhancerService()
story_rhythm_enhancer_service = StoryRhythmEnhancerService()
story_pacing_optimizer_service = StoryPacingOptimizerService()
story_climax_enhancer_service = StoryClimaxEnhancerService()
story_foreshadowing_adder_service = StoryForeshadowingAdderService()
story_symbolism_adder_service = StorySymbolismAdderService()
story_metaphor_enhancer_service = StoryMetaphorEnhancerService()
story_alliteration_enhancer_service = StoryAlliterationEnhancerService()
story_repetition_optimizer_service = StoryRepetitionOptimizerService()
story_transition_enhancer_service = StoryTransitionEnhancerService()
story_hook_creator_service = StoryHookCreatorService()
story_theme_enhancer_service = StoryThemeEnhancerService()
story_imagery_enhancer_service = StoryImageryEnhancerService()
story_voice_enhancer_service = StoryVoiceEnhancerService()
story_dialogue_balance_service = StoryDialogueBalanceService()
story_storage = StoryStorage()
plagiarism_service = PlagiarismService()


# ========== Eğitim ve Öğrenme ==========
@router.get("/stories/{story_id}/reading-level")
async def analyze_reading_level(story_id: str):
    story = story_storage.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    return await education_learning_service.analyze_reading_level(story.get('story_text', ''), story.get('language', 'tr'))


@router.get("/stories/{story_id}/vocabulary")
async def extract_vocabulary(story_id: str, difficulty_level: str = "medium"):
    story = story_storage.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    return await education_learning_service.extract_vocabulary(story.get('story_text', ''), difficulty_level)


@router.post("/stories/educational")
async def generate_educational_story(topic: str, age_group: str, educational_goal: str, language: str = "tr"):
    return await education_learning_service.generate_educational_story(topic, age_group, educational_goal, language)


# ========== Hikâye Planlayıcı (Temel) ==========
class ScheduleRequest(BaseModel):
    publish_at: str
    auto_publish: bool = True


@router.post("/stories/{story_id}/schedule")
async def schedule_story(story_id: str, user_id: str, request: ScheduleRequest):
    try:
        return story_scheduler_service.schedule_story_publication(story_id, user_id, request.publish_at, request.auto_publish)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== Otomasyon ==========
class AutomationRequest(BaseModel):
    automation_type: str
    trigger: Dict
    action: Dict


@router.post("/automations")
async def create_automation(user_id: str, request: AutomationRequest):
    return story_automation_service.create_automation(user_id, request.automation_type, request.trigger, request.action)


@router.get("/users/{user_id}/automations")
async def get_user_automations(user_id: str):
    return {"automations": story_automation_service.get_user_automations(user_id)}


# ========== AI Story Creation Advanced ==========
@router.post("/stories/multi-character")
async def create_multi_character_story(theme: str, characters: List[Dict], language: str = "tr", story_type: str = "masal"):
    return await ai_story_creation_advanced_service.create_multi_character_story(theme, characters, language, story_type)


@router.post("/stories/{story_id}/parallel-universe")
async def create_parallel_universe(story_id: str, universe_name: str, divergence_point: str):
    return await ai_story_creation_advanced_service.create_parallel_universe(story_id, universe_name, divergence_point)


@router.post("/series/create")
async def create_story_series(series_name: str, description: str, user_id: str):
    return ai_story_creation_advanced_service.create_story_series(series_name, description, user_id)


@router.post("/stories/{story_id}/auto-continue")
async def auto_continue_story(story_id: str, continuation_length: str = "medium"):
    return await ai_story_creation_advanced_service.auto_continue_story(story_id, continuation_length)


# ========== Zaman Çizelgesi ==========
@router.get("/stories/{story_id}/timeline")
async def get_timeline(story_id: str):
    try:
        return await timeline_service.generate_timeline(story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== Coğrafi Konum ==========
class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    region: Optional[str] = None


@router.post("/stories/{story_id}/location")
async def set_location(story_id: str, request: LocationRequest):
    return geolocation_service.set_story_location(story_id, request.latitude, request.longitude, request.location_name, request.region)


@router.get("/stories/nearby")
async def get_nearby_stories(latitude: float, longitude: float, radius_km: float = 10.0, limit: int = 10):
    return {"stories": geolocation_service.get_nearby_stories(latitude, longitude, radius_km, limit)}


# ========== Offline Mod ==========
@router.post("/stories/{story_id}/mark-offline")
async def mark_offline(story_id: str, user_id: str):
    try:
        return offline_service.mark_story_for_offline(user_id, story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/users/{user_id}/offline-stories")
async def get_offline_stories(user_id: str):
    return {"stories": offline_service.get_offline_stories(user_id)}


# ========== Akıllı Zamanlama (Advanced) ==========
class SmartReminderRequest(BaseModel):
    user_id: str
    task_description: str
    priority: str = "medium"


@router.post("/scheduling/create-reminder")
async def create_smart_reminder(request: SmartReminderRequest):
    return await story_smart_scheduling_service.create_smart_reminder(
        request.user_id, request.task_description, request.priority
    )


class StoryScheduleRequest(BaseModel):
    user_id: str
    theme: str
    preferred_time: Optional[str] = None


@router.post("/scheduling/schedule-story")
async def schedule_story_creation(request: StoryScheduleRequest):
    return await story_smart_scheduling_service.schedule_story_creation(
        request.user_id, request.theme, request.preferred_time
    )


@router.get("/scheduling/upcoming/{user_id}")
async def get_upcoming_reminders(user_id: str, hours_ahead: int = 24):
    return await story_smart_scheduling_service.get_upcoming_reminders(
        user_id, hours_ahead
    )


# ========== Otomatik Kategorizasyon ==========
class CategorizationRequest(BaseModel):
    story_id: str
    story_text: str


@router.post("/categorization/categorize")
async def categorize_story(request: CategorizationRequest):
    return await story_auto_categorization_service.categorize_story(
        request.story_id, request.story_text
    )


@router.get("/categorization/similar/{story_id}")
async def get_similar_stories(story_id: str, limit: int = 5):
    return await story_auto_categorization_service.get_similar_stories(
        story_id, limit
    )


# ========== İçerik Doğrulama ==========
class VerificationRequest(BaseModel):
    story_id: str
    story_text: str
    verification_type: str = "comprehensive"


@router.post("/verification/verify")
async def verify_content(request: VerificationRequest):
    return await story_content_verification_service.verify_content(
        request.story_id, request.story_text, request.verification_type
    )


# ========== Akıllı Etiketleme ==========
class TaggingRequest(BaseModel):
    story_id: str
    story_text: str


@router.post("/tagging/auto-tag")
async def auto_tag_story(request: TaggingRequest):
    return await story_smart_tagging_service.auto_tag_story(
        request.story_id, request.story_text
    )


class TagSuggestionRequest(BaseModel):
    story_text: str
    existing_tags: Optional[List[str]] = None


@router.post("/tagging/suggest")
async def suggest_tags(request: TagSuggestionRequest):
    return await story_smart_tagging_service.suggest_tags(
        request.story_text, request.existing_tags
    )


@router.get("/tagging/popular")
async def get_popular_tags(limit: int = 20):
    return await story_smart_tagging_service.get_popular_tags(limit)


# ========== Versiyon Kontrolü ==========
class VersionRequest(BaseModel):
    story_id: str
    story_text: str
    version_name: Optional[str] = None
    description: Optional[str] = None


@router.post("/version/create")
async def create_version(request: VersionRequest):
    return await story_version_control_service.create_version(
        request.story_id, request.story_text, request.version_name, request.description
    )


@router.get("/version/history/{story_id}")
async def get_version_history(story_id: str):
    return await story_version_control_service.get_version_history(story_id)


class RestoreVersionRequest(BaseModel):
    story_id: str
    version_id: str


@router.post("/version/restore")
async def restore_version(request: RestoreVersionRequest):
    return await story_version_control_service.restore_version(
        request.story_id, request.version_id
    )


class CompareVersionsRequest(BaseModel):
    story_id: str
    version1_id: str
    version2_id: str


@router.post("/version/compare")
async def compare_versions(request: CompareVersionsRequest):
    return await story_version_control_service.compare_versions(
        request.story_id, request.version1_id, request.version2_id
    )


# ========== İçerik Zenginleştirme ==========
class EnrichmentRequest(BaseModel):
    story_id: str
    story_text: str
    enrichment_type: str = "descriptive"


@router.post("/enrichment/enrich")
async def enrich_story(request: EnrichmentRequest):
    return await story_content_enrichment_service.enrich_story(
        request.story_id, request.story_text, request.enrichment_type
    )


class SensoryDetailsRequest(BaseModel):
    story_id: str
    story_text: str


@router.post("/enrichment/sensory-details")
async def add_sensory_details(request: SensoryDetailsRequest):
    return await story_content_enrichment_service.add_sensory_details(
        request.story_id, request.story_text
    )


# ========== Otomatik Başlık ==========
class TitleGenerationRequest(BaseModel):
    story_id: str
    story_text: str
    num_titles: int = 5
    title_style: str = "creative"


@router.post("/title/generate")
async def generate_titles(request: TitleGenerationRequest):
    return await story_auto_title_service.generate_titles(
        request.story_id, request.story_text, request.num_titles, request.title_style
    )


class TitleOptimizationRequest(BaseModel):
    current_title: str
    story_text: str


@router.post("/title/optimize")
async def optimize_title(request: TitleOptimizationRequest):
    return await story_auto_title_service.optimize_title(
        request.current_title, request.story_text
    )


# ========== İçerik Genişletme ==========
class ExpansionRequest(BaseModel):
    story_id: str
    story_text: str
    expansion_type: str = "general"
    target_length: Optional[int] = None


@router.post("/expansion/expand")
async def expand_story(request: ExpansionRequest):
    return await story_content_expansion_service.expand_story(
        request.story_id, request.story_text, request.expansion_type, request.target_length
    )


class AddChapterRequest(BaseModel):
    story_id: str
    story_text: str
    chapter_theme: str


@router.post("/expansion/add-chapter")
async def add_chapter(request: AddChapterRequest):
    return await story_content_expansion_service.add_chapter(
        request.story_id, request.story_text, request.chapter_theme
    )


# ========== İçerik Sıkıştırma ==========
class CompressionRequest(BaseModel):
    story_id: str
    story_text: str
    compression_ratio: float = 0.5


@router.post("/compression/compress")
async def compress_story(request: CompressionRequest):
    return await story_content_compression_service.compress_story(
        request.story_id, request.story_text, request.compression_ratio
    )


class ShortVersionRequest(BaseModel):
    story_id: str
    story_text: str
    max_words: int = 100


@router.post("/compression/short-version")
async def create_short_version(request: ShortVersionRequest):
    return await story_content_compression_service.create_short_version(
        request.story_id, request.story_text, request.max_words
    )


# ========== Çözümleme Ekleme ==========
class ResolutionAddRequest(BaseModel):
    story_id: str
    story_text: str
    resolution_type: str


@router.post("/resolution/add")
async def add_resolution(request: ResolutionAddRequest):
    return await story_resolution_adder_service.add_resolution(
        request.story_id, request.story_text, request.resolution_type
    )


# ========== Ders Ekleme ==========
class MoralAddRequest(BaseModel):
    story_id: str
    story_text: str
    moral_theme: Optional[str] = None


@router.post("/moral/add")
async def add_moral(request: MoralAddRequest):
    return await story_moral_adder_service.add_moral(
        request.story_id, request.story_text, request.moral_theme
    )


# ========== Eğlence Ekleme ==========
class EntertainmentAddRequest(BaseModel):
    story_id: str
    story_text: str
    entertainment_type: str


@router.post("/entertainment/add")
async def add_entertainment(request: EntertainmentAddRequest):
    return await story_entertainment_adder_service.add_entertainment(
        request.story_id, request.story_text, request.entertainment_type
    )


# ========== Heyecan Ekleme ==========
class ExcitementAddRequest(BaseModel):
    story_id: str
    story_text: str
    excitement_level: str


@router.post("/excitement/add")
async def add_excitement(request: ExcitementAddRequest):
    return await story_excitement_adder_service.add_excitement(
        request.story_id, request.story_text, request.excitement_level
    )


# ========== Gizem Ekleme ==========
class MysteryAddRequest(BaseModel):
    story_id: str
    story_text: str
    mystery_type: str


@router.post("/mystery/add")
async def add_mystery(request: MysteryAddRequest):
    return await story_mystery_adder_service.add_mystery(
        request.story_id, request.story_text, request.mystery_type
    )


# ========== Romantizm Ekleme ==========
class RomanceAddRequest(BaseModel):
    story_id: str
    story_text: str
    romance_level: str


@router.post("/romance/add")
async def add_romance(request: RomanceAddRequest):
    return await story_romance_adder_service.add_romance(
        request.story_id, request.story_text, request.romance_level
    )


# ========== AI Yeniden Yazma ==========
class RewriteRequest(BaseModel):
    story_id: str
    story_text: str
    rewrite_style: str = "improved"


@router.post("/rewriter/rewrite")
async def rewrite_story(request: RewriteRequest):
    return await story_ai_rewriter_service.rewrite_story(
        request.story_id, request.story_text, request.rewrite_style
    )


# ========== Intihal Kontrolü (Advanced & Basic) ==========
class PlagiarismCheckRequest(BaseModel):
    story_id: str
    story_text: str


@router.post("/plagiarism/check")
async def check_plagiarism_advanced(request: PlagiarismCheckRequest):
    return await story_plagiarism_checker_service.check_plagiarism(
        request.story_id, request.story_text
    )


@router.post("/stories/{story_id}/check-plagiarism")
async def check_plagiarism_basic(story_id: str):
    story = story_storage.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Hikâye bulunamadı")
    return await plagiarism_service.check_plagiarism(story.get('story_text', ''), story_id)


# ========== Kalite Skorlama ==========
@router.post("/quality/score")
async def score_story(request: PlagiarismCheckRequest):
    return await story_quality_scorer_service.score_story(
        request.story_id, request.story_text
    )


# ========== Dil Basitleştirme ==========
class SimplifyRequest(BaseModel):
    story_id: str
    story_text: str
    target_age: int = 7


@router.post("/language/simplify")
async def simplify_language(request: SimplifyRequest):
    return await story_language_simplifier_service.simplify_language(
        request.story_id, request.story_text, request.target_age
    )


# ========== Kelime Hazinesi Geliştirme ==========
class VocabularyRequest(BaseModel):
    story_id: str
    story_text: str
    enhancement_level: str = "moderate"


@router.post("/vocabulary/enhance")
async def enhance_vocabulary(request: VocabularyRequest):
    return await story_vocabulary_enhancer_service.enhance_vocabulary(
        request.story_id, request.story_text, request.enhancement_level
    )


# ========== Ritim Geliştirme ==========
@router.post("/rhythm/enhance")
async def enhance_rhythm(request: PlagiarismCheckRequest):
    return await story_rhythm_enhancer_service.enhance_rhythm(
        request.story_id, request.story_text
    )


# ========== Tempo Optimizasyonu ==========
class PacingRequest(BaseModel):
    story_id: str
    story_text: str
    pacing_type: str = "balanced"


@router.post("/pacing/optimize")
async def optimize_pacing(request: PacingRequest):
    return await story_pacing_optimizer_service.optimize_pacing(
        request.story_id, request.story_text, request.pacing_type
    )


# ========== Doruk Noktası Geliştirme ==========
@router.post("/climax/enhance")
async def enhance_climax(request: PlagiarismCheckRequest):
    return await story_climax_enhancer_service.enhance_climax(
        request.story_id, request.story_text
    )


# ========== Önsezi Ekleme ==========
@router.post("/foreshadowing/add")
async def add_foreshadowing(request: PlagiarismCheckRequest):
    return await story_foreshadowing_adder_service.add_foreshadowing(
        request.story_id, request.story_text
    )


# ========== Sembolizm Ekleme ==========
@router.post("/symbolism/add")
async def add_symbolism(request: PlagiarismCheckRequest):
    return await story_symbolism_adder_service.add_symbolism(
        request.story_id, request.story_text
    )


# ========== Metafor Geliştirme ==========
@router.post("/metaphor/enhance")
async def enhance_metaphors(request: PlagiarismCheckRequest):
    return await story_metaphor_enhancer_service.enhance_metaphors(
        request.story_id, request.story_text
    )


# ========== Aliterasyon Geliştirme ==========
@router.post("/alliteration/enhance")
async def enhance_alliteration(request: PlagiarismCheckRequest):
    return await story_alliteration_enhancer_service.enhance_alliteration(
        request.story_id, request.story_text
    )


# ========== Tekrar Optimizasyonu ==========
@router.post("/repetition/optimize")
async def optimize_repetition(request: PlagiarismCheckRequest):
    return await story_repetition_optimizer_service.optimize_repetition(
        request.story_id, request.story_text
    )


# ========== Geçiş Geliştirme ==========
@router.post("/transition/enhance")
async def enhance_transitions(request: PlagiarismCheckRequest):
    return await story_transition_enhancer_service.enhance_transitions(
        request.story_id, request.story_text
    )


# ========== Kanca Oluşturma ==========
class HookRequest(BaseModel):
    story_id: str
    story_text: str
    hook_type: str = "question"


@router.post("/hook/create")
async def create_hook(request: HookRequest):
    return await story_hook_creator_service.create_hook(
        request.story_id, request.story_text, request.hook_type
    )


# ========== Tema Geliştirme ==========
class ThemeEnhanceRequest(BaseModel):
    story_id: str
    story_text: str
    theme: Optional[str] = None


@router.post("/theme/enhance")
async def enhance_theme(request: ThemeEnhanceRequest):
    return await story_theme_enhancer_service.enhance_theme(
        request.story_id, request.story_text, request.theme
    )


# ========== Görsel Betimleme Geliştirme ==========
@router.post("/imagery/enhance")
async def enhance_imagery(request: PlagiarismCheckRequest):
    return await story_imagery_enhancer_service.enhance_imagery(
        request.story_id, request.story_text
    )


# ========== Ses Geliştirme ==========
class VoiceRequest(BaseModel):
    story_id: str
    story_text: str
    voice_style: str = "distinctive"


@router.post("/voice/enhance")
async def enhance_voice(request: VoiceRequest):
    return await story_voice_enhancer_service.enhance_voice(
        request.story_id, request.story_text, request.voice_style
    )


# ========== Diyalog Dengesi ==========
class DialogueBalanceRequest(BaseModel):
    story_id: str
    story_text: str
    dialogue_ratio: float = 0.3


@router.post("/dialogue/balance")
async def balance_dialogue(request: DialogueBalanceRequest):
    return await story_dialogue_balance_service.balance_dialogue(
        request.story_id, request.story_text, request.dialogue_ratio
    )
