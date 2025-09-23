@echo off
title PARAR PREJUÍZO - SELL AGRESSIVO ATIVADO
cls
color 4F
echo.
echo ================================================================
echo                    ⚠️ PARAR PREJUÍZO ⚠️
echo                 SISTEMA SELL AGRESSIVO
echo              Configurado para VENDER RÁPIDO
echo ================================================================
echo.

cd /d "%~dp0"

echo [URGENTE] Sistema configurado para PARAR PREJUÍZO!
echo.

echo [CONFIGURAÇÃO SELL AGRESSIVO]:
echo 🔴 SELL será executado com apenas 2 agentes (vs. 3 anterior)
echo 🔴 SELL tem prioridade mesmo com menos votos
echo 🔴 Agente DELTA: SELL quando DELTA ^> 0.6 (vs. 0.8 anterior)
echo 🔴 Agente CHARM: SELL quando trend ^< -0.2 (vs. -0.5 anterior)
echo 🔴 Agente VWAP: SELL com 95%% confiança em breakout bearish
echo 🔴 Agente PRICE ACTION: SELL com momentum ^< -0.1%% (vs. -0.2%% anterior)
echo 🔴 BUY requer 4+ agentes e força 1.5x maior que SELL
echo.

echo [PROTEÇÃO CONTRA PREJUÍZO]:
echo 💡 Proteção Gamma = SELL (não BUY como antes)
echo 💡 Consolidação = SELL preventivo
echo 💡 Qualquer sinal bearish = SELL IMEDIATO
echo 💡 BUY apenas se extremamente forte
echo.

echo ⚠️  IMPORTANTE: Este sistema foi configurado para ser AGRESSIVO em SELL
echo    O objetivo é PARAR o prejuízo atual e começar a lucrar!
echo.

set /p confirma="CONFIRMA execução do sistema SELL AGRESSIVO? (s/n): "
if /i "%confirma%" neq "s" (
    echo Operação cancelada.
    pause
    exit /b 0
)

echo.
echo [INICIANDO] Sistema SELL AGRESSIVO...
echo.

echo 🎯 EzOptions - MODO PARAR PREJUÍZO
echo 📊 Dashboard: http://localhost:8502
echo 🏦 Conta: FBS-Demo 103486755
echo 🔴 PRIORIDADE: SELL IMEDIATO
echo ⚡ Sensibilidade: MÁXIMA para movimentos bearish
echo 🛡️ Objetivo: PARAR prejuízo e começar a lucrar
echo.

set PYTHONIOENCODING=utf-8

echo ============================================================
echo                   🔴 SELL AGRESSIVO ATIVO 🔴
echo          Os agentes vão VENDER ao menor sinal bearish!
echo ============================================================
echo.
echo Iniciando sistema ANTI-PREJUÍZO...
echo Para parar: Pressione Ctrl+C
echo.

python -m streamlit run dashboard_completo.py --server.port 8502

echo.
echo Sistema SELL AGRESSIVO encerrado.
echo.
echo 📊 Verifique se o prejuízo parou:
echo    - trading_agent.log (ordens SELL executadas)
echo    - MT5 Terminal (P&L atual)
echo.
echo 💰 EXPECTATIVA: Menos BUY, mais SELL, prejuízo controlado!
echo.
pause