# Python 3.12 Kurulum Rehberi

Bu proje artık Python 3.12 ile çalışacak şekilde yapılandırılmıştır.

## Kurulum Adımları

### 1. Python 3.12 Kurulumu

Eğer Python 3.12 yüklü değilse:

**Windows:**
- [Python 3.12 İndirme Sayfası](https://www.python.org/downloads/release/python-3120/) adresinden Python 3.12'yi indirin
- Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

**Kontrol:**
```powershell
py -3.12 --version
```

### 2. Virtual Environment Oluşturma (Önerilen)

```powershell
cd backend
py -3.12 -m venv venv
```

**Virtual Environment'ı Aktifleştirme:**

PowerShell execution policy sorunu varsa, şu yöntemlerden birini kullanın:

**Yöntem 1: Doğrudan Python kullanarak (Önerilen)**
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Yöntem 2: Execution Policy'yi geçici olarak değiştirme**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```

**Yöntem 3: CMD kullanarak**
```cmd
venv\Scripts\activate.bat
```

### 3. Bağımlılıkları Yükleme

**Virtual Environment Aktifken:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Virtual Environment Aktif Değilse:**
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Not:** `pillow` paketi Python 3.12 ile uyumlu olmalı. Eğer kurulum hatası alırsanız:
```powershell
py -3.12 -m pip install pillow --upgrade
```

### 4. Testleri Çalıştırma

**ÖNEMLİ:** Testleri `backend` dizininden çalıştırın!

**Yöntem 1: Backend dizininden (Önerilen)**
```powershell
cd backend
py -3.12 -m pytest tests/test_health.py -v
```

**Yöntem 2: Batch script ile (Kolay)**
```powershell
cd backend
.\run_tests_simple.bat
```

**Yöntem 3: Virtual Environment Aktifken**
```powershell
cd backend
.\venv\Scripts\activate
pytest tests/test_health.py -v
```

**Tüm testler için:**
```powershell
cd backend
py -3.12 -m pytest tests/ -v
```

**Hata:** Eğer "file or directory not found: tests/test_health.py" hatası alıyorsanız:
- `backend` dizinine gittiğinizden emin olun: `cd backend`
- Veya tam yolu kullanın: `py -3.12 -m pytest backend/tests/test_health.py -v`

## Önemli Notlar

- Python 3.12 daha stabil ve yaygın olarak destekleniyor
- `httpx` versiyonu `0.25.1` ile `0.28.0` arasında olmalı (Python 3.12 uyumluluğu için)
- `httpcore` versiyonu `1.0.0` ile `1.1.0` arasında olmalı
- `anyio` versiyonu `3.7.1` ile `4.0.0` arasında olmalı (FastAPI uyumluluğu için)

## Sorun Giderme

### pytest bulunamıyor hatası:
```powershell
py -3.12 -m pip install pytest pytest-asyncio pytest-cov --user
```

### httpx uyumsuzluk hatası:
```powershell
py -3.12 -m pip install "httpx>=0.25.1,<0.28.0" --upgrade
```

### TestClient hatası:
Eğer hala `TestClient` hatası alıyorsanız:
```powershell
py -3.12 -m pip install "fastapi>=0.104.1" "starlette>=0.27.0" --upgrade
```

