from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
import secrets


class Settings(BaseSettings):
    # ============================================
    # MULTI-PROVIDER AI CONFIGURATION
    # Optimized for cost/performance balance
    # ============================================
    
    # Draft & Brainstorm - Google Gemini Flash (cheap, fast)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "google/gemini-3-flash")
    
    # Final Story - GPT OSS 20B (quality + good f/p)
    GPT_API_KEY: str = os.getenv("GPT_API_KEY", "")
    GPT_BASE_URL: str = os.getenv("GPT_BASE_URL", "https://api.wiro.ai/v1")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "openai/gpt-oss-20b")
    
    # Embeddings - Semantic Search (Gemini)
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    
    # STT - Speech to Text (Whisper Turkish)
    STT_API_KEY: str = os.getenv("STT_API_KEY", "")
    STT_BASE_URL: str = os.getenv("STT_BASE_URL", "https://api.wiro.ai/v1")
    STT_MODEL: str = os.getenv("STT_MODEL", "openai/whisper-large-v3-turbo-turkish")
    
    # Images - Google Imagen
    IMAGEN_API_KEY: str = os.getenv("IMAGEN_API_KEY", "")
    IMAGEN_FAST_MODEL: str = os.getenv("IMAGEN_FAST_MODEL", "google/imagen-v4-fast")
    IMAGEN_ULTRA_MODEL: str = os.getenv("IMAGEN_ULTRA_MODEL", "google/imagen-v4-ultra")
    TTS_FORMAT: str = os.getenv("TTS_FORMAT", "mp3_22050_32")
    
    # Video - Wiro Veo3
    VIDEO_MODEL: str = os.getenv("VIDEO_MODEL", "google/veo3-fast")
    VIDEO_RESOLUTION: str = os.getenv("VIDEO_RESOLUTION", "720p")
    VIDEO_DURATION: int = int(os.getenv("VIDEO_DURATION", "8"))
    
    # Wiro Specific (for HMAC signed requests)
    WIRO_API_KEY: str = os.getenv("WIRO_API_KEY", "")
    WIRO_API_SECRET: str = os.getenv("WIRO_API_SECRET", "")
    
    # Legacy OpenAI support (backward compatibility)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.wiro.ai/v1")
    
    # Hugging Face
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # ElevenLabs (Voice Cloning)
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Database (PostgreSQL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://masal_user:masal_pass@localhost:5432/masal_fabrikasi"
    )
    
    # Redis (for Celery and caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Supabase (Auth & Storage)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Backend
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # CORS
    cors_origins_raw: str = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:8081"
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [s.strip() for s in self.cors_origins_raw.split(",") if s.strip()]
    
    # Storage (for temporary files)
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    
    # Feature Flags
    USE_ASYNC_JOBS: bool = os.getenv("USE_ASYNC_JOBS", "true").lower() == "true"
    USE_CLOUD_STORAGE: bool = os.getenv("USE_CLOUD_STORAGE", "true").lower() == "true"  # Renamed from USE_CLOUDINARY
    
    # Rate Limiting
    RATE_LIMIT_FREE_TIER: int = int(os.getenv("RATE_LIMIT_FREE_TIER", "5"))
    RATE_LIMIT_PREMIUM_TIER: int = int(os.getenv("RATE_LIMIT_PREMIUM_TIER", "50"))
    RATE_LIMIT_PRO_TIER: int = int(os.getenv("RATE_LIMIT_PRO_TIER", "500"))
    
    # Stripe (Payments)
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Stripe Price IDs (Optional: can also be fetched dynamically or hardcoded)
    STRIPE_PRICE_ID_PREMIUM_MONTHLY: str = os.getenv("STRIPE_PRICE_ID_PREMIUM_MONTHLY", "")
    STRIPE_PRICE_ID_PRO_MONTHLY: str = os.getenv("STRIPE_PRICE_ID_PRO_MONTHLY", "")
    
    # Sentry (Error Tracking)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    
    # Security
    # CRITICAL: Generate a secure random key for production!
    # Run: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

    # Email Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

# Storage klasörlerini oluştur (geçici dosyalar için)
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
os.makedirs(f"{settings.STORAGE_PATH}/images", exist_ok=True)
os.makedirs(f"{settings.STORAGE_PATH}/audio", exist_ok=True)
os.makedirs(f"{settings.STORAGE_PATH}/video", exist_ok=True)
os.makedirs(f"{settings.STORAGE_PATH}/exports", exist_ok=True)
os.makedirs(f"{settings.STORAGE_PATH}/temp", exist_ok=True)
