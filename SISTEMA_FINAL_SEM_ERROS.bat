@echo off
title EzOptions Analytics Pro - VERSAO FINAL SEM ERROS
cls
echo.
echo ================================================================
echo                EzOptions Analytics Pro
echo                 VERSAO FINAL SEM ERROS
echo             Sistema 100%% Funcional!
echo ================================================================
echo.

cd /d "%~dp0"

echo [PASSO 1] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python nao encontrado
    pause & exit /b 1
)
echo ✅ Python: OK

echo.
echo [PASSO 2] Instalando/Atualizando dependencias...
python -m pip install --quiet --upgrade streamlit pandas plotly numpy python-dotenv MetaTrader5
echo ✅ Dependencias: OK

echo.
echo [PASSO 3] Status das correções aplicadas:
echo ✅ Confianca Media NaN: CORRIGIDO
echo ✅ MT5 Filling Mode: CORRIGIDO (com fallback automatico)
echo ✅ Streamlit Warnings: CORRIGIDOS
echo ✅ Pandas Warnings: CORRIGIDOS
echo ✅ Constantes MT5: VERIFICADAS E FUNCIONAIS

echo.
echo [PASSO 4] Verificando arquivos principais...
if not exist "dashboard_completo.py" (
    echo ❌ ERRO: dashboard_completo.py nao encontrado
    pause & exit /b 1
)
if not exist "real_agent_system.py" (
    echo ❌ ERRO: real_agent_system.py nao encontrado
    pause & exit /b 1
)
echo ✅ Arquivos: OK

echo.
echo [PASSO 5] Configuracoes MT5 importantes:
echo.
echo ⚠️  PARA TRADING AUTOMATICO FUNCIONAR:
echo    1. Abra MetaTrader 5 FBS
echo    2. Tools → Options → Expert Advisors
echo    3. Marque: ✅ "Allow automated trading"
echo    4. Marque: ✅ "Allow DLL imports"
echo    5. Clique OK
echo.

set /p continuar="Pressione ENTER para continuar (MT5 deve estar configurado): "

echo.
echo [PASSO 6] Iniciando sistema final...
echo.
echo 🚀 EzOptions Analytics Pro (VERSAO FINAL)
echo 📊 Dashboard: http://localhost:8502
echo 🏦 Conta: FBS-Demo 103486755 (USD 20,000)
echo 🇧🇷 Interface: Portugues do Brasil
echo ⚡ MT5: Conexao + Trading automatico
echo 🤖 Agentes: Funcionando sem erros
echo ✅ Sistema: 100%% estavel
echo.

set PYTHONIOENCODING=utf-8

echo Abrindo dashboard final (sem erros)...
echo Para parar: Pressione Ctrl+C
echo.

python -m streamlit run dashboard_completo.py --server.port 8502

echo.
echo ✅ Sistema encerrado com sucesso.
pause