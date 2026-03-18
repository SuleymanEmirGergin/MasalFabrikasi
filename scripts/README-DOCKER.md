# Docker ile Kurulum ve Test

## Gereksinim
- **Docker Desktop** yüklü ve **açık** olmalı (sistem tepsisinde çalışıyor olmalı).

## Tek komutla kurulum ve test (PowerShell)

Proje kök dizinindeyken:

```powershell
.\scripts\docker-setup-and-test.ps1
```

Bu script:
1. Docker bağlantısını kontrol eder
2. Postgres ve Redis konteynerlerini başlatır
3. Backend konteynerini build edip başlatır
4. `alembic upgrade head` ile migrasyonları uygular
5. Stripe, auth, GDPR ve health testlerini çalıştırır

## Manuel adımlar

Docker Desktop açıkken proje kökünde:

```powershell
# 1. Sadece veritabanı ve Redis
docker-compose up -d postgres redis

# 2. Birkaç saniye bekleyin, sonra backend
docker-compose up -d --build backend

# 3. Migrasyonlar
docker-compose exec backend alembic upgrade head

# 4. Tüm testler
docker-compose exec backend pytest tests/ -v --tb=short

# Sadece Stripe testleri
docker-compose exec backend pytest tests/unit/test_stripe_service.py tests/integration/test_stripe_endpoints.py -v
```

## Backend .env
`backend/.env` yoksa script öncesi oluşturulmalı. Projede `backend/.env.example` var; `backend/.env` için minimal bir dosya oluşturuldu (Docker için placeholder değerlerle).

## Konteynerleri durdurma
```powershell
docker-compose down
```

## Yararlı linkler
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/health
