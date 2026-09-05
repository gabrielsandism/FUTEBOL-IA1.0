@echo off
REM Football Scanner AI - Iniciar Frontend
REM Este arquivo inicia o servidor Next.js React
REM
REM IMPORTANTE: Rode start_backend.bat PRIMEIRO em outro Prompt!
REM
REM Como usar:
REM 1. Abra um NOVO Prompt (nao feche o anterior)
REM 2. Duplo-clique neste arquivo
REM 3. Espere aparecer "Ready in X.Xs"
REM 4. Seu navegador abrira em http://localhost:3000

cd /d "%~dp0frontend-react"

echo.
echo ============================================================
echo   ⚽ Football Scanner AI - Frontend
echo ============================================================
echo.
echo Verificando instalacao...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado!
    echo.
    echo Visite: https://nodejs.org/
    echo Instale a versao LTS
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
echo.
echo Instalando dependencias (primeira vez apenas)...
if not exist "node_modules" (
    call npm install -q
)

echo.
echo Iniciando Frontend em http://localhost:3000...
echo.

call npm run dev

pause
