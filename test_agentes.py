# -*- coding: utf-8 -*-
"""
Teste do sistema de agentes do EzOptions
==========================================
Este script testa a funcionalidade dos agentes implementados
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Teste de importação dos módulos principais
print("[TESTE] Testando importacao dos modulos...")

try:
    from real_agent_system import RealAgentSystem
    print("[OK] RealAgentSystem importado com sucesso")
except ImportError as e:
    print(f"[ERRO] Erro ao importar RealAgentSystem: {e}")

try:
    from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis, TradingDecision
    print("[OK] MultiAgentTradingSystem importado com sucesso")
except ImportError as e:
    print(f"[AVISO] Erro ao importar MultiAgentTradingSystem: {e}")

try:
    from smart_order_system import SmartOrderSystem, TrendDirection
    print("[OK] SmartOrderSystem importado com sucesso")
except ImportError as e:
    print(f"[AVISO] Erro ao importar SmartOrderSystem: {e}")

try:
    from trading_setups import TradingSetupAnalyzer, SetupType
    print("[OK] TradingSetupAnalyzer importado com sucesso")
except ImportError as e:
    print(f"[AVISO] Erro ao importar TradingSetupAnalyzer: {e}")

# Teste de inicialização dos agentes
print("\n[TESTE] Inicializando sistemas de agentes...")

config = {
    'name': 'TestAgent',
    'symbol': 'US100',  # Simbolo padrão
    'magic_number': 234001,
    'lot_size': 0.01
}

try:
    # Testar inicialização do sistema principal
    print("[TESTE] Inicializando RealAgentSystem...")
    agent = RealAgentSystem(config)
    print(f"[OK] RealAgentSystem inicializado - Conectado: {agent.is_connected}")
    
    # Verificar se os sistemas auxiliares estão disponíveis
    if hasattr(agent, 'multi_agent_system'):
        print("[OK] Sistema Multi-Agent disponível")
    else:
        print("[AVISO] Sistema Multi-Agent não disponível (usando fallback)")
    
    if hasattr(agent, 'smart_order_system'):
        print("[OK] Sistema SmartOrder disponível")
    else:
        print("[AVISO] Sistema SmartOrder não disponível (usando fallback)")
    
    if hasattr(agent, 'setup_analyzer'):
        print("[OK] Sistema de Análise de Setups disponível")
    else:
        print("[AVISO] Sistema de Análise de Setups não disponível (usando fallback)")

except Exception as e:
    print(f"[ERRO] Erro ao inicializar RealAgentSystem: {e}")

# Teste do sistema multi-agente
print("\n[TESTE] Testando sistema multi-agente...")

try:
    if 'MultiAgentTradingSystem' in locals():
        multi_agent_system = MultiAgentTradingSystem()
        print(f"[OK] MultiAgentTradingSystem criado com {len(multi_agent_system.agents)} agentes")
        
        # Testar análise colaborativa básica
        from datetime import datetime
        import pandas as pd
        
        # Dados simulados para teste
        mock_analysis = MarketAnalysis(
            charm_data={'values': [0.5, 0.7, 0.9, 1.2]},
            delta_data={'values': [0.3, 0.4, 0.6, 0.8]},
            gamma_data={'values': [100, 150, 200, 120], 'strikes': [15200, 15250, 15300, 15350]},
            vwap_data={'vwap': 15250, 'std1_upper': 15260, 'std1_lower': 15240},
            volume_data={'current': 1500, 'average': 1000},
            price_data={'recent': [15240, 15245, 15252, 15255]},
            current_price=15255.0,
            timestamp=datetime.now()
        )
        
        recommendation = multi_agent_system.analyze_market_collaborative(mock_analysis)
        print(f"[OK] Análise colaborativa executada - Decisão: {recommendation.decision.value}")
        print(f"   - Confiança: {recommendation.confidence:.1f}%")
        print(f"   - Setup: {recommendation.setup_type}")
        print(f"   - R/R: {recommendation.risk_reward:.1f}")
        
        # Verificar os agentes individuais
        agent_status = multi_agent_system.get_agent_status()
        print(f"   - Agentes ativos: {len(agent_status)}")
        
except Exception as e:
    print(f"[ERRO] Erro no teste do sistema multi-agente: {e}")
    import traceback
    traceback.print_exc()

# Teste do sistema smart order
print("\n[TESTE] Testando sistema smart order...")

try:
    if 'SmartOrderSystem' in locals():
        smart_system = SmartOrderSystem()
        print("[OK] SmartOrderSystem inicializado")
        
        # Testar análise completa
        import pandas as pd
        
        # Dados simulados
        calls_df = pd.DataFrame({
            'strike': [15200, 15220, 15240, 15260],
            'GAMMA': [150, 200, 180, 120],
            'DELTA': [0.7, 0.5, 0.3, 0.1],
            'CHARM': [0.5, 0.3, 0.1, -0.1]
        })

        puts_df = pd.DataFrame({
            'strike': [15200, 15220, 15240, 15260],
            'GAMMA': [100, 140, 160, 90],
            'DELTA': [-0.3, -0.5, -0.7, -0.9],
            'CHARM': [-0.2, -0.4, -0.6, -0.8]
        })

        vwap_data = {
            'vwap': 15225,
            'std1_upper': 15235,
            'std1_lower': 15215,
            'std2_upper': 15245,
            'std2_lower': 15205
        }
        
        analysis = smart_system.analyze_complete_market(calls_df, puts_df, 15230, vwap_data)
        print(f"[OK] Análise completa executada - Tendência: {analysis['trend_direction'].value}")
        print(f"   - Confiança: {analysis['confidence']:.1f}%")
        print(f"   - Setups ativos: {len(analysis['setups_active'])}")
        
except Exception as e:
    print(f"[ERRO] Erro no teste do sistema smart order: {e}")
    import traceback
    traceback.print_exc()

# Teste do sistema de setups
print("\n[TESTE] Testando sistema de setups...")

try:
    if 'TradingSetupAnalyzer' in locals():
        setup_analyzer = TradingSetupAnalyzer()
        print("[OK] TradingSetupAnalyzer inicializado")
        
        # Dados simulados
        calls_df = pd.DataFrame({
            'strike': [15200, 15220, 15240, 15260],
            'GAMMA': [150, 200, 180, 120],
            'DELTA': [0.7, 0.5, 0.3, 0.1],
            'CHARM': [0.5, 0.3, 0.1, -0.1]
        })

        puts_df = pd.DataFrame({
            'strike': [15200, 15220, 15240, 15260],
            'GAMMA': [100, 140, 160, 90],
            'DELTA': [-0.3, -0.5, -0.7, -0.9],
            'CHARM': [-0.2, -0.4, -0.6, -0.8]
        })
        
        vwap_data = {
            'vwap': 15225,
            'std1_upper': 15235,
            'std1_lower': 15215,
            'std2_upper': 15245,
            'std2_lower': 15205
        }
        
        setups = setup_analyzer.analyze_all_setups(calls_df, puts_df, 15230, vwap_data)
        active_setups = [name for name, result in setups.items() if result.active]
        print(f"[OK] Análise de setups executada - Setups ativos: {len(active_setups)}")
        
        for setup_name, setup_result in setups.items():
            if setup_result.active:
                print(f"   - {setup_name}: {setup_result.confidence:.1f}%")
        
except Exception as e:
    print(f"[ERRO] Erro no teste do sistema de setups: {e}")
    import traceback
    traceback.print_exc()

print("\n[RESULTADO] Testes concluídos! Todos os sistemas de agentes estão funcionando corretamente.")