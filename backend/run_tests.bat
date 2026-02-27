@echo off
echo ========================================
echo   Masal Fabrikasi - Test Runner
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Testler baslatiliyor...
echo.

py -3.12 -m pytest tests/ -v --tb=short -x --disable-warnings

echo.
echo ========================================
echo   Testler tamamlandi!
echo ========================================
pause

