@echo off
echo ========================================
echo   Hizli Test (Sadece Health)
echo ========================================
echo.

cd /d "%~dp0"

py -3.12 -m pytest tests/test_health.py -v

echo.
echo ========================================
pause

