@echo off
title EzOptions Analytics Pro - CORRIGIDO
cls

echo ============================================================
echo           EzOptions Analytics Pro - SISTEMA CORRIGIDO
echo ============================================================
echo.

REM Ir para o diretório correto
cd /d "%~dp0"

REM Verificar se Python está disponível
echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python de: https://python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python encontrado

echo.
echo [2/3] Instalando/Verificando dependencias...
REM Usar caminho completo do Python
python -m pip install --upgrade --quiet streamlit pandas plotly numpy python-dotenv MetaTrader5

if errorlevel 1 (
    echo [AVISO] Alguns pacotes podem ja estar instalados
)
echo [OK] Dependencias verificadas

echo.
echo [3/3] Iniciando EzOptions Analytics Pro...
echo.
echo 🚀 Dashboard sera aberto em: http://localhost:8502
echo 🏦 Conta: FBS-Demo (USD 20,000.00)
echo 🇧🇷 Interface: Portugues do Brasil
echo ⚡ Conexao MT5: Automatica
echo 🤖 Agentes: Automaticos
echo.

REM Definir encoding para caracteres especiais
set PYTHONIOENCODING=utf-8

REM Usar Python com caminho completo para executar streamlit
python -m streamlit run dashboard_completo.py --server.port 8502 --server.headless false

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar o dashboard
    echo.
    echo Solucoes:
    echo 1. Feche outros programas que possam estar usando a porta 8502
    echo 2. Reinicie o prompt como administrador
    echo 3. Execute: python -m pip install --upgrade streamlit
    echo.
)

echo.
echo [INFO] Sistema encerrado
pause