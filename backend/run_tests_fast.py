#!/usr/bin/env python3
"""
Hızlı test çalıştırma scripti - Coverage olmadan
"""
import subprocess
import sys
import time

def run_tests_fast():
    """Coverage olmadan hızlı test çalıştır"""
    print("🚀 Hızlı test modu başlatılıyor...")
    print("=" * 60)
    
    start_time = time.time()
    
    # Coverage olmadan test çalıştır
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-x",  # İlk hatada dur
        "--disable-warnings",
        "-q"  # Quiet mode
    ]
    
    print(f"Komut: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    elapsed = time.time() - start_time
    
    print(result.stdout)
    if result.stderr:
        print("Hatalar:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    
    print()
    print("=" * 60)
    print(f"⏱️  Toplam süre: {elapsed:.2f} saniye")
    print(f"📊 Exit code: {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests_fast())

