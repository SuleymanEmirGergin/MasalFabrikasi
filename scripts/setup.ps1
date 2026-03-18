# Masal Fabrikasi - Environment setup script (PowerShell)
# Run from repo root: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $RepoRoot "backend"))) { $RepoRoot = (Get-Location).Path }

Write-Host "=== Masal Fabrikasi setup (root: $RepoRoot) ===" -ForegroundColor Cyan

# 1. Backend .env
$backendEnv = Join-Path $RepoRoot "backend\.env"
$backendExample = Join-Path $RepoRoot "backend\.env.example"
if (-not (Test-Path $backendEnv) -and (Test-Path $backendExample)) {
    Copy-Item $backendExample $backendEnv
    Write-Host "[OK] backend/.env created from .env.example" -ForegroundColor Green
} elseif (Test-Path $backendEnv) {
    Write-Host "[SKIP] backend/.env already exists" -ForegroundColor Yellow
} else {
    Write-Host "[WARN] backend/.env.example not found" -ForegroundColor Yellow
}

# 2. Frontend .env
$frontendEnv = Join-Path $RepoRoot "frontend\.env"
$frontendExample = Join-Path $RepoRoot "frontend\.env.example"
if (-not (Test-Path $frontendEnv) -and (Test-Path $frontendExample)) {
    Copy-Item $frontendExample $frontendEnv
    Write-Host "[OK] frontend/.env created from .env.example" -ForegroundColor Green
} elseif (Test-Path $frontendEnv) {
    Write-Host "[SKIP] frontend/.env already exists" -ForegroundColor Yellow
}

# 3. Backend pip install
$backendPath = Join-Path $RepoRoot "backend"
if (Test-Path (Join-Path $backendPath "requirements.txt")) {
    Push-Location $backendPath
    try {
        pip install -r requirements.txt --quiet
        Write-Host "[OK] Backend dependencies installed" -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

# 4. Frontend npm install
$frontendPath = Join-Path $RepoRoot "frontend"
if (Test-Path (Join-Path $frontendPath "package.json")) {
    Push-Location $frontendPath
    try {
        npm install
        Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit backend/.env and frontend/.env with your keys (WIRO_API_KEY, Firebase, etc.)"
Write-Host "  2. Start DB/Redis: docker-compose up -d postgres redis"
Write-Host "  3. Backend: cd backend && alembic upgrade head && uvicorn main:app --reload"
Write-Host "  4. Frontend: cd frontend && npm run dev"
Write-Host ""
