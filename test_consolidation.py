# -*- coding: utf-8 -*-
"""
TESTE DETECCAO DE CONSOLIDACAO
=============================

Testa se o sistema detecta mercado consolidado e NAO opera.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis
from datetime import datetime

def test_consolidation_detection():
    print("=== TESTE DETECCAO DE CONSOLIDACAO ===")
    print()

    system = MultiAgentTradingSystem()

    # TESTE: Mercado CONSOLIDADO (sinais conflitantes, baixa volatilidade)
    print("[TESTE] Cenario de mercado CONSOLIDADO")
    print("-" * 50)

    market_data_consolidation = MarketAnalysis(
        charm_data={'values': [0.1, -0.1, 0.05, -0.05, 0.0]},  # CHARM oscilando perto de zero
        delta_data={'values': [0.5, 0.52, 0.48, 0.51, 0.49]},  # DELTA estavel, pouca mudanca
        gamma_data={'values': [50, 45, 55, 48, 52], 'strikes': [15200, 15220, 15240, 15260]},  # GAMMA baixo e estavel
        vwap_data={'vwap': 15225, 'std1_upper': 15228, 'std1_lower': 15222},  # Bandas muito estreitas = baixa volatilidade
        volume_data={'current': 800, 'average': 1000},          # Volume baixo
        price_data={'recent': [15223, 15225, 15224, 15225]},    # Preco oscilando numa faixa estreita
        current_price=15225.0,
        timestamp=datetime.now()
    )

    recommendation = system.analyze_market_collaborative(market_data_consolidation)

    print(f"Decisao: {recommendation.decision.value}")
    print(f"Confianca: {recommendation.confidence:.1f}%")
    print(f"Setup: {recommendation.setup_type}")

    # Verificar se detecta consolidacao
    is_consolidated = (
        recommendation.confidence < 40 or  # Baixa confianca
        "CONSOLIDAT" in recommendation.setup_type.upper() or
        "SETUP5" in recommendation.setup_type or
        recommendation.decision.value == "HOLD"
    )

    if is_consolidated:
        print()
        print("STATUS: MERCADO CONSOLIDADO DETECTADO!")
        print("ACAO: NAO OPERAR - Aguardando breakout")
        print("Motivo: Sinais conflitantes ou faixa de negociacao estreita")
        print()
        print("SISTEMA FUNCIONANDO CORRETAMENTE!")
    else:
        print()
        print("PROBLEMA: Nao detectou consolidacao")
        print("Sistema deve evitar operar nesse cenario")

    print()
    print("=== CRITERIOS DE CONSOLIDACAO ===")
    print("1. Confianca < 40% (sinais conflitantes)")
    print("2. Setup = SETUP5_CONSOLIDATED")
    print("3. Decisao = HOLD")
    print("4. CHARM perto de zero (sem direcao)")
    print("5. DELTA estavel (pouca mudanca)")
    print("6. Preco em faixa estreita")

if __name__ == "__main__":
    try:
        test_consolidation_detection()
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()