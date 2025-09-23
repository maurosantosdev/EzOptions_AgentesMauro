@echo off
title EzOptions Analytics Pro - Real Trading
echo ============================================================
echo        EzOptions Analytics Pro - Real Trading
echo              Conectando com MT5 FBS-Demo
echo ============================================================
echo.

cd /d "%~dp0"

echo Verificando MetaTrader 5...
tasklist | findstr "terminal64.exe" >nul
if errorlevel 1 (
    echo.
    echo ⚠️  AVISO: MetaTrader 5 nao detectado rodando
    echo    Certifique-se de que o MT5 esta aberto
    echo.
    pause
)

echo Iniciando dashboard com dados reais...
streamlit run real_dashboard.py --server.headless true

pause