import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import os

def init_sentry():
    """Initialize Sentry for error tracking."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("SENTRY_ENVIRONMENT", "development")
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            integrations=[
                FastApiIntegration(),
                RedisIntegration(),
            ],
            # Performance monitoring
            traces_sample_rate=0.1,  # 10% of transactions
            # Error sampling
            sample_rate=1.0,  # 100% of errors
            # Release tracking
            release=os.getenv("APP_VERSION", "1.0.0"),
            # Additional context
            before_send=before_send_filter,
        )
        print(f"✅ Sentry initialized for {environment}")
    else:
        print("⚠️  Sentry DSN not found, error tracking disabled")

def before_send_filter(event, hint):
    """Filter events before sending to Sentry."""
    # Don't send health check errors
    if 'request' in event:
        url = event['request'].get('url', '')
        if '/health' in url:
            return None
    
    # Add custom tags
    event.setdefault('tags', {})
    event['tags']['app'] = 'masal-fabrikasi'
    
    return event

# Export
__all__ = ['init_sentry']
