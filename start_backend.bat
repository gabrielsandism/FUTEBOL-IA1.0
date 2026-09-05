@echo off
REM Football Scanner AI - Iniciar Backend
REM Este arquivo inicia o servidor FastAPI
REM
REM Como usar:
REM 1. Duplo-clique neste arquivo
REM 2. Deixe a janela aberta
REM 3. Abra start_frontend.bat em OUTRO Prompt
REM 4. Acesse http://localhost:3000

cd /d "%~dp0"

echo.
echo ============================================================
echo   ⚽ Football Scanner AI - Backend
echo ============================================================
echo.
echo Verificando instalacao...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Visite: https://python.org/downloads
    echo Marque "Add Python to PATH" durante a instalacao
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.
echo Iniciando Backend...
echo.

python launcher.py

pause
