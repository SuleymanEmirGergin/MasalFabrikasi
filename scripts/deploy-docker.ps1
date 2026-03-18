# Masal Fabrikasi - Docker ile deploy
# Kullanim: Proje kokunde .\scripts\deploy-docker.ps1
# Gereksinim: Docker Desktop acik, backend/.env mevcut

$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { Get-Location }
Set-Location $Root

if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "HATA: docker-compose.yml bulunamadi. Proje kokunde calistirin." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "backend\.env")) {
    Write-Host "UYARI: backend\.env yok. backend\.env.example'dan kopyalayip doldurun." -ForegroundColor Yellow
}

Write-Host "Postgres, Redis, Backend ve Celery baslatiliyor..." -ForegroundColor Cyan
docker-compose up -d postgres redis backend celery_worker
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Servisler ayakta. Migrasyonlar backend CMD icinde calisir." -ForegroundColor Green
Write-Host "  API:    http://localhost:8000" -ForegroundColor White
Write-Host "  Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health: http://localhost:8000/api/health" -ForegroundColor White
Write-Host ""
Write-Host "Durdurmak: docker-compose down" -ForegroundColor Gray
