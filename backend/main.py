from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
from dotenv import load_dotenv
import os

from app.routers import story, health, character, user, achievement, leaderboard, challenge, quiz, analytics, social, media, ai_tools, story_features, story_advanced_features, user_features, platform, education, market, collaboration, vision, voice_cloning, parental, shop, metrics_router
from app.routers import auth_router, gdpr_router
from app.core.config import settings
from app.services.cloud_storage_service import cloud_storage_service
from contextlib import asynccontextmanager

# Import exception handlers and middleware
from app.core.exceptions import MasalFabrikasiException
from app.core.exception_handlers import (
    masalfabrikasi_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from app.middleware.request_tracking import RequestTrackingMiddleware

load_dotenv()

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from app.core.logging_config import setup_logging
from app.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.core.sentry_config import init_sentry
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Initialize Sentry
init_sentry()

# Setup structured logging
from app.core.logging import setup_logging
logger = setup_logging(
    level="INFO" if not settings.DEBUG else "DEBUG",
    use_json=not settings.DEBUG  # JSON in production, readable in dev
)

load_dotenv()

# Validate environment on startup
from app.core.env_validator import validate_environment
validate_environment()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Bucketları kontrol et ve oluştur
    if settings.USE_CLOUD_STORAGE:
        await cloud_storage_service.initialize_buckets()
    yield
    # Shutdown logic (varsa)

app = FastAPI(
    lifespan=lifespan,
    title="Masal Fabrikası AI",
    description="""
    ## 🎭 Masal Fabrikası AI - 500+ Özellikli Hikaye Üretim Platformu
    
    AI destekli kapsamlı hikaye üretim, düzenleme ve yönetim servisi.
    
    ### 🚀 Özellikler
    
    - **500+ Farklı Özellik**: Hikaye geliştirme, analiz, optimizasyon ve dönüştürme
    - **AI Destekli Üretim**: OpenAI GPT-4 ile hikaye, görsel ve ses üretimi
    - **Gelişmiş Analiz**: Okunabilirlik, karmaşıklık, duygusal etki analizi
    - **Karakter Geliştirme**: Derin karakter analizi ve geliştirme araçları
    - **Dünya Yaratma**: Detaylı dünya kurma ve yönetim sistemleri
    - **Olay Örgüsü**: Karmaşık olay örgüsü oluşturma ve analiz
    - **Diyalog Optimizasyonu**: Doğal ve etkili diyalog geliştirme
    - **Betimleme Zenginleştirme**: Canlı ve duyusal betimlemeler
    - **Eğitsel Özellikler**: Değer öğretme, beceri geliştirme
    - **Eğlence Özellikleri**: Etkileşim, oyunculuk, merak uyandırma
    
    ### 📚 API Dokümantasyonu
    
    - **Swagger UI**: `/docs` - İnteraktif API dokümantasyonu
    - **ReDoc**: `/redoc` - Alternatif dokümantasyon görünümü
    
    ### 🧪 Test
    
    ```bash
    pytest                    # Tüm testler
    pytest -m unit           # Unit testler
    pytest -m integration    # Integration testler
    pytest --cov=app         # Coverage raporu
    ```
    """,
    version="2.0.0",
    contact={
        "name": "Masal Fabrikası AI",
        "email": "support@masalfabrikasi.ai",
    },
    license_info={
        "name": "MIT",
    },
)

# Register Exception Handlers
app.add_exception_handler(MasalFabrikasiException, masalfabrikasi_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add Request Tracking Middleware
app.add_middleware(RequestTrackingMiddleware)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
from app.middleware.pagination_middleware import PaginationEnforcementMiddleware
app.add_middleware(PaginationEnforcementMiddleware)

# CORS yapılandırması
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static dosyalar için mount (görseller, ses dosyaları ve export dosyaları)
if os.path.exists(settings.STORAGE_PATH):
    app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")

# Router'ları ekle
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(gdpr_router.router, prefix="/api/gdpr", tags=["GDPR Compliance"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(story.router, prefix="/api", tags=["Story"])
app.include_router(character.router, prefix="/api", tags=["Character"])
app.include_router(user.router, prefix="/api", tags=["User"])
# app.include_router(achievement.router, prefix="/api", tags=["Achievement"]) # Moved to Gamification
# app.include_router(leaderboard.router, prefix="/api", tags=["Leaderboard"]) # Moved to Gamification
app.include_router(challenge.router, prefix="/api", tags=["Challenge"])
app.include_router(quiz.router, prefix="/api", tags=["Quiz"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(social.router, prefix="/api", tags=["Social"])
app.include_router(media.router, prefix="/api", tags=["Media"])
app.include_router(ai_tools.router, prefix="/api", tags=["AI Tools"])
app.include_router(story_features.router, prefix="/api", tags=["Story Features"])
app.include_router(story_advanced_features.router, prefix="/api", tags=["Story Advanced Analysis"])
app.include_router(user_features.router, prefix="/api", tags=["User Features"])
app.include_router(platform.router, prefix="/api", tags=["Platform"])
app.include_router(education.router, prefix="/api", tags=["Education"])
app.include_router(market.router, prefix="/api", tags=["Market"])
app.include_router(collaboration.router, prefix="/api", tags=["Collaboration"])
app.include_router(vision.router, prefix="/api", tags=["Vision / Magic Canvas"])
app.include_router(voice_cloning.router, prefix="/api/voice-cloning", tags=["Voice Cloning"])
app.include_router(parental.router, prefix="/api/parental", tags=["Parental Control"])
app.include_router(shop.router, prefix="/api/shop", tags=["Avatar & Shop"])

# Import Stripe router
from app.routers import stripe_router
app.include_router(stripe_router.router, prefix="/api/stripe", tags=["Payments"])

# Import IAP router
from app.routers import iap_router
app.include_router(iap_router.router, prefix="/api/iap", tags=["In-App Purchases"])

# Import Notification router
from app.routers import notification_router
app.include_router(notification_router.router, prefix="/api/notifications", tags=["Notifications"])

# Import Admin router
from app.routers import admin_router
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin Operations"])

# Import Referral router
from app.routers import referral_router
app.include_router(referral_router.router, prefix="/api/referral", tags=["Referral System"])

# Import Gamification router
from app.routers import gamification_router
app.include_router(gamification_router.router, prefix="/api/gamification", tags=["Gamification"])

# Import AI Tools router
from app.routers import ai_tools_router
app.include_router(ai_tools_router.router, prefix="/api/ai-tools", tags=["AI Tools"])

# Import Interactive Story router
from app.routers import interactive_router
app.include_router(interactive_router.router, prefix="/api/interactive", tags=["Interactive Story"])

# Import Parental router
from app.routers import parental_router
app.include_router(parental_router.router, prefix="/api/parental", tags=["Parental Dashboard"])

# Import Community router
from app.routers import community_router
app.include_router(community_router.router, prefix="/api/community", tags=["Community Library"])

# Mount Socket.IO
from app.core.socket_manager import socket_manager
app.mount("/ws", socket_manager.app)

# Import Magic Canvas Router
from app.routers import magic_canvas_router
app.include_router(magic_canvas_router.router, prefix="/api/tools", tags=["Magic Canvas"])

# Import Character Chat Router
from app.routers import character_chat_router
app.include_router(character_chat_router.router, prefix="/api/chat", tags=["Character Chat"])

# Import Smart Room Router
from app.routers import smart_room_router
app.include_router(smart_room_router.router, prefix="/api/smart-room", tags=["Smart Room"])

# Import Subscription Router
from app.routers import subscription_router
app.include_router(subscription_router.router, prefix="/api/subscription", tags=["Subscription"])

# Import Bedtime Router
from app.routers import bedtime_router
app.include_router(bedtime_router.router, prefix="/api/bedtime", tags=["Bedtime Mode"])

# Import Value Features Router (Cost-Free Legendary Features)
from app.routers import value_features_router
app.include_router(value_features_router.router, prefix="/api/value", tags=["Value Features"])

# Import Growth router
from app.routers import growth
app.include_router(growth.router, prefix="/api/growth", tags=["Growth & Waitlist"])

# Import Metrics Router
app.include_router(metrics_router.router, tags=["Monitoring"])


@app.get("/")
async def root():
    return {"message": "Masal Fabrikası AI API", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )

