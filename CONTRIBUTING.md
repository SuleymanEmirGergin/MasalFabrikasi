# Katkıda Bulunma Rehberi

Masal Fabrikası projesine katkı için teşekkürler. Aşağıdaki adımlar PR sürecini hızlandırır.

## Geliştirme Ortamı

1. Repoyu klonlayın ve bağımlılıkları kurun:
   ```powershell
   # Windows
   .\scripts\setup.ps1
   ```
   ```bash
   # macOS / Linux
   chmod +x scripts/setup.sh && ./scripts/setup.sh
   ```
2. `backend/.env` ve `frontend/.env` dosyalarını ilgili `.env.example` dosyalarına göre doldurun.
3. Backend: `cd backend && uvicorn app.main:app --reload`
4. Frontend: `cd frontend && npm run dev`
5. Veritabanı: `docker-compose up -d postgres redis` (veya yerel Postgres/Redis)

Detaylı kurulum için [README.md](README.md) ve [DEPLOYMENT.md](DEPLOYMENT.md) dosyalarına bakın.

## Branch İsimlendirme

- **feature/** – Yeni özellik: `feature/quiz-scoring`, `feature/offline-sync`
- **fix/** – Hata düzeltme: `fix/login-redirect`, `fix/audio-upload`
- **docs/** – Sadece dokümantasyon: `docs/api-examples`
- **chore/** – Build, CI, bağımlılık: `chore/upgrade-deps`

## Commit Mesajları

Kısa ve anlaşılır olun; mümkünse İngilizce veya Türkçe tutarlı kullanın.

- `feat: add voice cloning delete button`
- `fix: prevent double submit on login`
- `docs: update CONTRIBUTING branch names`
- `chore: bump vite to 8.x`

## Pull Request Süreci

1. Fork edin, yukarıdaki branch isimlendirmesine uygun bir branch açın.
2. Değişikliklerinizi yapın; yerel testleri çalıştırın:
   - Backend: `cd backend && pytest tests/ -v`
   - Frontend: `cd frontend && npm run build && npm run test:e2e`
3. PR açarken:
   - Ne değiştiğini kısaca yazın.
   - İlgili issue varsa `Fixes #123` ekleyin.
4. CI (test, lint, pip-audit, frontend build) yeşil olmalıdır.

## Kod Standartları

- **Backend:** Ruff + Black (CI’da kontrol edilir). `cd backend && ruff check app/ && black --check app/`
- **Frontend:** ESLint. `cd frontend && npm run lint`
- **Güvenlik:** Backend bağımlılıkları için `pip-audit` CI’da çalışır; yerel kontrol: `cd backend && pip-audit`

## API Kullanım Örnekleri

Backend API dokümantasyonu çalışan sunucuda şu adrestedir:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

Örnek istekler (curl):

```bash
# Sağlık kontrolü
curl http://localhost:8000/api/health

# Hikaye listesi (JWT gerekir)
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/stories
```

Auth token, frontend’de giriş yaptıktan sonra Supabase/Firebase üzerinden alınır; API’ye `Authorization: Bearer <token>` header’ı ile gönderilir. Tüm endpoint’ler ve şemalar için `/docs` kullanın.

## Sorular

- **Hata / özellik talebi:** [GitHub Issues](https://github.com/yourusername/masal-fabrikasi/issues)
- **Güvenlik:** [SECURITY.md](SECURITY.md) dosyasındaki talimatları izleyin.
