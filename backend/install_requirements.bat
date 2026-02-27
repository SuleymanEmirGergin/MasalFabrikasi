@echo off
echo ========================================
echo   Bagimliliklari Yukleme (Python 3.12)
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] pip guncelleniyor...
py -3.12 -m pip install --upgrade pip --quiet

echo.
echo [2/3] Pre-built wheel'lerle paketler yukleniyor...
echo (Rust gerekmeden calisir)

REM Oncelikle pre-built wheel'leri kullanarak tokenizers'i yukle
py -3.12 -m pip install --only-binary :all: tokenizers --quiet
if errorlevel 1 (
    echo UYARI: tokenizers pre-built wheel ile yuklenemedi, normal mod deneniyor...
    py -3.12 -m pip install tokenizers --quiet
)

echo.
echo [3/3] Diger bagimliliklar yukleniyor...
REM googletrans kaldirildi (httpx uyumsuzlugu nedeniyle)
py -3.12 -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo UYARI: Bazı paketler yuklenemedi. Tekrar deniyoruz (Rust olmadan)...
    py -3.12 -m pip install -r requirements.txt --no-build-isolation
)

echo.
echo NOT: googletrans paketi kaldirildi (httpx uyumsuzlugu nedeniyle)
echo       Ceviri servisleri OpenAI kullaniyor, googletrans gerekli degil.

echo.
echo ========================================
echo   Yukleme tamamlandi!
echo ========================================
echo.
echo Testleri calistirmak icin:
echo   py -3.12 -m pytest tests/test_health.py -v
echo.
pause

