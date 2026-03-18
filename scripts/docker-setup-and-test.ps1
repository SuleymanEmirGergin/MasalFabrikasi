# Masal Fabrikasi - Docker konteyner kurulumu ve testler
# Kullanim: PowerShell'de .\scripts\docker-setup-and-test.ps1
# Gereksinim: Docker Desktop acik ve calisir durumda olmali

$ErrorActionPreference = "Stop"
# Script scripts/ icinde; proje kokunu bul (ust dizin)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path "$ProjectRoot\docker-compose.yml")) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
if (-not (Test-Path "$ProjectRoot\docker-compose.yml")) {
    $ProjectRoot = Get-Location
}
Set-Location $ProjectRoot

Write-Host "=== 1. Docker baglantisini kontrol et ===" -ForegroundColor Cyan
try {
    $null = docker info 2>&1
} catch {
    $null = $_
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "HATA: Docker daemon ulasilamiyor." -ForegroundColor Red
    Write-Host "  - Docker Desktop acik mi? Sistem tepsisinde Docker ikonunu kontrol edin." -ForegroundColor Yellow
    Write-Host "  - Aciksa 30 saniye bekleyip tekrar deneyin: .\scripts\docker-setup-and-test.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== 2. Postgres ve Redis konteynerlerini baslat ===" -ForegroundColor Cyan
docker-compose up -d postgres redis
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Saglik kontrolleri icin 15 saniye bekleniyor..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "=== 3. Backend konteynerini baslat ===" -ForegroundColor Cyan
docker-compose up -d --build backend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Backend baslamasi icin 10 saniye bekleniyor..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "=== 4. Veritabani migrasyonlari ===" -ForegroundColor Cyan
docker-compose exec -T backend alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== 5. Testler (Stripe unit + integration, auth, gdpr, health) ===" -ForegroundColor Cyan
docker-compose exec -T backend pytest tests/unit/test_stripe_service.py tests/integration/test_stripe_endpoints.py tests/integration/test_auth_endpoints.py tests/integration/test_gdpr_endpoints.py tests/test_health.py -v --tb=short 2>&1

$testExit = $LASTEXITCODE
Write-Host ""
if ($testExit -eq 0) {
    Write-Host "Tum testler gecti." -ForegroundColor Green
} else {
    Write-Host "Bazi testler basarisiz (cikis kodu: $testExit)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Servisler:" -ForegroundColor Cyan
Write-Host "  API:     http://localhost:8000" -ForegroundColor White
Write-Host "  Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health:  http://localhost:8000/api/health" -ForegroundColor White
Write-Host ""
Write-Host "Durdurmak icin: docker-compose down" -ForegroundColor Gray
exit $testExit
