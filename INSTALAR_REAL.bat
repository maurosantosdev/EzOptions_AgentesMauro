@echo off
title EzOptions Analytics Pro - Instalacao Completa
echo ============================================================
echo        EzOptions Analytics Pro - Instalacao Completa
echo                    (Trading Real)
echo ============================================================
echo.

echo Instalando todas as dependencias para trading real...
echo.

echo [1/6] Instalando Streamlit...
pip install streamlit --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar Streamlit
    pause
    exit /b 1
)

echo [2/6] Instalando Plotly...
pip install plotly --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar Plotly
    pause
    exit /b 1
)

echo [3/6] Instalando MetaTrader5...
pip install MetaTrader5 --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar MetaTrader5
    pause
    exit /b 1
)

echo [4/6] Instalando yfinance...
pip install yfinance --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar yfinance
    pause
    exit /b 1
)

echo [5/6] Instalando python-dotenv...
pip install python-dotenv --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar python-dotenv
    pause
    exit /b 1
)

echo [6/6] Instalando outras dependencias...
pip install pandas numpy pytz --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias extras
    pause
    exit /b 1
)

echo.
echo ============================================================
echo            INSTALACAO COMPLETA CONCLUIDA!
echo ============================================================
echo.
echo AGORA VOCE TEM ACESSO A:
echo   * Dashboard com dados reais da sua conta MT5
echo   * Conexao FBS-Demo (Login: 103486755)
echo   * Diagnostico completo de trading
echo   * Sistema de agentes com 6 setups
echo.
echo PROXIMOS PASSOS:
echo   1. Abra o MetaTrader 5 FBS
echo   2. Execute: START_REAL.bat
echo   3. O dashboard abrira com seus dados reais
echo.
pause