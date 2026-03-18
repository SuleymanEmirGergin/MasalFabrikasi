#!/usr/bin/env python3
"""
Security vulnerability scan for Masal Fabrikasi backend.

Runs:
  1. pip-audit - dependency CVEs
  2. bandit - static code analysis (if installed)

Usage (from backend/):
  python scripts/security_scan.py

Requires (install separately):
  pip install pip-audit
  pip install bandit  # optional
"""
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path, name: str) -> bool:
    """Run command; return True if exit code 0."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        if out:
            print(out)
        if err:
            print(err, file=sys.stderr)
        if r.returncode != 0:
            print(f"[{name}] exited with code {r.returncode}", file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print(f"[{name}] not found. Install with: pip install {name.replace('_', '-')}", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print(f"[{name}] timed out.", file=sys.stderr)
        return False


def main() -> int:
    print("=== Security scan (backend) ===\n")
    all_ok = True

    # 1. pip-audit
    print("--- pip-audit (dependency vulnerabilities) ---")
    if not run([sys.executable, "-m", "pip_audit"], cwd=BACKEND_ROOT, name="pip-audit"):
        print("Tip: pip install pip-audit")
        all_ok = False
    print()

    # 2. bandit (optional; non-zero exit = issues found, we still pass script exit)
    print("--- bandit (code security) ---")
    try:
        r = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "app", "-ll"],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            timeout=90,
        )
        if r.returncode == 0:
            print("Bandit: no issues found.")
        else:
            print(r.stdout or "")
            print(r.stderr or "", file=sys.stderr)
            print("Bandit: issues found (review above).")
    except FileNotFoundError:
        print("Bandit not found. Install with: pip install bandit")
    except Exception as e:
        print(f"Bandit error: {e}", file=sys.stderr)
    print()

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
