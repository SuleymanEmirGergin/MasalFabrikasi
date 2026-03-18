#!/usr/bin/env python3
"""Test runner script"""
import subprocess
import sys
import time
import os
from pathlib import Path

# Change to backend directory
os.chdir(Path(__file__).parent)

print("🧪 Testler başlatılıyor...")
print("=" * 60)

start_time = time.time()

# Run tests
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x", "--disable-warnings"],
    cwd=Path(__file__).parent
)

elapsed = time.time() - start_time

print("\n" + "=" * 60)
print(f"⏱️  Toplam süre: {elapsed:.2f} saniye")
print(f"📊 Exit code: {result.returncode}")

sys.exit(result.returncode)

