from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.services.marketplace_service import MarketplaceService
from app.services.realtime_collaboration_service import RealtimeCollaborationService
from app.services.social_features_service import SocialFeaturesService
from app.services.story_community_features_service import StoryCommunityFeaturesService
from app.services.community_social_advanced_service import CommunitySocialAdvancedService
from app.services.story_storage import StoryStorage
from app.services.story_enhancement_service import StoryEnhancementService

router = APIRouter()

marketplace_service = MarketplaceService()
realtime_collaboration_service = RealtimeCollaborationService()
social_features_service = SocialFeaturesService()
story_community_features_service = StoryCommunityFeaturesService()
community_social_advanced_service = CommunitySocialAdvancedService()
story_storage = StoryStorage()
story_enhancement_service = StoryEnhancementService()

# ========== Pazar Yeri ==========
class ListStoryRequest(BaseModel):
    price: float
    currency: str = "TRY"
    description: Optional[str] = None


@router.post("/marketplace/list")
async def list_story(story_id: str, user_id: str, request: ListStoryRequest):
    try:
        return marketplace_service.list_story_for_sale(story_id, user_id, request.price, request.currency, request.description)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/marketplace/stories")
async def get_marketplace_stories(category: Optional[str] = None, limit: int = 20):
    return {"stories": marketplace_service.get_marketplace_stories(category, None, None, "created_at", limit)}


# ========== Gerçek Zamanlı İşbirliği ==========
@router.post("/stories/{story_id}/collaboration-session")
async def create_session(story_id: str, user_id: str):
    try:
        return realtime_collaboration_service.create_collaboration_session(story_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== Sosyal Özellikler (Temel) ==========
@router.post("/clubs")
async def create_club(name: str, description: str, created_by: str, is_public: bool = True):
    return social_features_service.create_story_club(name, description, created_by, is_public)


@router.get("/challenges/active")
async def get_active_challenges(limit: int = 10):
    return {"challenges": social_features_service.get_active_challenges(limit)}


# ========== Topluluk Özellikleri (Advanced) ==========
@router.post("/contests/create")
async def create_contest(title: str, description: str, theme: str, start_date: str, end_date: str, creator_id: str):
    return community_social_advanced_service.create_contest(title, description, theme, start_date, end_date, creator_id)


@router.post("/contests/{contest_id}/submit")
async def submit_to_contest(contest_id: str, story_id: str, user_id: str):
    return community_social_advanced_service.submit_to_contest(contest_id, story_id, user_id)


@router.post("/templates/community")
async def create_community_template(name: str, content: str, category: str, creator_id: str, is_public: bool = True):
    return community_social_advanced_service.create_community_template(name, content, category, creator_id, is_public)


@router.post("/groups/create")
async def create_story_group(name: str, description: str, creator_id: str, is_public: bool = True):
    return community_social_advanced_service.create_story_group(name, description, creator_id, is_public)


@router.post("/authors/profile")
async def create_author_profile(user_id: str, pen_name: str, bio: Optional[str] = None, social_links: Optional[Dict] = None):
    return community_social_advanced_service.create_author_profile(user_id, pen_name, bio, social_links)


# ========== Topluluk Standart Özellikler ==========
class CommunityRequest(BaseModel):
    creator_id: str
    community_name: str
    description: str
    is_public: bool = True


@router.post("/community/create")
async def create_community(request: CommunityRequest):
    return await story_community_features_service.create_community(
        request.creator_id, request.community_name, request.description, request.is_public
    )


class JoinCommunityRequest(BaseModel):
    community_id: str
    user_id: str


@router.post("/community/join")
async def join_community(request: JoinCommunityRequest):
    return await story_community_features_service.join_community(
        request.community_id, request.user_id
    )


class ShareToCommunityRequest(BaseModel):
    community_id: str
    story_id: str
    user_id: str


@router.post("/community/share-story")
async def share_story_to_community(request: ShareToCommunityRequest):
    return await story_community_features_service.share_story_to_community(
        request.community_id, request.story_id, request.user_id
    )


@router.get("/community/stories/{community_id}")
async def get_community_stories(community_id: str):
    return await story_community_features_service.get_community_stories(community_id)


@router.get("/community/popular")
async def get_popular_communities(limit: int = 10):
    return await story_community_features_service.get_popular_communities(limit)


# ========== Yorum Analizi ==========
class CommentAnalysisRequest(BaseModel):
    story_id: str
    comments: List[str]


@router.post("/comments/analyze")
async def analyze_comments(request: CommentAnalysisRequest):
    comments_text = "\n".join([f"- {c}" for c in request.comments])
    return await story_enhancement_service.process(
        "comment-analysis", "", comments_text=comments_text
    )


class ResponseSuggestionRequest(BaseModel):
    comment: str
    story_context: Optional[str] = None


@router.post("/comments/suggest-response")
async def generate_response_suggestions(request: ResponseSuggestionRequest):
    return await story_enhancement_service.process(
        "comment-response", "", comment=request.comment, story_context=request.story_context
    )


# ========== Viral Özellikler ==========
class ViralContentRequest(BaseModel):
    story_id: str
    story_text: str
    content_type: str = "quote"


@router.post("/viral/create-content")
async def create_viral_content(request: ViralContentRequest):
    return await story_enhancement_service.process(
        "viral-features", request.story_text, content_type=request.content_type
    )


class SharingTrackRequest(BaseModel):
    story_id: str
    platform: str
    user_id: Optional[str] = None


@router.post("/viral/track-sharing")
async def track_sharing(request: SharingTrackRequest):
    # Tracking logic likely DB based. If service deleted, we stub it.
    return {"message": "Sharing tracked (stub)"}


@router.get("/viral/stats/{story_id}")
async def get_viral_stats(story_id: str):
    # Stats logic likely DB based.
    return {"shares": 0, "clicks": 0}


class ShareableImageRequest(BaseModel):
    story_id: str
    quote: str
    style: str = "modern"


@router.post("/viral/shareable-image")
async def create_shareable_image(request: ShareableImageRequest):
    story = story_storage.get_story(request.story_id)
    story_text = story.get('story_text', '') if story else ""

    result = await story_enhancement_service.process(
        "viral-image-prompt", story_text, style=request.style
    )
    # Ideally call image generation service here with result['result']
    return result
