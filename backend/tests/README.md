# Test Dokümantasyonu

Bu klasör projenin test dosyalarını içerir.

## Test Yapısı

```
tests/
├── __init__.py
├── conftest.py              # Pytest konfigürasyonu ve fixtures
├── test_health.py           # Health check testleri
├── test_story_service.py    # Story service unit testleri
├── test_api_endpoints.py    # API endpoint integration testleri
└── test_new_features.py     # Yeni özellikler testleri
```

## Test Çalıştırma

### Tüm testleri çalıştırma
```bash
pytest
```

### Sadece unit testler
```bash
pytest -m unit
```

### Sadece integration testler
```bash
pytest -m integration
```

### Coverage raporu ile
```bash
pytest --cov=app --cov-report=html
```

### Belirli bir test dosyası
```bash
pytest tests/test_health.py
```

### Belirli bir test fonksiyonu
```bash
pytest tests/test_health.py::test_health_check
```

## Test Markers

- `@pytest.mark.unit` - Unit testler
- `@pytest.mark.integration` - Integration testler
- `@pytest.mark.api` - API endpoint testleri
- `@pytest.mark.slow` - Yavaş çalışan testler

## Fixtures

### test_client
FastAPI test client'ı sağlar.

### mock_openai_client
OpenAI client'ını mocklar.

### mock_storage_path
Geçici storage path'i sağlar.

### sample_story_data
Örnek hikaye verisi sağlar.

### sample_user_data
Örnek kullanıcı verisi sağlar.

## Test Örnekleri

### Basit Endpoint Testi
```python
def test_health_check(test_client: TestClient):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Mock ile Servis Testi
```python
@pytest.mark.asyncio
async def test_create_story(story_service, mock_openai_client):
    result = await story_service.create_story(
        theme="test theme",
        language="tr"
    )
    assert result is not None
```

## Notlar

- Testler otomatik olarak test storage dizinini kullanır
- OpenAI API key gerektiren testler mock'lanmıştır
- Her test sonrası temizlik yapılır

