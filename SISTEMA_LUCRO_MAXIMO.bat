@echo off
title EzOptions Analytics Pro - SISTEMA DE LUCRO MÁXIMO
cls
echo.
echo ================================================================
echo          EzOptions Analytics Pro - LUCRO MÁXIMO
echo              10 Agentes Otimizados Para Lucro
echo                Sistema de Alta Performance
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
echo [PASSO 2] Instalando dependencias otimizadas...
python -m pip install --quiet --upgrade streamlit pandas plotly numpy python-dotenv MetaTrader5
echo ✅ Dependencias: OK

echo.
echo [PASSO 3] Sistema Otimizado Para LUCRO MÁXIMO:
echo 💰 Objetivo: Gerar lucro consistente e crescente
echo 📈 Estratégia: BUY + SELL em todos os setups
echo ⚡ Performance: 5-8 trades/dia (vs. 1-2 anterior)
echo 🎯 R/R Target: 2.0:1 mínimo (vs. 1.5:1 anterior)
echo 🛡️ Stop Loss: 1.5 ATR (mais apertado = menor risco)
echo 💎 Take Profit: 3.5 ATR (maior = mais lucro)

echo.
echo [PASSO 4] Configurações de Lucratividade:
echo 🎯 Win Rate Alvo: 75%% (vs. 50%% anterior)
echo 💰 Lucro Semanal Meta: +$60-80
echo 📊 Lucro Mensal Meta: +$250-320
echo 🚀 Crescimento: +15%% mês a mês
echo 🔄 Auto-Otimização: Sistema aprende e melhora

echo.
echo [PASSO 5] Vantagens do Sistema Multi-Agente:
echo 🤖 10 Agentes analisando simultaneamente
echo 🧠 Decisões baseadas em consenso inteligente
echo ⚡ Execução instantânea de oportunidades
echo 📊 Cobertura 100%% do mercado (BUY+SELL)
echo 🛡️ Gestão automática de risco
echo 💡 Aprendizado contínuo de performance

echo.
echo [PASSO 6] Setups Otimizados para Lucro:
echo 🚀 Setup 1 (Bullish Breakout) → BUY Agressivo
echo 📉 Setup 2 (Bearish Breakout) → SELL Agressivo
echo 📉 Setup 3 (Pullback Top) → SELL Preciso
echo 🚀 Setup 4 (Pullback Bottom) → BUY Preciso
echo ⏸️ Setup 5 (Consolidado) → Aguarda breakout para entrada explosiva
echo 🛡️ Setup 6 (Proteção Gamma) → BUY Defensivo + lucrativo

echo.
echo ⚠️  CONFIGURAÇÃO OBRIGATÓRIA MT5:
echo    1. MetaTrader 5 FBS aberto e logado
echo    2. Tools → Options → Expert Advisors
echo    3. ✅ "Allow automated trading"
echo    4. ✅ "Allow DLL imports"
echo    5. ✅ Verificar saldo disponível

set /p ready="Sistema de LUCRO MÁXIMO pronto. Pressione ENTER para iniciar: "

echo.
echo [PASSO 7] Iniciando sistema de alta performance...
echo.
echo 🎯 EzOptions LUCRO MÁXIMO System
echo 📊 Dashboard: http://localhost:8502
echo 🏦 Conta: FBS-Demo 103486755 (USD 20,000)
echo 🤖 10 Agentes: Otimizados para LUCRO
echo 💰 Meta Diária: +$12-15 (vs. anterior: -$2-3)
echo 📈 Meta Semanal: +$60-80
echo 🚀 Meta Mensal: +$250-320
echo ⚡ Trades/Dia: 5-8 (máxima cobertura)

set PYTHONIOENCODING=utf-8

echo.
echo ============================================================
echo               ATENÇÃO: SISTEMA DE LUCRO ATIVO
echo          Os agentes irão MAXIMIZAR cada oportunidade!
echo ============================================================
echo.
echo Iniciando sistema otimizado para LUCRO MÁXIMO...
echo Para parar: Pressione Ctrl+C
echo.

python -m streamlit run dashboard_completo.py --server.port 8502

echo.
echo ✅ Sistema de LUCRO MÁXIMO encerrado.
echo.
echo 📊 Relatórios de Performance:
echo    - multi_agent_system.log (decisões dos agentes)
echo    - trading_agent.log (trades executados)
echo.
echo 💰 Verifique seu P&L no MT5 - Meta: LUCRO CRESCENTE!
echo.
pause