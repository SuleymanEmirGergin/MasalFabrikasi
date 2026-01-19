import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from app.core.config import settings

def before_send(event, hint):
    """
    Scrub sensitive data from Sentry events.
    """
    if 'request' in event:
        request = event['request']
        if 'headers' in request:
            # Scrub Authorization header
            if 'Authorization' in request['headers']:
                request['headers']['Authorization'] = '[SCRUBBED]'
            if 'authorization' in request['headers']:
                request['headers']['authorization'] = '[SCRUBBED]'

            # Scrub Cookie header
            if 'Cookie' in request['headers']:
                request['headers']['Cookie'] = '[SCRUBBED]'
            if 'cookie' in request['headers']:
                request['headers']['cookie'] = '[SCRUBBED]'

    # Scrub sensitive data from local variables in stacktraces
    if 'exception' in event:
        for value in event['exception']['values']:
            if 'stacktrace' in value:
                for frame in value['stacktrace']['frames']:
                    if 'vars' in frame:
                        for key in list(frame['vars'].keys()):
                            if any(s in key.lower() for s in ['password', 'token', 'secret', 'key', 'auth']):
                                frame['vars'][key] = '[SCRUBBED]'

    return event

def init_sentry():
    """
    Initialize Sentry for error tracking.
    """
    # print(f"DEBUG: SENTRY_DSN='{settings.SENTRY_DSN}'") # Removed to avoid leaking DSN in logs
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
            before_send=before_send,
            send_default_pii=False, # Explicitly disable default PII
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
