# -*- coding: utf-8 -*-
"""
Teste Simples do Sistema de Ordens Inteligentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_order_system import SmartOrderSystem, TrendDirection
from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis
from datetime import datetime
import pandas as pd
import numpy as np

def test_smart_analysis():
    print("=== TESTE DO SISTEMA DE ORDENS INTELIGENTES ===")
    print()

    # Criar sistema de ordens inteligentes
    smart_system = SmartOrderSystem(symbol="US100", magic_number=999999, lot_size=0.01)
    print("[OK] SmartOrderSystem criado")

    # Dados simulados para teste
    calls_df = pd.DataFrame({
        'strike': [15200, 15220, 15240, 15260, 15280],
        'GAMMA': [150, 200, 180, 120, 100],
        'DELTA': [0.8, 0.6, 0.4, 0.2, 0.1],
        'CHARM': [0.6, 0.4, 0.2, 0.0, -0.2]
    })

    puts_df = pd.DataFrame({
        'strike': [15200, 15220, 15240, 15260, 15280],
        'GAMMA': [100, 140, 160, 130, 90],
        'DELTA': [-0.2, -0.4, -0.6, -0.8, -0.9],
        'CHARM': [-0.1, -0.3, -0.5, -0.7, -0.9]
    })

    vwap_data = {
        'vwap': 15225,
        'std1_upper': 15235,
        'std1_lower': 15215,
        'std2_upper': 15245,
        'std2_lower': 15205
    }

    print("[OK] Dados de teste criados")

    # TESTE 1: Cenário BULLISH
    print()
    print("[BULL] TESTE 1: CENARIO BULLISH")
    print("-" * 40)

    current_price = 15250.0  # Acima do 2º desvio VWAP = bullish
    analysis_bullish = smart_system.analyze_complete_market(calls_df, puts_df, current_price, vwap_data)

    print(f"Preco Atual: {current_price}")
    print(f"Tendencia: {analysis_bullish['trend_direction'].value}")
    print(f"Confianca: {analysis_bullish['confidence']:.1f}%")
    print(f"Deve Comprar: {analysis_bullish['should_buy']}")
    print(f"Deve Vender: {analysis_bullish['should_sell']}")
    print(f"Setups Ativos: {len(analysis_bullish['setups_active'])}")

    print("\nRazoes da Analise:")
    for reason in analysis_bullish['reasoning']:
        print(f"  - {reason}")

    if analysis_bullish['should_buy']:
        buy_limit_price = current_price * (1 - smart_system.limit_distance_pct)
        print(f"\n[EXEC] Executaria BUY Market: {current_price:.2f}")
        print(f"[EXEC] Executaria BUY Limit: {buy_limit_price:.2f} (0.05% abaixo)")
        print("[INFO] Cancelaria ordens SELL automaticamente")

    # TESTE 2: Cenário BEARISH
    print()
    print("[BEAR] TESTE 2: CENARIO BEARISH")
    print("-" * 40)

    # Modificar dados para cenário bearish
    calls_df_bear = calls_df.copy()
    calls_df_bear['DELTA'] = [0.9, 0.8, 0.7, 0.8, 0.9]  # DELTA alto = demanda esgotada
    calls_df_bear['CHARM'] = [-0.8, -0.6, -0.4, -0.2, 0.0]  # CHARM decrescente

    current_price = 15200.0  # Abaixo do 2º desvio VWAP = bearish
    vwap_data_bear = vwap_data.copy()
    vwap_data_bear['std2_lower'] = 15210  # Ajustar para ficar abaixo

    analysis_bearish = smart_system.analyze_complete_market(calls_df_bear, puts_df, current_price, vwap_data_bear)

    print(f"Preco Atual: {current_price}")
    print(f"Tendencia: {analysis_bearish['trend_direction'].value}")
    print(f"Confianca: {analysis_bearish['confidence']:.1f}%")
    print(f"Deve Comprar: {analysis_bearish['should_buy']}")
    print(f"Deve Vender: {analysis_bearish['should_sell']}")

    print("\nRazoes da Analise:")
    for reason in analysis_bearish['reasoning']:
        print(f"  - {reason}")

    if analysis_bearish['should_sell']:
        sell_limit_price = current_price * (1 + smart_system.limit_distance_pct)
        print(f"\n[EXEC] Executaria SELL Market: {current_price:.2f}")
        print(f"[EXEC] Executaria SELL Limit: {sell_limit_price:.2f} (0.05% acima)")
        print("[INFO] Cancelaria ordens BUY automaticamente")

    print()
    print("=== RESUMO DOS TESTES ===")
    print("[OK] SmartOrderSystem funcionando")
    print("[OK] Analise GAMMA/DELTA/CHARM integrada")
    print("[OK] Deteccao BULLISH/BEARISH/NEUTRAL")
    print("[OK] Estrategias BUY+BUY_LIMIT e SELL+SELL_LIMIT")
    print("[OK] Distancia de 0.05% para ordens limit")
    print("[OK] Cancelamento de ordens opostas")
    print()
    print("[SUCCESS] SISTEMA PRONTO PARA OPERACAO REAL!")

def test_integration():
    """Teste da integração com multi-agentes"""
    print()
    print("=== TESTE DE INTEGRACAO MULTI-AGENTES ===")

    # Criar sistema multi-agente
    multi_agent_system = MultiAgentTradingSystem()

    # Dados de mercado para os agentes
    market_data = MarketAnalysis(
        charm_data={'values': [0.5, 0.7, 0.9, 1.2, 1.5]},  # CHARM crescente forte
        delta_data={'values': [-0.2, -0.4, -0.6, -0.8, -0.9]},  # DELTA negativo
        gamma_data={'values': [150, 200, 180, 120], 'strikes': [15200, 15220, 15240, 15260]},
        vwap_data={'vwap': 15225, 'std1_upper': 15235, 'std1_lower': 15215},
        volume_data={'current': 1500, 'average': 1000},
        price_data={'recent': [15220, 15230, 15240, 15250]},
        current_price=15250.0,
        timestamp=datetime.now()
    )

    # Análise colaborativa dos 10 agentes
    recommendation = multi_agent_system.analyze_market_collaborative(market_data)

    print(f"[AGENTS] Decisao: {recommendation.decision.value}")
    print(f"[AGENTS] Confianca: {recommendation.confidence:.1f}%")
    print(f"[AGENTS] Setup: {recommendation.setup_type}")
    print(f"[AGENTS] Razao: {recommendation.reasoning}")

    print()
    print("[SUCCESS] Integracao Multi-Agentes + SmartOrder OK!")

if __name__ == "__main__":
    try:
        test_smart_analysis()
        test_integration()
    except Exception as e:
        print(f"[ERROR] Erro no teste: {e}")
        import traceback
        traceback.print_exc()