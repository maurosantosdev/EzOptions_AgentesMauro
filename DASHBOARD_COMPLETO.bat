@echo off
title EzOptions Analytics Pro - Sistema Completo
cls

echo.
echo ========================================================
echo         EzOptions Analytics Pro - Sistema Completo
echo ========================================================
echo.

REM Verificar se Python está disponível
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH
    echo.
    echo Instale Python 3.8+ e adicione ao PATH do sistema
    echo Download: https://python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar arquivos principais
if not exist "dashboard_completo.py" (
    echo [ERRO] Arquivo dashboard_completo.py nao encontrado
    pause
    exit /b 1
)

if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado - criando padrao...
    echo MT5_LOGIN=103486755 > .env
    echo MT5_SERVER=FBS-Demo >> .env
    echo MT5_PASSWORD=gPo@j6*V >> .env
    echo MT5_PATH="C:\Program Files\FBS MetaTrader 5\terminal64.exe" >> .env
    echo.
    echo [OK] Arquivo .env criado com configuracoes padrao
    echo.
)

REM Verificar/Instalar dependências
echo [INFO] Verificando dependencias...
pip install -q streamlit pandas plotly numpy python-dotenv MetaTrader5

echo.
echo [INFO] Iniciando sistema automatico...
echo.
echo - MT5 sera conectado automaticamente
echo - Agentes serao iniciados automaticamente
echo - Interface em Portugues do Brasil
echo - Dados reais da conta FBS-Demo
echo.

REM Iniciar dashboard completo
echo [INFO] Abrindo dashboard completo...
echo.

streamlit run dashboard_completo.py --server.headless false --server.port 8502

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar o dashboard
    echo.
    echo Verifique se:
    echo 1. MetaTrader 5 esta instalado
    echo 2. Conta FBS configurada corretamente
    echo 3. Todas as dependencias estao instaladas
    echo.
    pause
) else (
    echo.
    echo [INFO] Dashboard encerrado com sucesso
    echo.
)

pause