# Ödeme Entegrasyonu (iyzico + Stripe)

Bu doküman iyzico ve Stripe için callback/webhook URL'leri, gerekli ortam değişkenleri ve frontend entegrasyon notlarını açıklar.

---

## iyzico (Türkiye)

### Gerekli ortam değişkenleri

```env
IYZICO_API_KEY=your_api_key
IYZICO_SECRET_KEY=your_secret_key
IYZICO_BASE_URL=sandbox-api.iyzipay.com
```

Canlı ortamda: `IYZICO_BASE_URL=api.iyzipay.com`

### Callback URL

Ödeme sonrası iyzico kullanıcıyı backend'inize yönlendirir. URL örneği:

```
https://<API_HOST>/api/iyzico/callback
```

`<API_HOST>` backend API'nizin dışarıdan erişilebilir adresi olmalıdır (örn. `api.siteniz.com`). Bu URL'yi Checkout Form oluştururken `callback_url` olarak gönderin.

### Akış

1. **Frontend:** `POST /api/iyzico/create-checkout` ile istek atar.
   - Body: `product_id`, `user_id`, `callback_url`, `buyer_email` (opsiyonel), `buyer_name` (opsiyonel), `locale` (opsiyonel, varsayılan `tr`).
   - `callback_url`: Ödeme tamamlanınca iyzico'nun kullanıcıyı yönlendireceği URL. **Backend callback endpoint'i** olmalıdır: `https://<API_HOST>/api/iyzico/callback`. Böylece iyzico tarayıcıyı bu URL'ye `?token=...` ile yönlendirir.

2. **Backend** `create-checkout` yanıtında `paymentPageUrl` döner. Frontend kullanıcıyı bu URL'ye yönlendirir.

3. Kullanıcı iyzico sayfasında ödemeyi tamamlar. iyzico tarayıcıyı `callback_url` (yani `https://<API_HOST>/api/iyzico/callback?token=...`) adresine yönlendirir.

4. **Backend** `GET /api/iyzico/callback?token=...` çağrıldığında:
   - `iyzico_service.retrieve_checkout_form(token)` ile sonucu alır.
   - Başarılıysa Purchase kaydı oluşturur, kredi/abonelik günceller.
   - Yanıt: `{"status": "success", "message": "Ödeme işlendi", "product_id": "..."}`.

### Ürün listesi

`GET /api/iyzico/products` — Tüm ürünler ve fiyatlar.

### Test

Lokal test için callback URL’in dışarıdan erişilebilir olması gerekir. Örn. ngrok: `ngrok http 8000` ile `https://xxx.ngrok.io/api/iyzico/callback` kullanılabilir.

---

## Stripe

### Gerekli ortam değişkenleri

```env
STRIPE_SECRET_KEY=sk_test_...   # veya sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...  # frontend için, opsiyonel
STRIPE_PRICE_ID_PREMIUM_MONTHLY=   # abonelik fiyat ID (opsiyonel)
STRIPE_PRICE_ID_PRO_MONTHLY=       # Pro plan fiyat ID (opsiyonel)
```

### Webhook URL

Stripe Dashboard’da webhook endpoint olarak ekleyin:

```
https://<API_HOST>/api/stripe/webhook
```

**Önemli:** Webhook’u işleyen asıl router `stripe_router.py` (prefix `/api/stripe`). `subscription_router.py` içindeki webhook ayrı bir implementasyon; ana webhook mantığı `/api/stripe/webhook` üzerindedir.

### Webhook event’leri

Aşağıdaki event’leri dinleyin:

- `payment_intent.succeeded` — Tek seferlik ödeme (kredi satın alma vb.)
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

### Ödeme / abonelik akışı

- **Tek seferlik ödeme:** `POST /api/stripe/create-payment-intent` (body: `product_id`, `user_id`). Frontend Stripe.js ile ödeme yapar; başarı webhook ile işlenir.
- **Abonelik:** `POST /api/stripe/create-subscription` (body: `product_id`, `user_id`, `payment_method_id`). Webhook’ta `customer.subscription.created/updated/deleted` işlenir.

### Subscription Checkout Session (subscription_router)

`POST /api/subscription/create-checkout-session?price_id=...` ile Stripe Checkout sayfası oluşturulur. Success ve cancel URL’leri şu an kodda sabit (`https://masalfabrikasi.app/success`, `https://masalfabrikasi.app/cancel`). **Öneri:** Ortama göre (staging/prod) bu URL’leri `FRONTEND_URL` veya benzeri bir env’den okuyacak şekilde güncelleyin (örn. `{FRONTEND_URL}/success`, `{FRONTEND_URL}/cancel`).

---

## Özet tablo

| Özellik        | iyzico                         | Stripe                              |
|----------------|--------------------------------|-------------------------------------|
| Ana endpoint   | `/api/iyzico/create-checkout`  | `/api/stripe/create-payment-intent`, `/api/stripe/create-subscription` |
| Callback/Webhook | `GET /api/iyzico/callback?token=...` | `POST /api/stripe/webhook`          |
| Ürün listesi   | `GET /api/iyzico/products`     | `GET /api/stripe/products`           |

Ortam değişkenlerinin tam listesi için bkz. [ENV_AND_DATABASE.md](ENV_AND_DATABASE.md).
