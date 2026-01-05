@echo off
REM Basit test calistirma scripti - backend dizininde calisir
cd /d "%~dp0"
echo Testler calistiriliyor...
py -3.12 -m pytest tests/test_health.py -v
pause

