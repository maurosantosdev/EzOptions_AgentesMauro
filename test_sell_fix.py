# -*- coding: utf-8 -*-
"""
TESTE URGENTE - SELL FUNCIONANDO
===============================

Testa se agora quando Multi-Agente decide SELL, o sistema executa SELL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis, TradingDecision
from datetime import datetime

def test_sell_execution():
    print("=== TESTE URGENTE - SELL FUNCIONANDO ===")
    print()

    # Criar sistema multi-agente
    system = MultiAgentTradingSystem()

    # CENÁRIO BEARISH FORTE - deve gerar SELL
    print("[TESTE] Cenário BEARISH forte - deve executar SELL")
    print("-" * 50)

    market_data_bearish = MarketAnalysis(
        charm_data={'values': [1.0, 0.5, 0.0, -0.5, -1.0]},  # CHARM decrescente forte
        delta_data={'values': [0.8, 0.9, 1.0, 1.1, 1.2]},    # DELTA alto = bearish
        gamma_data={'values': [100, -50, -100, -200], 'strikes': [15200, 15220, 15240, 15260]},  # GAMMA negativo
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 2000, 'average': 1000},       # Volume alto
        price_data={'recent': [15280, 15260, 15240, 15220]},  # Preço caindo forte
        current_price=15220.0,
        timestamp=datetime.now()
    )

    # Testar multi-agente
    recommendation = system.analyze_market_collaborative(market_data_bearish)

    print(f"Decisao Multi-Agente: {recommendation.decision.value}")
    print(f"Confianca: {recommendation.confidence:.1f}%")
    print(f"Setup detectado: {recommendation.setup_type}")
    print()

    if recommendation.decision.value == "SELL":
        print("✅ [SUCESSO] Agentes Multi-Agente decidem SELL corretamente!")
        print("Agora o sistema deve executar SELL (não mais BUY)")
    else:
        print("❌ [PROBLEMA] Agentes ainda não decidem SELL em cenário bearish")
        print(f"Decisão: {recommendation.decision.value} - deveria ser SELL")

    print()
    print("=== PRÓXIMO PASSO ===")
    print("Execute o sistema real e veja nos logs:")
    print("- 'AGENTES DECIDEM: SELL'")
    print("- 'ORDENS EXECUTADAS: SELL - Agentes Multi-Agente'")
    print("- Deve executar sell 0.01 US100 (não mais buy)")
    print()

if __name__ == "__main__":
    try:
        test_sell_execution()
    except Exception as e:
        print(f"[ERRO] Erro no teste: {e}")
        import traceback
        traceback.print_exc()