@echo off
title EzOptions Analytics Pro - Sistema Completo
cls

echo.
echo ============================================================
echo         EzOptions Analytics Pro - Sistema Completo
echo                    TOTALMENTE AUTOMATICO
echo ============================================================
echo.

cd /d "%~dp0"

REM Verificar se Python está disponível
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor instale Python 3.8+ de: https://python.org/downloads/
    echo Certifique-se de marcar "Add Python to PATH" durante a instalacao
    echo.
    pause
    exit /b 1
)
echo [OK] Python encontrado

REM Atualizar pip
echo.
echo [2/5] Atualizando pip...
python -m pip install --upgrade pip --quiet

REM Instalar/Atualizar dependências automaticamente
echo.
echo [3/5] Instalando dependencias necessarias...
echo Esta etapa pode demorar alguns minutos na primeira execucao...

python -m pip install --upgrade streamlit pandas plotly numpy python-dotenv MetaTrader5 --quiet

if errorlevel 1 (
    echo [ERRO] Falha na instalacao das dependencias
    echo.
    echo Tente executar manualmente:
    echo pip install streamlit pandas plotly numpy python-dotenv MetaTrader5
    echo.
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas

REM Verificar arquivos necessários
echo.
echo [4/5] Verificando arquivos...
if not exist "dashboard_completo.py" (
    echo [ERRO] dashboard_completo.py nao encontrado
    pause
    exit /b 1
)

if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado - criando com configuracoes padrao...
    echo MT5_LOGIN=103486755 > .env
    echo MT5_SERVER=FBS-Demo >> .env
    echo MT5_PASSWORD=gPo@j6*V >> .env
    echo MT5_PATH="C:\Program Files\FBS MetaTrader 5\terminal64.exe" >> .env
)

echo [OK] Arquivos verificados

REM Iniciar o sistema
echo.
echo [5/5] Iniciando sistema completo...
echo.
echo O que sera iniciado:
echo   ✓ Dashboard em Portugues do Brasil
echo   ✓ Conexao automatica com MT5
echo   ✓ Agentes de trading automaticos
echo   ✓ 6 setups de trading avancados
echo   ✓ Conta FBS-Demo (USD 20,000.00)
echo.

echo Iniciando em 3 segundos...
timeout /t 3 >nul

echo.
echo ============================================================
echo                    INICIANDO DASHBOARD...
echo ============================================================
echo.

REM Definir codificação UTF-8 para evitar problemas de caracteres
set PYTHONIOENCODING=utf-8

REM Iniciar o dashboard completo
echo [INFO] Abrindo EzOptions Analytics Pro...
echo [INFO] URL: http://localhost:8502
echo.

streamlit run dashboard_completo.py --server.headless false --server.port 8502

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar o dashboard
    echo.
    echo Solucoes:
    echo 1. Verifique se a porta 8502 esta livre
    echo 2. Execute: pip install --upgrade streamlit
    echo 3. Reinicie o prompt de comando como administrador
    echo.
    pause
) else (
    echo.
    echo [INFO] Sistema encerrado normalmente
    echo.
)

pause