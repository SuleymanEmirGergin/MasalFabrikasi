#!/usr/bin/env bash
# Masal Fabrikasi - Environment setup script (Bash)
# Run from repo root: ./scripts/setup.sh

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Masal Fabrikasi setup (root: $REPO_ROOT) ==="

# 1. Backend .env
if [ ! -f backend/.env ] && [ -f backend/.env.example ]; then
  cp backend/.env.example backend/.env
  echo "[OK] backend/.env created from .env.example"
elif [ -f backend/.env ]; then
  echo "[SKIP] backend/.env already exists"
fi

# 2. Frontend .env
if [ ! -f frontend/.env ] && [ -f frontend/.env.example ]; then
  cp frontend/.env.example frontend/.env
  echo "[OK] frontend/.env created from .env.example"
elif [ -f frontend/.env ]; then
  echo "[SKIP] frontend/.env already exists"
fi

# 3. Backend pip install
if [ -f backend/requirements.txt ]; then
  (cd backend && pip install -r requirements.txt -q)
  echo "[OK] Backend dependencies installed"
fi

# 4. Frontend npm install
if [ -f frontend/package.json ]; then
  (cd frontend && npm install)
  echo "[OK] Frontend dependencies installed"
fi

echo ""
echo "Next steps:"
echo "  1. Edit backend/.env and frontend/.env with your keys (WIRO_API_KEY, Firebase, etc.)"
echo "  2. Start DB/Redis: docker-compose up -d postgres redis"
echo "  3. Backend: cd backend && alembic upgrade head && uvicorn main:app --reload"
echo "  4. Frontend: cd frontend && npm run dev"
echo ""
