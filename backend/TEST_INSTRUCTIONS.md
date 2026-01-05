# 🧪 Test Çalıştırma Talimatları

## ⚡ Hızlı Test (Önerilen - 15-25 saniye)

```bash
cd backend
py -3.12 -m pytest tests/ -v --tb=short -x --disable-warnings
```

## 🎯 Sadece Health Testleri (3-5 saniye)

```bash
cd backend
py -3.12 -m pytest tests/test_health.py -v
```

## 📊 Coverage ile Tam Test (1-2 dakika)

```bash
cd backend
py -3.12 -m pytest tests/ --cov=app --cov-report=html
```

## 🐍 Python Script ile

```bash
cd backend
py -3.12 test_runner.py
```

veya

```bash
cd backend
py -3.12 run_tests_fast.py
```

## 📝 Test Dosyaları

1. **test_health.py** - Health check endpoint testleri (2 test)
2. **test_story_service.py** - Story service unit testleri (3 test)
3. **test_api_endpoints.py** - API endpoint integration testleri (6 test)
4. **test_new_features.py** - Yeni özellikler testleri (4 test)

**Toplam: ~15 test**

## ⏱️ Tahmini Süreler

- **Hızlı mod**: 15-25 saniye
- **Coverage ile**: 1-2 dakika
- **Sadece health**: 3-5 saniye

## 🔍 Sorun Giderme

Eğer testler çalışmıyorsa:

1. Python versiyonunu kontrol edin: `py -3.12 --version`
2. Pytest kurulu mu: `py -3.12 -m pytest --version`
3. Dependencies kurulu mu: `py -3.12 -m pip list | findstr pytest`

## ✅ Başarılı Test Çıktısı

```
tests/test_health.py::test_health_check PASSED
tests/test_health.py::test_root_endpoint PASSED
tests/test_story_service.py::TestStoryService::test_create_story_basic PASSED
...
```

## ❌ Hata Durumunda

Testler ilk hatada duracak (`-x` flag'i ile). Hata mesajını kontrol edin ve düzeltin.

