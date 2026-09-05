@echo off
echo ============================================================
echo   Football Scanner AI - Build Script (Windows)
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+
    pause
    exit /b 1
)

:: Install dependencies
echo [1/3] Instalando dependencias...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

:: Run tests
echo [2/3] Executando testes...
python -m pytest tests/ -q
if errorlevel 1 (
    echo [AVISO] Alguns testes falharam. Continuando build...
)

:: Build executable
echo [3/3] Gerando executavel...
pyinstaller FootballScannerAI.spec --clean --noconfirm

echo.
echo ============================================================
echo   Build concluido!
echo   Executavel: dist\FootballScannerAI\FootballScannerAI.exe
echo ============================================================
pause
