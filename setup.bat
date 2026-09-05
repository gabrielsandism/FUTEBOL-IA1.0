@echo off
REM Football Scanner AI - Setup Completo
REM Execute este arquivo para fazer instalacao automatica
REM Precisa rodar apenas UMA VEZ

cls

echo.
echo ============================================================
echo   ⚽ Football Scanner AI - Setup Inicial
echo ============================================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Visite: https://python.org/downloads
    echo Baixe a versao 3.10 ou superior
    echo IMPORTANTE: Marque "Add Python to PATH" durante a instalacao!
    echo.
    pause
    exit /b 1
)
echo [OK] Python instalado

REM Verificar Node.js
echo [2/5] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado!
    echo.
    echo Visite: https://nodejs.org/
    echo Baixe a versao LTS
    echo.
    pause
    exit /b 1
)
echo [OK] Node.js instalado

REM Instalar dependencias Python
echo [3/5] Instalando dependencias Python...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERRO] Falha na instalacao de dependencias Python
    pause
    exit /b 1
)
echo [OK] Dependencias Python instaladas

REM Instalar dependencias Frontend
echo [4/5] Instalando dependencias Frontend...
cd frontend-react
call npm install -q
if errorlevel 1 (
    echo [ERRO] Falha na instalacao de dependencias Frontend
    pause
    exit /b 1
)
echo [OK] Dependencias Frontend instaladas
cd ..

REM Criar estrutura de pastas
echo [5/5] Criando estrutura do projeto...
if not exist "data" mkdir data
if not exist "data\backtest" mkdir data\backtest
if not exist "data\historical" mkdir data\historical
echo [OK] Estrutura criada

echo.
echo ============================================================
echo   ✓ SETUP CONCLUIDO COM SUCESSO!
echo ============================================================
echo.
echo Proximos passos:
echo.
echo 1. Abra um Prompt de Comando
echo    Digite: start_backend.bat
echo.
echo 2. Abra OUTRO Prompt de Comando
echo    Digite: start_frontend.bat
echo.
echo 3. Acesse no navegador:
echo    http://localhost:3000
echo.
echo ============================================================
echo.
pause
