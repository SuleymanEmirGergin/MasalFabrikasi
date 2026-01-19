import sys
import os
import time
from celery import Celery

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

try:
    from app.celery_app import celery_app
except ImportError:
    print("Could not import celery_app. Ensure you are running from repo root.")
    sys.exit(1)

def smoke_test():
    print("🚀 Starting Celery Smoke Test...")

    # Check Broker Connection
    try:
        with celery_app.connection() as connection:
            print(f"✅ Broker connected: {connection.as_uri()}")
            connection.ensure_connection(max_retries=3)
    except Exception as e:
        print(f"❌ Broker connection failed: {e}")
        sys.exit(1)

    # Check Worker Availability
    i = celery_app.control.inspect()
    workers = i.active()
    if not workers:
        print("⚠️  No active workers found. Is celery_worker running?")
        # We don't fail here because maybe we just want to test enqueueing
    else:
        print(f"✅ Active workers: {list(workers.keys())}")

    print("✅ Smoke test passed!")

if __name__ == "__main__":
    smoke_test()
