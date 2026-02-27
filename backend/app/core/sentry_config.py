import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from app.core.config import settings

def init_sentry():
    """
    Initialize Sentry for error tracking.
    """
    print(f"DEBUG: SENTRY_DSN='{settings.SENTRY_DSN}'")
    if not settings.SENTRY_DSN or not settings.SENTRY_DSN.strip():
        return
    
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(),
                CeleryIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% of transactions
            profiles_sample_rate=0.1,
            environment=settings.ENVIRONMENT,
            release=settings.APP_VERSION,
        )
    except Exception as e:
        print(f"Warning: Sentry initialization failed: {e}")

def capture_exception(exception: Exception, context: dict = None):
    """
    Capture exception to Sentry with context.
    """
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_exception(exception)
