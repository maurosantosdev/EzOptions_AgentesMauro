# -*- coding: utf-8 -*-
"""
Teste do Sistema SELL Agressivo
==============================

Verifica se os agentes estão priorizando SELL corretamente
"""

from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis
from datetime import datetime
import numpy as np

def test_sell_aggressive():
    print("=== TESTE DO SISTEMA SELL AGRESSIVO ===")
    print()

    # Criar sistema multi-agente
    system = MultiAgentTradingSystem()

    # CENÁRIO 1: Mercado com sinais bearish (deve gerar SELL)
    print("🔴 CENÁRIO 1: Sinais Bearish - Deve gerar SELL")
    market_data_bearish = MarketAnalysis(
        charm_data={'values': [0.5, 0.2, -0.1, -0.8, -1.2]},  # CHARM decrescente forte
        delta_data={'values': [0.2, 0.4, 0.6, 0.7, 0.8]},     # DELTA alto (demanda esgotada)
        gamma_data={'values': [100, 80, 60, 40], 'strikes': [15180, 15200, 15220, 15240]},
        vwap_data={'vwap': 15220, 'std1_upper': 15230, 'std1_lower': 15210, 'std2_lower': 15200},
        volume_data={'current': 1800, 'average': 1000},        # Volume alto
        price_data={'recent': [15225, 15220, 15215, 15205]},   # Preço caindo
        current_price=15205.0,  # Preço abaixo da VWAP
        timestamp=datetime.now()
    )

    recommendation = system.analyze_market_collaborative(market_data_bearish)
    print(f"DECISÃO: {recommendation.decision.value}")
    print(f"CONFIANÇA: {recommendation.confidence:.1f}%")
    print(f"SETUP: {recommendation.setup_type}")
    print(f"REASONING: {recommendation.reasoning}")
    print()

    # CENÁRIO 2: Mercado com sinais bullish fracos (deve gerar HOLD ou SELL preventivo)
    print("🟡 CENÁRIO 2: Sinais Bullish Fracos - Deve evitar BUY")
    market_data_weak_bull = MarketAnalysis(
        charm_data={'values': [-0.2, -0.1, 0.1, 0.3, 0.4]},   # CHARM crescente fraco
        delta_data={'values': [0.1, 0.2, 0.3, 0.4, 0.5]},     # DELTA moderado
        gamma_data={'values': [100, 110, 120, 130], 'strikes': [15200, 15220, 15240, 15260]},
        vwap_data={'vwap': 15230, 'std1_upper': 15240, 'std1_lower': 15220},
        volume_data={'current': 900, 'average': 1000},         # Volume baixo
        price_data={'recent': [15230, 15232, 15235, 15237]},   # Subida fraca
        current_price=15237.0,
        timestamp=datetime.now()
    )

    recommendation2 = system.analyze_market_collaborative(market_data_weak_bull)
    print(f"DECISÃO: {recommendation2.decision.value}")
    print(f"CONFIANÇA: {recommendation2.confidence:.1f}%")
    print(f"SETUP: {recommendation2.setup_type}")
    print(f"REASONING: {recommendation2.reasoning}")
    print()

    # CENÁRIO 3: Mercado com sinais bullish muito fortes (deve permitir BUY)
    print("🟢 CENÁRIO 3: Sinais Bullish MUITO Fortes - Pode permitir BUY")
    market_data_strong_bull = MarketAnalysis(
        charm_data={'values': [-0.8, -0.4, 0.2, 0.8, 1.5]},   # CHARM crescente muito forte
        delta_data={'values': [0.1, -0.2, -0.4, -0.6, -0.8]}, # DELTA negativo (oferta esgotada)
        gamma_data={'values': [100, 150, 200, 250], 'strikes': [15200, 15220, 15240, 15260]},
        vwap_data={'vwap': 15230, 'std1_upper': 15240, 'std1_lower': 15220, 'std2_upper': 15250},
        volume_data={'current': 2000, 'average': 1000},        # Volume muito alto
        price_data={'recent': [15220, 15235, 15245, 15255]},   # Subida forte
        current_price=15255.0,  # Acima do 2º desvio
        timestamp=datetime.now()
    )

    recommendation3 = system.analyze_market_collaborative(market_data_strong_bull)
    print(f"DECISÃO: {recommendation3.decision.value}")
    print(f"CONFIANÇA: {recommendation3.confidence:.1f}%")
    print(f"SETUP: {recommendation3.setup_type}")
    print(f"REASONING: {recommendation3.reasoning}")
    print()

    # RESUMO
    print("=== RESUMO DO TESTE ===")
    cenarios = [
        ("Bearish", recommendation.decision.value),
        ("Bullish Fraco", recommendation2.decision.value),
        ("Bullish Forte", recommendation3.decision.value)
    ]

    for cenario, decisao in cenarios:
        status = "✅ CORRETO" if (
            (cenario == "Bearish" and decisao == "SELL") or
            (cenario == "Bullish Fraco" and decisao in ["HOLD", "SELL"]) or
            (cenario == "Bullish Forte" and decisao in ["BUY", "HOLD"])
        ) else "❌ PROBLEMA"

        print(f"{cenario}: {decisao} - {status}")

    print()
    print("🎯 SISTEMA CONFIGURADO PARA:")
    print("   - SELL AGRESSIVO em sinais bearish")
    print("   - EVITAR BUY em sinais fracos")
    print("   - BUY apenas em sinais MUITO fortes")
    print("   - PARAR PREJUÍZO prioritariamente")

if __name__ == "__main__":
    test_sell_aggressive()