@echo off
cd /d "%~dp0football_scanner_ai"
echo Instalando dependencias...
pip install -r requirements.txt -q
echo Iniciando Football Scanner AI...
python launcher.py
pause
