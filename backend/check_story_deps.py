
import sys
import os
import traceback
import importlib

sys.path.append(os.getcwd())

services = [
    ("app.services.story_service", "StoryService"),
    ("app.services.image_service", "ImageService"),
    ("app.services.tts_service", "TTSService"),
    ("app.services.story_storage", "StoryStorage"),
    ("app.services.story_editor", "StoryEditor"),
    ("app.services.multi_image_service", "MultiImageService"),
    ("app.services.statistics_service", "StatisticsService"),
    ("app.services.template_service", "TemplateService"),
    ("app.services.collection_service", "CollectionService"),
    ("app.services.export_service", "ExportService"),
    ("app.services.interactive_story_service", "InteractiveStoryService"),
    ("app.services.translation_service", "TranslationService"),
    ("app.services.user_profile_service", "UserProfileService"),
    ("app.services.dialogue_service", "DialogueService"),
    ("app.services.character_service", "CharacterService"),
    ("app.services.story_outline_service", "StoryOutlineService"),
    ("app.services.comment_service", "CommentService"),
    ("app.services.like_service", "LikeService"),
    ("app.services.collaboration_service", "CollaborationService"),
    ("app.services.voice_acting_service", "VoiceActingService"),
    ("app.services.sound_effect_service", "SoundEffectService"),
    ("app.services.story_versioning_service", "StoryVersioningService"),
    ("app.services.story_analysis_service", "StoryAnalysisService"),
    ("app.services.recommendation_service", "RecommendationService"),
    ("app.services.music_service", "MusicService"),
    ("app.services.story_comparison_service", "StoryComparisonService"),
    ("app.services.community_service", "CommunityService"),
    ("app.services.search_service", "SearchService"),
    ("app.services.analytics_service", "AnalyticsService"),
    ("app.services.story_series_service", "StorySeriesService"),
    ("app.services.story_improvement_service", "StoryImprovementService"),
    ("app.services.parental_control_service", "ParentalControlService"),
    ("app.services.audio_recording_service", "AudioRecordingService"),
    ("app.services.sharing_service", "SharingService"),
    ("app.services.ebook_service", "EbookService"),
    ("app.services.performance_metrics_service", "PerformanceMetricsService"),
    ("app.services.ai_chatbot_service", "AIChatbotService"),
    ("app.services.advanced_translation_service", "AdvancedTranslationService"),
    ("app.services.voice_command_service", "VoiceCommandService"),
    ("app.services.marketplace_service", "MarketplaceService"),
    ("app.services.realtime_collaboration_service", "RealtimeCollaborationService"),
    ("app.services.advanced_analytics_service", "AdvancedAnalyticsService"),
    ("app.services.social_features_service", "SocialFeaturesService"),
    # ("app.services.story_scheduler_service", "StorySchedulerService"),
    ("app.services.content_moderation_service", "ContentModerationService"),
    ("app.services.plagiarism_service", "PlagiarismService"),
    ("app.services.story_rating_service", "StoryRatingService"),
    ("app.services.curated_collections_service", "CuratedCollectionsService"),
    ("app.services.reading_goals_service", "ReadingGoalsService"),
    ("app.services.mood_recommendation_service", "MoodRecommendationService"),
    ("app.services.advanced_export_service", "AdvancedExportService"),
    ("app.services.platform_integration_service", "PlatformIntegrationService"),
    ("app.services.api_webhook_service", "APIWebhookService"),
    ("app.services.template_marketplace_service", "TemplateMarketplaceService"),
    ("app.services.voice_story_creation_service", "VoiceStoryCreationService"),
    ("app.services.ar_vr_service", "ARVRService"),
    ("app.services.timeline_service", "TimelineService"),
    ("app.services.geolocation_service", "GeolocationService"),
    ("app.services.backup_sync_service", "BackupSyncService"),
    ("app.services.filter_service", "FilterService"),
    ("app.services.reporting_service", "ReportingService"),
    ("app.services.offline_service", "OfflineService"),
]

print("🔍 Checking Story Services Instantiation...")

for module_name, class_name in services:
    print(f"👉 Checking {class_name} ({module_name})...", end=" ", flush=True)
    try:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        instance = cls()
        print("✅ OK")
    except Exception as e:
        print("❌ FAILED")
        print(f"\nCRITICAL ERROR in {class_name}:")
        traceback.print_exc()
        break
