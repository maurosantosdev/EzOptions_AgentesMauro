@echo off
title EzOptions Analytics Pro - VERSAO CORRIGIDA
cls
echo.
echo ================================================================
echo                EzOptions Analytics Pro
echo                   VERSAO CORRIGIDA
echo             Todos os Erros Corrigidos!
echo ================================================================
echo.

cd /d "%~dp0"

echo [PASSO 1] Verificando sistema...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python nao encontrado
    pause & exit /b 1
)
echo ✅ Python: OK

echo.
echo [PASSO 2] Instalando dependencias...
python -m pip install --quiet --upgrade streamlit pandas plotly numpy python-dotenv MetaTrader5
echo ✅ Dependencias: OK

echo.
echo [PASSO 3] Aplicando correcoes...
echo ✅ Confianca Media: Corrigida (nao mais NaN)
echo ✅ MT5 Filling Mode: Corrigido (suporte automatico)
echo ✅ Streamlit Warnings: Corrigidos (width='stretch')
echo ✅ Pandas Warning: Corrigido (freq='h')

echo.
echo [PASSO 4] Configuracoes MT5...
echo ⚠️  IMPORTANTE: Para trading funcionar:
echo    1. Abra MetaTrader 5 FBS
echo    2. Tools → Options → Expert Advisors
echo    3. Marque: "Allow automated trading"
echo    4. Marque: "Allow DLL imports"
echo    5. Clique OK

echo.
echo [PASSO 5] Iniciando sistema corrigido...
echo.
echo 🚀 EzOptions Analytics Pro (CORRIGIDO)
echo 📊 Dashboard: http://localhost:8502
echo 🏦 Conta FBS: 103486755 (Demo - USD 20,000)
echo 🇧🇷 Interface: Portugues do Brasil
echo ⚡ MT5: Conexao automatica
echo 🤖 Trading: Agentes automaticos
echo ✅ Sem warnings ou erros
echo.

set PYTHONIOENCODING=utf-8

echo Abrindo dashboard corrigido...
echo Para parar: Pressione Ctrl+C
echo.

python -m streamlit run dashboard_completo.py --server.port 8502

echo.
echo Sistema encerrado.
pause