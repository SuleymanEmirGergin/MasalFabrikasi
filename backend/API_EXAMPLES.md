# API Kullanım Örnekleri

Bu dosya Masal Fabrikası AI API'sinin kullanım örneklerini içerir.

## Temel Kullanım

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00"
}
```

### 2. Hikaye Üretimi

```bash
curl -X POST http://localhost:8000/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "uzayda yalnız bir gezgin",
    "language": "tr",
    "story_type": "masal"
  }'
```

**Response:**
```json
{
  "story_id": "uuid",
  "story_text": "Bir zamanlar uzayda yalnız bir gezgin vardı...",
  "image_url": "/storage/images/uuid.png",
  "audio_url": "/storage/audio/uuid.mp3",
  "created_at": "2024-01-01T00:00:00"
}
```

### 3. Hikayeleri Listeleme

```bash
curl http://localhost:8000/api/stories?limit=10&story_type=masal
```

## Yeni Özellikler (500+)

### Karakter Derinliği

```bash
curl -X POST http://localhost:8000/api/character-depth/process \
  -H "Content-Type: application/json" \
  -d '{
    "story_id": "story_123",
    "story_text": "Hikaye metni..."
  }'
```

### Dünya Detayları

```bash
curl -X POST http://localhost:8000/api/world-detail/process \
  -H "Content-Type: application/json" \
  -d '{
    "story_id": "story_123",
    "story_text": "Hikaye metni..."
  }'
```

### Olay Örgüsü Karmaşıklığı

```bash
curl -X POST http://localhost:8000/api/plot-complexity/process \
  -H "Content-Type: application/json" \
  -d '{
    "story_id": "story_123",
    "story_text": "Hikaye metni..."
  }'
```

### Okunabilirlik Analizi

```bash
curl -X POST http://localhost:8000/api/readability-analyzer/process \
  -H "Content-Type: application/json" \
  -d '{
    "story_id": "story_123",
    "story_text": "Hikaye metni..."
  }'
```

### Akış Optimizasyonu

```bash
curl -X POST http://localhost:8000/api/flow-optimizer/process \
  -H "Content-Type: application/json" \
  -d '{
    "story_id": "story_123",
    "story_text": "Hikaye metni..."
  }'
```

### Duygusal Etki Analizi

```bash
curl -X POST http://localhost:8000/api/emotional-impact/process \
  -H "Content-Type: application/json" \
  -d '{
    "story_id": "story_123",
    "story_text": "Hikaye metni..."
  }'
```

## Python Örnekleri

### requests Kütüphanesi ile

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Hikaye üretimi
response = requests.post(
    f"{BASE_URL}/generate-story",
    json={
        "theme": "uzayda yalnız bir gezgin",
        "language": "tr",
        "story_type": "masal"
    }
)
print(response.json())

# Karakter derinliği
response = requests.post(
    f"{BASE_URL}/character-depth/process",
    json={
        "story_id": "story_123",
        "story_text": "Hikaye metni..."
    }
)
print(response.json())
```

### httpx (Async) ile

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api"

async def main():
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get(f"{BASE_URL}/health")
        print(response.json())
        
        # Hikaye üretimi
        response = await client.post(
            f"{BASE_URL}/generate-story",
            json={
                "theme": "uzayda yalnız bir gezgin",
                "language": "tr",
                "story_type": "masal"
            }
        )
        print(response.json())

asyncio.run(main())
```

## JavaScript/TypeScript Örnekleri

### Fetch API ile

```javascript
const BASE_URL = "http://localhost:8000/api";

// Health check
fetch(`${BASE_URL}/health`)
  .then(res => res.json())
  .then(data => console.log(data));

// Hikaye üretimi
fetch(`${BASE_URL}/generate-story`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    theme: "uzayda yalnız bir gezgin",
    language: "tr",
    story_type: "masal"
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Karakter derinliği
fetch(`${BASE_URL}/character-depth/process`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    story_id: "story_123",
    story_text: "Hikaye metni..."
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Axios ile

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Health check
api.get('/health')
  .then(response => console.log(response.data));

// Hikaye üretimi
api.post('/generate-story', {
  theme: "uzayda yalnız bir gezgin",
  language: "tr",
  story_type: "masal"
})
  .then(response => console.log(response.data));

// Karakter derinliği
api.post('/character-depth/process', {
  story_id: "story_123",
  story_text: "Hikaye metni..."
})
  .then(response => console.log(response.data));
```

## Tüm Endpoint'ler

500+ endpoint'in tam listesi için Swagger UI'yi ziyaret edin:
http://localhost:8000/docs

## Hata Yönetimi

### Başarılı Response
```json
{
  "id": "uuid",
  "result": "İşlem sonucu..."
}
```

### Hata Response
```json
{
  "detail": "Hata mesajı"
}
```

### HTTP Status Kodları
- `200` - Başarılı
- `400` - Geçersiz istek
- `404` - Bulunamadı
- `500` - Sunucu hatası

## Rate Limiting

Şu anda rate limiting yoktur, ancak production'da eklenmesi önerilir.

## Authentication

Şu anda authentication yoktur, ancak production'da eklenmesi önerilir.

