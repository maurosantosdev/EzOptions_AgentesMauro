@echo off
title EzOptions Analytics Pro - Sistema Completo
color 0A
echo ============================================================
echo         EzOptions Analytics Pro - Sistema Completo
echo                    TRADING AUTOMATICO
echo ============================================================
echo.

cd /d "%~dp0"

echo [INFO] Verificando e instalando dependencias...
echo Esta etapa pode demorar alguns minutos na primeira vez...
echo.

REM Instalar dependencias automaticamente
python -m pip install --upgrade pip --quiet
python -m pip install streamlit pandas plotly numpy python-dotenv MetaTrader5 --quiet

if errorlevel 1 (
    echo [ERRO] Falha na instalacao das dependencias
    echo Execute manualmente: pip install streamlit pandas plotly numpy python-dotenv MetaTrader5
    pause
    exit /b 1
)

echo ✅ Dependencias OK
echo.

echo 🔍 Verificando MetaTrader 5...
tasklist | findstr "terminal64.exe" >nul
if errorlevel 1 (
    echo.
    echo ⚠️  MetaTrader 5 nao detectado
    echo    Abra o MT5 FBS primeiro
    echo.
    set /p choice="Continuar mesmo assim? (s/n): "
    if /i "%choice%" neq "s" exit /b 1
)

echo ✅ MT5 detectado
echo.

echo 🚀 Iniciando sistema completo...
echo.
echo Componentes que serao iniciados:
echo   • Dashboard Web (http://localhost:8501)
echo   • Agentes de Trading Automatico
echo   • Sistema de 6 Setups Avancados
echo   • Conexao Real com FBS-Demo
echo.

set /p choice="Iniciar sistema completo? (s/n): "
if /i "%choice%" neq "s" (
    echo Operacao cancelada.
    pause
    exit /b 0
)

echo.
echo ============================================================
echo                    INICIANDO SISTEMA...
echo ============================================================
echo.

echo [INFO] Iniciando Dashboard Completo em Portugues...
echo [INFO] URL: http://localhost:8502
echo.

REM Definir encoding UTF-8
set PYTHONIOENCODING=utf-8

REM Usar o dashboard completo em portugues
streamlit run dashboard_completo.py --server.headless false --server.port 8502

echo.
echo ============================================================
echo                 SISTEMA INICIADO COM SUCESSO!
echo ============================================================
echo.
echo [INFO] Dashboard iniciado com sucesso!
echo [INFO] URL: http://localhost:8502
echo [INFO] Conta: FBS-Demo (103486755)
echo [INFO] Tudo em Portugues do Brasil!
echo.
echo Para parar o sistema, pressione Ctrl+C
echo.
pause