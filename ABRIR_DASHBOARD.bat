@echo off
echo ============================================================
echo           EzOptions Analytics Pro - Launcher
echo ============================================================
echo.

cd /d "%~dp0"

echo Verificando diretorio...
dir /b *.py | findstr "abrir_dashboard.py" >nul
if errorlevel 1 (
    echo ERRO: Arquivo abrir_dashboard.py nao encontrado!
    pause
    exit /b 1
)

echo Iniciando dashboard...
echo.
python abrir_dashboard.py

echo.
echo Dashboard finalizado.
pause