@echo off
title EzOptions Analytics Pro - SISTEMA MULTI-AGENTE INTELIGENTE
cls
echo.
echo ================================================================
echo          EzOptions Analytics Pro - MULTI-AGENTE
echo              10 Agentes Inteligentes Colaborando
echo                  Sistema de Lucratividade
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
echo [PASSO 2] Instalando dependencias multi-agente...
python -m pip install --quiet --upgrade streamlit pandas plotly numpy python-dotenv MetaTrader5
echo ✅ Dependencias: OK

echo.
echo [PASSO 3] Sistema Multi-Agente configurado:
echo 🤖 Agente 01: Analista CHARM - Detecta força direcional
echo 🤖 Agente 02: Analista DELTA - Detecta demanda/oferta
echo 🤖 Agente 03: Analista GAMMA - Detecta reversões
echo 🤖 Agente 04: Analista VWAP - Confirma breakouts
echo 🤖 Agente 05: Analista Volume - Valida movimentos
echo 🤖 Agente 06: Analista Price Action - Momentum
echo 🤖 Agente 07: Gerente de Risco - Risk/Reward
echo 🤖 Agente 08: Coordenador Setups - 6 setups
echo 🤖 Agente 09: Otimizador Estratégia - Performance
echo 🤖 Agente 10: Tomador Decisão - Consenso final

echo.
echo [PASSO 4] Configurações de trading:
echo 📊 Confiança para análise: ≥90%%
echo 💰 Confiança para operação: ≥60%%
echo 📈 Suporte BUY + SELL automatico
echo ⚖️ Risk/Reward mínimo: 1.5:1
echo 🛡️ Stop Loss automático por setup

echo.
echo [PASSO 5] Estratégia para reverter prejuízo:
echo 🎯 Operação SOMENTE com consenso ≥3 agentes
echo 📊 Análise colaborativa em tempo real
echo 🚀 BUY em setups bullish (1, 4, 6)
echo 📉 SELL em setups bearish (2, 3)
echo ⏸️ HOLD em consolidação (5) até breakout
echo 💎 Gestão inteligente de posições

echo.
echo ⚠️  CONFIGURAÇÃO MT5 OBRIGATÓRIA:
echo    1. MetaTrader 5 FBS deve estar aberto
echo    2. Tools → Options → Expert Advisors
echo    3. ✅ "Allow automated trading"
echo    4. ✅ "Allow DLL imports"

set /p ready="Sistema multi-agente pronto. Pressione ENTER para iniciar: "

echo.
echo [PASSO 6] Iniciando sistema inteligente...
echo.
echo 🚀 EzOptions Multi-Agent System
echo 📊 Dashboard: http://localhost:8502
echo 🏦 Conta: FBS-Demo 103486755 (USD 20,000)
echo 🤖 10 Agentes: Analisando colaborativamente
echo 🧠 IA: Decisões baseadas em consenso
echo 💰 Objetivo: Reverter prejuízo e gerar lucro
echo ⚡ Execução: BUY/SELL automático inteligente

set PYTHONIOENCODING=utf-8

echo.
echo ============================================================
echo          ATENÇÃO: Os agentes irão conversar entre si
echo              e tomar decisões inteligentes!
echo ============================================================
echo.
echo Iniciando dashboard com multi-agentes...
echo Para parar: Pressione Ctrl+C
echo.

python -m streamlit run dashboard_completo.py --server.port 8502

echo.
echo ✅ Sistema multi-agente encerrado.
echo.
echo 📊 Verifique os logs:
echo    - multi_agent_system.log (decisões dos agentes)
echo    - trading_agent.log (execução de trades)
echo.
pause