
import sys
import os
import traceback

sys.path.append(os.getcwd())

print("Attempting to import main app...")
try:
    from main import app
    print("✅ Main App Imported Successfully")
except Exception:
    print("❌ FAILED to import main app")
    traceback.print_exc()
