@echo off
title EzOptions Analytics Pro - VERSAO FINAL
cls
echo.
echo ================================================================
echo                EzOptions Analytics Pro
echo                     VERSAO FINAL
echo                  Sistema Automatico
echo ================================================================
echo.

REM Ir para o diretório do arquivo
cd /d "%~dp0"

echo [PASSO 1] Verificando sistema...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERRO: Python nao encontrado
    echo.
    echo SOLUCAO:
    echo 1. Baixe Python em: https://python.org/downloads/
    echo 2. Durante instalacao, marque "Add Python to PATH"
    echo 3. Reinicie o computador
    echo 4. Execute este arquivo novamente
    echo.
    pause
    exit /b 1
)
echo ✅ Python: OK

echo.
echo [PASSO 2] Instalando dependencias...
echo (Esta etapa demora ~2 minutos na primeira vez)

python -m pip install --quiet --upgrade streamlit pandas plotly numpy python-dotenv MetaTrader5

echo ✅ Dependencias: OK

echo.
echo [PASSO 3] Verificando arquivos...
if not exist "dashboard_completo.py" (
    echo ❌ ERRO: dashboard_completo.py nao encontrado
    pause
    exit /b 1
)
echo ✅ Arquivos: OK

echo.
echo [PASSO 4] Iniciando sistema...
echo.
echo 🚀 EzOptions Analytics Pro
echo 📊 Dashboard: http://localhost:8502
echo 🏦 Conta FBS: 103486755 (Demo - USD 20,000)
echo 🇧🇷 Idioma: Portugues do Brasil
echo ⚡ MT5: Conexao automatica
echo 🤖 Trading: Agentes automaticos
echo.

set PYTHONIOENCODING=utf-8

echo Abrindo dashboard...
echo Para parar o sistema: Pressione Ctrl+C
echo.

python -m streamlit run dashboard_completo.py --server.port 8502

echo.
echo Sistema encerrado.
pause