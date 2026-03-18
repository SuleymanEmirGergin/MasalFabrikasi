# Bildirim Altyapısı (Push Notifications)

Backend push bildirim API'si ve Expo Push entegrasyonu. Ek FCM key gerekmez; Expo push token yeterlidir.

---

## Backend API

### Cihaz kaydı

**POST** `/api/notifications/register`

Kullanıcının cihazından alınan Expo push token'ı backend'e kaydeder.

**Body (JSON):**

```json
{
  "user_id": "uuid-string",
  "push_token": "ExponentPushToken[xxxxxx]",
  "platform": "ios",
  "device_name": "iPhone"
}
```

| Alan | Zorunlu | Açıklama |
|------|---------|----------|
| `user_id` | Evet | Supabase auth user id (UUID) |
| `push_token` | Evet | Expo Push Token |
| `platform` | Hayır | `ios`, `android`, `unknown` (varsayılan: `unknown`) |
| `device_name` | Hayır | Cihaz adı (varsayılan: `unknown`) |

**Yanıt:** `{"status": "success", "message": "Device registered"}`

### Bildirim gönderme

**POST** `/api/notifications/send`

Belirli bir kullanıcıya (kayıtlı cihazlarına) bildirim gönderir. Admin/sistem kullanımı içindir.

**Body (JSON):**

```json
{
  "user_id": "uuid-string",
  "title": "Yeni hikaye",
  "body": "Sizin için yeni bir hikaye hazır.",
  "data": { "story_id": "abc123" }
}
```

| Alan | Zorunlu | Açıklama |
|------|---------|----------|
| `user_id` | Evet | Hedef kullanıcı (auth user id) |
| `title` | Evet | Bildirim başlığı |
| `body` | Evet | Bildirim gövdesi |
| `data` | Hayır | Ek veri (deep link vb.) |

**Yanıt:** Expo Push API yanıtı; kullanıcının kayıtlı cihazı yoksa `{"status": "skipped", "reason": "User has no active devices"}`.

---

## Expo Push

Backend **Expo Push API** (`https://exp.host/--/api/v2/push/send`) kullanır. FCM/APNs key'leri backend tarafında gerekmez; mobil uygulama Expo push token üretir ve bu token ile gönderim yapılır.

### İleride yapılacaklar (mobil)

1. **Expo Notifications** kurulumu (React Native/Expo projesinde).
2. Uygulama açılışında veya giriş sonrası `getExpoPushTokenAsync()` (veya benzeri) ile token alınır.
3. Token `POST /api/notifications/register` ile backend'e gönderilir (user_id = giriş yapan kullanıcı).
4. Test bildirimi: Backend'den `POST /api/notifications/send` ile ilgili user_id'ye deneme bildirimi atılabilir.

Detaylı Expo Notifications dokümantasyonu: [Expo Push Notifications](https://docs.expo.dev/push-notifications/overview/).
