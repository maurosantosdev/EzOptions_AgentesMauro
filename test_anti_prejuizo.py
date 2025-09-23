# -*- coding: utf-8 -*-
"""
TESTE ANTI-PREJUIZO - Sistema SELL Agressivo
===========================================

Testa se o sistema agora esta executando SELL corretamente
para PARAR os prejuizos do usuario.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis
from datetime import datetime

def test_sell_agressivo():
    print("=== TESTE ANTI-PREJUIZO - SELL AGRESSIVO ===")
    print()

    # Criar sistema multi-agente
    system = MultiAgentTradingSystem()

    # CENARIO 1: DELTA positivo = deve gerar SELL OBRIGATORIO
    print("[TESTE 1] DELTA POSITIVO (demanda esgotada)")
    print("-" * 50)

    market_data_1 = MarketAnalysis(
        charm_data={'values': [0.1, 0.2, 0.3, 0.4, 0.5]},
        delta_data={'values': [0.1, 0.2, 0.4, 0.6, 0.8]},  # DELTA alto = SELL
        gamma_data={'values': [100, 110, 120, 130], 'strikes': [15200, 15220, 15240, 15260]},
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 1200, 'average': 1000},
        price_data={'recent': [15220, 15225, 15230, 15235]},
        current_price=15235.0,
        timestamp=datetime.now()
    )

    recommendation_1 = system.analyze_market_collaborative(market_data_1)
    print(f"Decisao: {recommendation_1.decision.value}")
    print(f"Confianca: {recommendation_1.confidence:.1f}%")
    print(f"Reasoning: {recommendation_1.reasoning}")

    if recommendation_1.decision.value == "SELL":
        print("[SUCESSO] Sistema detectou SELL corretamente!")
    else:
        print("[PROBLEMA] Sistema NAO detectou SELL - ainda gerando prejuizo!")

    print()

    # CENARIO 2: GAMMA negativo = deve gerar SELL IMEDIATO
    print("[TESTE 2] GAMMA NEGATIVO (perigoso)")
    print("-" * 50)

    market_data_2 = MarketAnalysis(
        charm_data={'values': [0.0, -0.1, -0.2, -0.3, -0.4]},
        delta_data={'values': [0.3, 0.4, 0.5, 0.6, 0.7]},
        gamma_data={'values': [50, -20, -50, -100], 'strikes': [15200, 15220, 15240, 15260]},  # GAMMA negativo
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 800, 'average': 1000},
        price_data={'recent': [15240, 15235, 15230, 15225]},
        current_price=15225.0,
        timestamp=datetime.now()
    )

    recommendation_2 = system.analyze_market_collaborative(market_data_2)
    print(f"Decisao: {recommendation_2.decision.value}")
    print(f"Confianca: {recommendation_2.confidence:.1f}%")
    print(f"Reasoning: {recommendation_2.reasoning}")

    if recommendation_2.decision.value == "SELL":
        print("[SUCESSO] Sistema detectou SELL para GAMMA negativo!")
    else:
        print("[PROBLEMA] Sistema NAO protegeu contra GAMMA negativo!")

    print()

    # CENARIO 3: Sinais neutros = deve gerar SELL PREVENTIVO
    print("[TESTE 3] SINAIS NEUTROS (deve ser SELL preventivo)")
    print("-" * 50)

    market_data_3 = MarketAnalysis(
        charm_data={'values': [0.0, 0.1, 0.0, -0.1, 0.0]},  # Neutro
        delta_data={'values': [0.1, 0.2, 0.1, 0.2, 0.1]},   # Baixo
        gamma_data={'values': [100, 105, 110, 108], 'strikes': [15200, 15220, 15240, 15260]},
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 900, 'average': 1000},  # Volume baixo
        price_data={'recent': [15225, 15226, 15225, 15224]},  # Sideways
        current_price=15225.0,
        timestamp=datetime.now()
    )

    recommendation_3 = system.analyze_market_collaborative(market_data_3)
    print(f"Decisao: {recommendation_3.decision.value}")
    print(f"Confianca: {recommendation_3.confidence:.1f}%")
    print(f"Reasoning: {recommendation_3.reasoning}")

    if recommendation_3.decision.value == "SELL":
        print("[SUCESSO] Sistema fez SELL preventivo!")
    elif recommendation_3.decision.value == "HOLD":
        print("[ACEITAVEL] Sistema em HOLD - melhor que BUY perigoso")
    else:
        print("[PROBLEMA] Sistema ainda fazendo BUY arriscado!")

    print()

    # RESUMO DOS TESTES
    print("=== RESUMO ANTI-PREJUIZO ===")
    sell_count = sum(1 for r in [recommendation_1, recommendation_2, recommendation_3]
                     if r.decision.value == "SELL")

    print(f"Testes realizados: 3")
    print(f"SELLs executados: {sell_count}")
    print(f"Taxa de SELL: {sell_count/3*100:.1f}%")

    if sell_count >= 2:
        print("[SUCESSO] Sistema agora eh AGRESSIVO em SELL!")
        print("Deve PARAR os prejuizos do usuario!")
    elif sell_count == 1:
        print("[PARCIAL] Sistema melhorou mas ainda pode ser mais agressivo")
    else:
        print("[FALHOU] Sistema ainda NAO executa SELL suficiente")
        print("Usuario continuara tendo prejuizo!")

    print()
    print("CONFIGURACOES APLICADAS:")
    print("- Confianca minima: 30% (muito baixa para SELL rapido)")
    print("- DELTA > 0.3 = SELL obrigatorio")
    print("- GAMMA negativo = SELL imediato")
    print("- Qualquer sinal neutro = SELL preventivo")
    print("- Stop Loss: 0.3% (muito proximo)")
    print("- BUY precisa de 6+ agentes com 80%+ confianca")
    print()

if __name__ == "__main__":
    try:
        test_sell_agressivo()
    except Exception as e:
        print(f"[ERRO] Erro no teste: {e}")
        import traceback
        traceback.print_exc()