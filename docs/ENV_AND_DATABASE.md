# Ortam Değişkenleri ve DATABASE_URL

Detaylı liste için `backend/.env.example` dosyasına da bakın.

---

## Tüm ortam değişkenleri

### Zorunlu (uygulama başlaması için)

| Değişken | Açıklama |
|----------|----------|
| `DATABASE_URL` | PostgreSQL bağlantı dizesi |
| `REDIS_URL` | Redis bağlantı dizesi (Celery + cache) |
| `SUPABASE_URL` | Supabase proje URL (Auth + Storage) |
| `SUPABASE_ANON_KEY` | Supabase anonim key |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `WIRO_API_KEY` | Wiro AI API key (hikaye/görsel/ses/video) |

### Opsiyonel – Özellik bazlı

**Payments (Ödemeler)**

- **iyzico (Türkiye):** `IYZICO_API_KEY`, `IYZICO_SECRET_KEY`, `IYZICO_BASE_URL`
- **Stripe:** `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_ID_PREMIUM_MONTHLY`, `STRIPE_PRICE_ID_PRO_MONTHLY` — detay: [PAYMENTS_INTEGRATION.md](PAYMENTS_INTEGRATION.md)

**AI (Wiro / çoklu sağlayıcı)**

- **Genel:** `WIRO_API_SECRET` (HMAC imzalı istekler)
- **Metin:** `GEMINI_API_KEY`, `GEMINI_MODEL`; `GPT_API_KEY`, `GPT_BASE_URL`, `GPT_MODEL`
- **Görsel:** `IMAGEN_API_KEY`, `IMAGEN_FAST_MODEL`, `IMAGEN_ULTRA_MODEL`
- **Ses:** `STT_API_KEY`, `STT_BASE_URL`, `STT_MODEL`; TTS için Wiro/ElevenLabs: `ELEVENLABS_API_KEY`
- **Video:** `VIDEO_MODEL`, `VIDEO_RESOLUTION`, `VIDEO_DURATION`
- **Embedding:** `EMBEDDING_API_KEY`, `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`
- **Legacy:** `OPENAI_API_KEY`, `OPENAI_BASE_URL`

**Monitoring**

- `SENTRY_DSN` — hata takibi

**Cloud storage**

- `USE_CLOUD_STORAGE` — `true` ise Supabase Storage kullanılır (varsayılan). Cloudinary kodda ana storage değildir.

**Diğer**

- `SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `USE_ASYNC_JOBS`, `RATE_LIMIT_FREE_TIER`, `RATE_LIMIT_PREMIUM_TIER`, `RATE_LIMIT_PRO_TIER`
- `MAX_FILE_SIZE_MB`, `FRONTEND_URL`, `ENVIRONMENT`, `APP_VERSION`
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` (email)

---

## Entegrasyon kontrol listesi

| Key / Özellik | Kullanıldığı yer |
|---------------|-------------------|
| `WIRO_API_KEY` | Hikaye metni, görsel (Imagen), ses (TTS), video (Veo3), STT |
| `SUPABASE_*` | Auth, Storage (görsel/ses yükleme), Magic Canvas |
| `IYZICO_*` | Türkiye ödemeleri – Checkout Form, callback |
| `STRIPE_*` | Abonelik checkout, webhook ile ödeme/abonelik güncelleme |
| `SENTRY_DSN` | Production hata takibi |

---

## DATABASE_URL nereden gelir?

- **Lokal geliştirme:** `backend/.env` dosyasında tanımlayın. Örnek:
  ```env
  DATABASE_URL=postgresql://admin:ŞİFRENİZ@localhost:5432/masalfabrikasi
  DATABASE_PASSWORD=ŞİFRENİZ
  ```
  PostgreSQL’i kendi makinenizde veya bir konteynerde çalıştırıyorsanız `localhost` ve kullandığınız kullanıcı/şifre/db adı ile doldurun.

- **Docker Compose:** Backend servisi çalışırken `DATABASE_URL` **otomatik atanır**; compose dosyasında şu satır vardır:
  ```yaml
  environment:
    DATABASE_URL: postgresql://admin:${DATABASE_PASSWORD:-changeme}@postgres:5432/masalfabrikasi
  ```
  Yani `backend/.env` içinde sadece `DATABASE_PASSWORD` (ve isterseniz diğer değişkenler) yeterli. `postgres` burada Docker’daki Postgres servisinin adıdır.

- **Railway / Render / Fly.io:** Panelden “Environment Variables” bölümüne ekleyin. Örnek:
  ```env
  DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
  ```
  Değeri genelde sağlayıcı (Railway vb.) kendi eklediği Postgres servisinden kopyalamanız yeterli.

Özet: **Lokal** için `.env`’de kendiniz yazın; **Docker** için sadece `DATABASE_PASSWORD`; **bulut** için panelden verilen `DATABASE_URL`’i kullanın.

---

## iyzico (Ödeme) kurulumu

1. [iyzico](https://www.iyzico.com) üzerinden merchant hesabı açın.
2. Sandbox (test) veya canlı API anahtarlarınızı alın.
3. `backend/.env` içine ekleyin:
   ```env
   IYZICO_API_KEY=your_api_key
   IYZICO_SECRET_KEY=your_secret_key
   IYZICO_BASE_URL=sandbox-api.iyzipay.com
   ```
   Canlı ortamda: `IYZICO_BASE_URL=api.iyzipay.com`
4. Ödeme sonrası callback için backend’inizin **dışarıdan erişilebilir** bir URL’i olmalı (örn. `https://api.siteniz.com/api/iyzico/callback`). Bu URL’i Checkout Form oluştururken `callback_url` olarak gönderin.

API dokümantasyonu: [docs.iyzico.com](https://docs.iyzico.com)

---

## Stripe kurulumu

Stripe kullanacaksanız `backend/.env` içine `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` ve isteğe bağlı price ID’leri ekleyin. Webhook URL’i ve akış detayları için bkz. **[PAYMENTS_INTEGRATION.md](PAYMENTS_INTEGRATION.md)**.

---

## Gamification ve yetkilendirme

Gamification endpoint'leri (leaderboard, quests, achievements) `user_id` path parametresi alır. Bu `user_id` değerinin Supabase Auth ile doğrulanmış kullanıcı ile eşleşmesi gerekir; aksi halde yetkisiz veri erişimi riski vardır. İleride bu route'larda `get_current_user` dependency kullanılması önerilir.

---

## Rate limit notu

Ödeme callback (`GET /api/iyzico/callback`) ve Stripe webhook (`POST /api/stripe/webhook`) endpoint'leri iyzico/Stripe sunucuları tarafından çağrılır. Mevcut yapı SlowAPI ile genel rate limit kullanır; bu endpoint'ler için farklı/gevşek limit veya istisna tanımlanabilir (ör. webhook imza doğrulaması yeterli görülüyorsa).
