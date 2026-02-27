
import sys
import os
import traceback

sys.path.append(os.getcwd())

print("Checking Voice Cloning Router Import...")
try:
    import app.routers.voice_cloning
    print("✅ Voice Cloning Router OK")
except Exception:
    print("❌ FAILED")
    traceback.print_exc()
