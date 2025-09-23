# -*- coding: utf-8 -*-
"""
TESTE SISTEMA PREDITIVO
======================

Testa a análise preditiva dos agentes:
- Se vai ficar VERDE → COMPRA e PARA SELL
- Se vai ficar VERMELHO → VENDE e PARA BUY
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis
from datetime import datetime

def test_predictive_logic():
    print("=== TESTE SISTEMA PREDITIVO ===")
    print()

    system = MultiAgentTradingSystem()

    # TESTE 1: Mercado vai ficar VERDE (Bullish forte)
    print("[TESTE 1] Cenário que prevê mercado VERDE")
    print("-" * 50)

    market_data_bullish = MarketAnalysis(
        charm_data={'values': [-1.0, -0.5, 0.0, 0.5, 1.0]},   # CHARM crescente forte = VERDE
        delta_data={'values': [0.9, 0.7, 0.5, 0.3, 0.1]},     # DELTA decrescente = bullish
        gamma_data={'values': [300, 350, 400, 450], 'strikes': [15200, 15220, 15240, 15260]},  # GAMMA positivo forte
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 2500, 'average': 1000},        # Volume alto
        price_data={'recent': [15200, 15210, 15220, 15235]},   # Preço subindo
        current_price=15235.0,
        timestamp=datetime.now()
    )

    recommendation1 = system.analyze_market_collaborative(market_data_bullish)

    print(f"Decisao: {recommendation1.decision.value}")
    print(f"Confianca: {recommendation1.confidence:.1f}%")
    print(f"Setup: {recommendation1.setup_type}")

    if recommendation1.decision.value == "BUY" and recommendation1.confidence >= 70:
        print("PREVISAO: MERCADO VAI FICAR VERDE!")
        print("ACAO: COMPRAR e PARAR todos os SELL")
    else:
        print("Previsao incerta ou neutra")

    print()

    # TESTE 2: Mercado vai ficar VERMELHO (Bearish forte)
    print("[TESTE 2] Cenário que prevê mercado VERMELHO")
    print("-" * 50)

    market_data_bearish = MarketAnalysis(
        charm_data={'values': [1.0, 0.5, 0.0, -0.5, -1.0]},   # CHARM decrescente forte = VERMELHO
        delta_data={'values': [0.1, 0.3, 0.6, 0.9, 1.2]},     # DELTA crescente = bearish
        gamma_data={'values': [100, -50, -150, -250], 'strikes': [15200, 15220, 15240, 15260]},  # GAMMA negativo forte
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 2200, 'average': 1000},        # Volume alto
        price_data={'recent': [15250, 15240, 15230, 15215]},   # Preço caindo
        current_price=15215.0,
        timestamp=datetime.now()
    )

    recommendation2 = system.analyze_market_collaborative(market_data_bearish)

    print(f"Decisao: {recommendation2.decision.value}")
    print(f"Confianca: {recommendation2.confidence:.1f}%")
    print(f"Setup: {recommendation2.setup_type}")

    if recommendation2.decision.value == "SELL" and recommendation2.confidence >= 70:
        print("PREVISAO: MERCADO VAI FICAR VERMELHO!")
        print("ACAO: VENDER e PARAR todos os BUY")
    else:
        print("Previsao incerta ou neutra")

    print()
    print("=== RESUMO ===")
    print("O sistema preditivo:")
    print("1. Analisa dados com 10 agentes")
    print("2. Se confianca >= 70%:")
    print("   - BUY = Mercado vai ficar VERDE → COMPRA e PARA SELL")
    print("   - SELL = Mercado vai ficar VERMELHO → VENDE e PARA BUY")
    print("3. Stop Loss: -0.02%")
    print("4. Take Profit: +50%")
    print()
    print("Execute: python predictive_agent_system.py")

if __name__ == "__main__":
    try:
        test_predictive_logic()
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()