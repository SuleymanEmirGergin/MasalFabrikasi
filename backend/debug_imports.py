
import sys
import os
import importlib
import traceback

sys.path.append(os.getcwd())

routers_to_check = [
    "app.routers.story",
    "app.routers.health",
    "app.routers.character",
    "app.routers.user",
    "app.routers.challenge",
    "app.routers.quiz",
    "app.routers.analytics",
    "app.routers.social",
    "app.routers.media",
    "app.routers.ai_tools",
    "app.routers.story_features",
    "app.routers.story_advanced_features",
    "app.routers.user_features",
    "app.routers.platform",
    "app.routers.education",
    "app.routers.market",
    "app.routers.collaboration",
    "app.routers.vision",
    "app.routers.voice_cloning",
    "app.routers.parental",
    "app.routers.shop",
    "app.routers.metrics_router",
    "app.routers.stripe_router",
    "app.routers.iap_router",
    "app.routers.notification_router",
    "app.routers.admin_router",
    "app.routers.referral_router",
    "app.routers.gamification_router",
    "app.routers.ai_tools_router",
    "app.routers.interactive_router",
    "app.routers.parental_router",
    "app.routers.community_router",
    "app.routers.magic_canvas_router",
    "app.routers.character_chat_router",
    "app.routers.smart_room_router",
    "app.routers.subscription_router",
    "app.routers.bedtime_router",
    "app.routers.value_features_router"
]

print("🔍 Starting granular import check...")

for module_name in routers_to_check:
    print(f"👉 Importing {module_name}...", end=" ", flush=True)
    try:
        importlib.import_module(module_name)
        print("✅ OK")
    except Exception as e:
        print("❌ FAILED")
        print(f"\nCRITICAL ERROR in {module_name}:")
        traceback.print_exc()
        print("\nStopping checks due to critical error.")
        break  # Stop at the first error to keep log clean
