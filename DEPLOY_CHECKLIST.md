# Deploy Öncesi Kontrol Listesi

## 1. Ortam dosyası (backend/.env)

- [ ] `DATABASE_PASSWORD` güçlü bir şifre (Docker için)
- [ ] `SECRET_KEY` üretildi: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] `DEBUG=false` (canlı ortamda)
- [ ] `IYZICO_API_KEY` ve `IYZICO_SECRET_KEY` (iyzico panelinden)
- [ ] `IYZICO_BASE_URL=api.iyzipay.com` (canlı) veya `sandbox-api.iyzipay.com` (test)
- [ ] `SUPABASE_*` ve `WIRO_*` gerekliyse dolduruldu
- [ ] `CORS_ORIGINS` frontend adresinizi içeriyor

## 2. DATABASE_URL

- **Docker:** Boş bırakabilirsiniz; `docker-compose` otomatik atar.
- **Railway/Render:** Panelden eklenen Postgres’in `DATABASE_URL` değişkeni kullanılır.

## 3. Docker ile deploy

```bash
docker-compose up -d postgres redis backend celery_worker
```

Ardından: http://localhost:8000/docs ve http://localhost:8000/api/health kontrol edin.

## 4. Bulut (Railway / Render)

- Repo GitHub’a push edildi
- PostgreSQL ve Redis servisleri eklendi
- Tüm env değişkenleri panele girildi (DEPLOYMENT.md’deki liste)
- İlk deploy sonrası: `alembic upgrade head` (Railway: `railway run alembic upgrade head`)

## 5. iyzico callback URL

Canlıda ödeme sonrası yönlenecek adres örnek:

- `https://api.siteniz.com/api/iyzico/callback`

Bu URL’i uygulama tarafında Checkout oluştururken `callback_url` olarak kullanın.
