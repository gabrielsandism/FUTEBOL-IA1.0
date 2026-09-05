@echo off
echo ============================================================
echo   Football Scanner AI - Instalador Windows
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python 3.10+ em https://python.org/downloads
    echo Marque "Add to PATH" durante a instalacao
    pause
    exit /b 1
)

echo [1/2] Instalando dependencias...
pip install -r requirements.txt -q
echo [2/2] Pronto!

echo.
echo Para iniciar: python launcher.py
echo Ou execute: start.bat
echo.
pause
