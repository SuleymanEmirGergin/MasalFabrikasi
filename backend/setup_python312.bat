@echo off
echo ========================================
echo   Python 3.12 Kurulum Scripti
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Python 3.12 versiyonu kontrol ediliyor...
py -3.12 --version
if errorlevel 1 (
    echo HATA: Python 3.12 bulunamadi!
    echo Lutfen Python 3.12'yi kurun: https://www.python.org/downloads/release/python-3120/
    pause
    exit /b 1
)

echo.
echo [2/4] Virtual environment olusturuluyor...
if exist venv (
    echo Virtual environment zaten mevcut, siliniyor...
    rmdir /s /q venv
)
py -3.12 -m venv venv
if errorlevel 1 (
    echo HATA: Virtual environment olusturulamadi!
    pause
    exit /b 1
)

echo.
echo [3/4] pip guncelleniyor...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet

echo.
echo [4/4] Bagimliliklari yukleniyor...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo UYARI: Bazı paketler yuklenemedi. Manuel olarak yuklemeyi deneyin:
    echo venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo.
echo ========================================
echo   Kurulum tamamlandi!
echo ========================================
echo.
echo Virtual environment'i aktiflestirmek icin:
echo   venv\Scripts\activate.bat
echo.
echo Veya testleri calistirmak icin:
echo   venv\Scripts\python.exe -m pytest tests/test_health.py -v
echo.
pause

