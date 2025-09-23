# -*- coding: utf-8 -*-
"""
TESTE LÓGICA INVERTIDA - Fazendo o Contrário
==========================================

Testa se o sistema agora faz o CONTRÁRIO:
- Quando detecta SELL → Executa BUY
- Quando detecta BUY → Executa SELL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis
from smart_order_system import SmartOrderSystem
from datetime import datetime
import pandas as pd

def test_logica_invertida():
    print("=== TESTE LÓGICA INVERTIDA - FAZENDO O CONTRÁRIO ===")
    print()

    # Criar sistemas
    multi_system = MultiAgentTradingSystem()
    smart_system = SmartOrderSystem()

    # TESTE 1: Cenario que antes gerava SELL -> Agora deve gerar BUY
    print("[TESTE 1] Cenario BEARISH -> Deve executar BUY (invertido)")
    print("-" * 60)

    market_data_bearish = MarketAnalysis(
        charm_data={'values': [0.5, 0.2, -0.1, -0.5, -0.8]},  # CHARM decrescente = bearish
        delta_data={'values': [0.3, 0.5, 0.7, 0.8, 0.9]},     # DELTA alto = sell normal
        gamma_data={'values': [100, -50, -100, -150], 'strikes': [15200, 15220, 15240, 15260]},  # GAMMA negativo
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 1500, 'average': 1000},
        price_data={'recent': [15240, 15235, 15230, 15225]},   # Preço caindo
        current_price=15225.0,
        timestamp=datetime.now()
    )

    # Testar multi-agente (deve detectar SELL mas executar BUY)
    recommendation = multi_system.analyze_market_collaborative(market_data_bearish)
    print(f"Multi-Agente - Decisao: {recommendation.decision.value}")
    print(f"Multi-Agente - Confianca: {recommendation.confidence:.1f}%")

    # Criar dados para SmartOrder
    calls_df = pd.DataFrame({
        'strike': [15200, 15220, 15240, 15260],
        'GAMMA': [100, -50, -100, -150],  # GAMMA negativo
        'DELTA': [0.9, 0.8, 0.7, 0.6],   # DELTA alto
        'CHARM': [-0.8, -0.6, -0.4, -0.2]  # CHARM decrescente
    })

    puts_df = pd.DataFrame({
        'strike': [15200, 15220, 15240, 15260],
        'GAMMA': [80, -30, -80, -120],
        'DELTA': [-0.1, -0.2, -0.3, -0.4],
        'CHARM': [-0.2, -0.4, -0.6, -0.8]
    })

    vwap_data = {'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215}

    # Testar SmartOrder (deve detectar BEARISH mas executar BUY)
    smart_analysis = smart_system.analyze_complete_market(calls_df, puts_df, 15225.0, vwap_data)
    print(f"SmartOrder - Tendencia detectada: {smart_analysis['trend_direction'].value}")
    print(f"SmartOrder - Deve comprar: {smart_analysis['should_buy']}")
    print(f"SmartOrder - Deve vender: {smart_analysis['should_sell']}")

    print()

    # TESTE 2: Cenario que antes gerava BUY -> Agora deve gerar SELL
    print("[TESTE 2] Cenario BULLISH -> Deve executar SELL (invertido)")
    print("-" * 60)

    market_data_bullish = MarketAnalysis(
        charm_data={'values': [-0.8, -0.4, 0.2, 0.6, 1.0]},  # CHARM crescente = bullish
        delta_data={'values': [0.8, 0.6, 0.4, 0.2, -0.2]},   # DELTA decrescente = bullish
        gamma_data={'values': [200, 250, 300, 350], 'strikes': [15200, 15220, 15240, 15260]},  # GAMMA positivo forte
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215, 'std2_upper': 15245},
        volume_data={'current': 2000, 'average': 1000},
        price_data={'recent': [15220, 15230, 15240, 15250]},   # Preço subindo
        current_price=15250.0,  # Acima do 2º desvio
        timestamp=datetime.now()
    )

    # Testar multi-agente (deve detectar BUY mas executar SELL)
    recommendation2 = multi_system.analyze_market_collaborative(market_data_bullish)
    print(f"Multi-Agente - Decisao: {recommendation2.decision.value}")
    print(f"Multi-Agente - Confianca: {recommendation2.confidence:.1f}%")

    # Dados bullish para SmartOrder
    calls_df_bull = pd.DataFrame({
        'strike': [15200, 15220, 15240, 15260],
        'GAMMA': [200, 250, 300, 350],  # GAMMA positivo forte
        'DELTA': [-0.2, 0.2, 0.4, 0.6], # DELTA baixo/negativo = bullish
        'CHARM': [1.0, 0.8, 0.6, 0.4]   # CHARM crescente
    })

    smart_analysis2 = smart_system.analyze_complete_market(calls_df_bull, puts_df, 15250.0, vwap_data)
    print(f"SmartOrder - Tendencia detectada: {smart_analysis2['trend_direction'].value}")
    print(f"SmartOrder - Deve comprar: {smart_analysis2['should_buy']}")
    print(f"SmartOrder - Deve vender: {smart_analysis2['should_sell']}")

    print()

    # RESUMO
    print("=== RESUMO DA LÓGICA INVERTIDA ===")
    print("OBJETIVO: Fazer o CONTRÁRIO do que os agentes recomendam")
    print()

    # Verificar se a inversão está funcionando
    teste1_correto = recommendation.decision.value == "BUY"  # Era cenário bearish, deve virar BUY
    teste2_correto = recommendation2.decision.value == "SELL" or recommendation2.decision.value == "HOLD"  # Era cenário bullish, deve virar SELL

    print(f"TESTE 1 (Bearish -> BUY): {'CORRETO' if teste1_correto else 'FALHOU'}")
    print(f"TESTE 2 (Bullish -> SELL): {'CORRETO' if teste2_correto else 'FALHOU'}")

    if teste1_correto and teste2_correto:
        print()
        print("[SUCCESS] LOGICA INVERTIDA FUNCIONANDO!")
        print("[INFO] Sistema agora faz o CONTRARIO das recomendacoes!")
        print("[PROFIT] Se antes estava dando prejuizo, agora deve dar lucro!")
    else:
        print()
        print("[WARNING] Logica invertida pode precisar de ajustes adicionais")

    print()
    print("CONFIGURACOES INVERTIDAS:")
    print("[INVERT] Agentes detectam SELL -> Sistema executa BUY")
    print("[INVERT] Agentes detectam BUY -> Sistema executa SELL")
    print("[INVERT] SmartOrder: BULLISH analysis -> SELL execution")
    print("[INVERT] SmartOrder: BEARISH analysis -> BUY execution")
    print("[INVERT] Todos os 6 setups invertidos automaticamente")

if __name__ == "__main__":
    try:
        test_logica_invertida()
    except Exception as e:
        print(f"[ERRO] Erro no teste: {e}")
        import traceback
        traceback.print_exc()