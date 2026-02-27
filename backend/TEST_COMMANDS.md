# 🧪 Test Komutları - Windows PowerShell

## ⚡ Hızlı Test (Önerilen)

PowerShell'de şu komutu çalıştır:

```powershell
cd backend
py -3.12 -m pytest tests/ -v --tb=short -x --disable-warnings
```

## 🎯 Sadece Health Testleri (En Hızlı)

```powershell
cd backend
py -3.12 -m pytest tests/test_health.py -v
```

## 📊 Coverage ile Tam Test

```powershell
cd backend
py -3.12 -m pytest tests/ --cov=app --cov-report=html
```

## 🖱️ Batch Script ile (Kolay)

Windows Explorer'da `backend` klasörüne git ve çift tıkla:

- **`run_tests.bat`** - Tüm testleri çalıştır
- **`run_tests_quick.bat`** - Sadece health testleri

## 🐍 Python Script ile

```powershell
cd backend
py -3.12 test_runner.py
```

veya

```powershell
cd backend
py -3.12 run_tests_fast.py
```

## ⏱️ Tahmini Süreler

- **Hızlı mod**: 15-25 saniye
- **Coverage ile**: 1-2 dakika  
- **Sadece health**: 3-5 saniye

## 📝 Notlar

- PowerShell'de `py -3.12` kullan (sadece `python` değil)
- Eğer `py` çalışmıyorsa: `python -m pytest` dene
- Testler ilk hatada duracak (`-x` flag'i ile)

