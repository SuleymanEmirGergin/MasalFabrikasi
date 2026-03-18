
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'app'))
sys.path.append(os.getcwd())

print("Running Smoke Test...")

try:
    print("1. Importing Models...")
    from app.models import Base
    print("   Models imported successfully.")
except Exception as e:
    print(f"FAILED to import Models. Error type: {type(e).__name__}")
    print(f"Error details: {str(e)[:200]}") # Truncate to avoid tool output limit hitting
    import traceback
    traceback.print_exc(limit=1)
    sys.exit(1)

try:
    print("2. Importing Config...")
    from app.core.config import settings
    print("   Config imported successfully.")
except Exception as e:
    print(f"FAILED to import Config: {e}")
    sys.exit(1)

try:
    print("3. Importing Services...")
    from app.services.story_service import StoryService
    from app.services.image_service import ImageService
    from app.services.tts_service import TTSService
    from app.services.voice_cloning_service import VoiceCloningService
    print("   Services imported successfully.")
except Exception as e:
    print(f"FAILED to import Services: {e}")
    sys.exit(1)

try:
    print("4. Importing Routers...")
    from app.routers import story, voice_cloning, gamification_router, magic_canvas_router
    print("   Routers imported successfully.")
except Exception as e:
    print(f"FAILED to import Routers: {e}")
    sys.exit(1)

try:
    print("5. Checking Celery App...")
    from app.celery_app import celery
    print("   Celery App imported successfully.")
except Exception as e:
    print(f"FAILED to import Celery App: {e}")
    sys.exit(1)

print("\nSMOKE TEST PASSED! Codebase structure is sound.")
