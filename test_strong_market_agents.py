"""
Teste para verificar se os novos agentes de mercado forte estão implementados corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strong_market_agents import (
    BuyStopStrongMarketAgent, 
    BuyLimitStrongMarketAgent, 
    SellStopStrongMarketAgent, 
    SellLimitStrongMarketAgent,
    MultiStrongMarketAgentManager
)
from trading_setups import TradingSetupAnalyzer, SetupType
import pandas as pd
import numpy as np

def test_agent_creation():
    """Testa a criação dos agentes"""
    print("Testando criação dos agentes de mercado forte...")
    
    # Configuração padrão para testes
    config = {
        'name': 'TestAgent',
        'symbol': 'US100',
        'magic_number': 234000,
        'lot_size': 0.01,
        'options_symbol': 'QQQ'
    }
    
    try:
        agent1 = BuyStopStrongMarketAgent(config)
        print(f"✓ Agente BuyStopStrongMarketAgent criado: {agent1.name}")
        
        agent2 = BuyLimitStrongMarketAgent(config)
        print(f"✓ Agente BuyLimitStrongMarketAgent criado: {agent2.name}")
        
        agent3 = SellStopStrongMarketAgent(config)
        print(f"✓ Agente SellStopStrongMarketAgent criado: {agent3.name}")
        
        agent4 = SellLimitStrongMarketAgent(config)
        print(f"✓ Agente SellLimitStrongMarketAgent criado: {agent4.name}")
        
        return True
    except Exception as e:
        print(f"✗ Erro na criação dos agentes: {e}")
        return False

def test_setup_analyzer_inclusion():
    """Testa se os novos setups estão incluídos no analisador"""
    print("\nTestando inclusão dos novos setups no TradingSetupAnalyzer...")
    
    try:
        analyzer = TradingSetupAnalyzer()
        
        # Criar dados de teste fictícios
        calls_data = {
            'strike': [100, 105, 110, 115, 120],
            'GAMMA': [500, 1500, 800, 300, 100],
            'DELTA': [0.2, 0.5, 0.7, 0.8, 0.9],
            'CHARM': [10, 20, 15, 5, 2],
        }
        
        puts_data = {
            'strike': [80, 85, 90, 95, 100],
            'GAMMA': [100, 300, 800, 1200, 500],
            'DELTA': [-0.9, -0.8, -0.7, -0.5, -0.2],
            'CHARM': [-2, -5, -15, -20, -10],
        }
        
        calls_df = pd.DataFrame(calls_data)
        puts_df = pd.DataFrame(puts_data)
        
        current_price = 105
        vwap_data = {
            'vwap': 104,
            'std1_upper': 107,
            'std1_lower': 102,
            'std2_upper': 109,
            'std2_lower': 100
        }
        
        # Analisar todos os setups
        setups = analyzer.analyze_all_setups(calls_df, puts_df, current_price, vwap_data)
        
        # Verificar se os novos setups estão presentes
        new_setups = [
            SetupType.BUY_STOP_STRONG_MARKET.value,
            SetupType.BUY_LIMIT_STRONG_MARKET.value,
            SetupType.SELL_STOP_STRONG_MARKET.value,
            SetupType.SELL_LIMIT_STRONG_MARKET.value
        ]
        
        all_present = True
        for setup in new_setups:
            if setup in setups:
                print(f"✓ Setup {setup} encontrado")
            else:
                print(f"✗ Setup {setup} NÃO encontrado")
                all_present = False
        
        if all_present:
            print("✓ Todos os novos setups estão implementados corretamente!")
        
        # Mostrar confianças dos novos setups
        print("\nConfianças dos novos setups:")
        for setup_type in new_setups:
            if setup_type in setups:
                result = setups[setup_type]
                print(f"  {setup_type}: {result.confidence:.2f}% - Ativo: {result.active}")
        
        return all_present
    except Exception as e:
        print(f"✗ Erro no teste do analisador: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_agent_manager():
    """Testa o gerenciador de múltiplos agentes"""
    print("\nTestando MultiStrongMarketAgentManager...")
    
    try:
        config = {
            'name': 'TestMultiAgent',
            'symbol': 'US100',
            'magic_number': 234000,
            'lot_size': 0.01,
            'options_symbol': 'QQQ'
        }
        
        manager = MultiStrongMarketAgentManager(config)
        print("✓ MultiStrongMarketAgentManager criado com sucesso")
        print(f"✓ Número de agentes gerenciados: {len(manager.agents)}")
        
        # Verificar se todos os agentes estão presentes
        expected_agents = ['buy_stop', 'buy_limit', 'sell_stop', 'sell_limit']
        for agent_name in expected_agents:
            if agent_name in manager.agents:
                print(f"✓ Agente {agent_name} presente no gerenciador")
            else:
                print(f"✗ Agente {agent_name} NÃO encontrado no gerenciador")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Erro no teste do gerenciador: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    print("=" * 60)
    print("TESTE DOS NOVOS AGENTES DE MERCADO FORTE")
    print("=" * 60)
    
    results = []
    
    # Testar criação de agentes
    results.append(test_agent_creation())
    
    # Testar inclusão no analisador
    results.append(test_setup_analyzer_inclusion())
    
    # Testar gerenciador de agentes
    results.append(test_multi_agent_manager())
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    test_names = [
        "Criação dos agentes",
        "Inclusão no analisador",
        "Gerenciador de agentes"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "PASSOU" if result else "FALHOU"
        print(f"{test_name}: {status}")
    
    all_passed = all(results)
    print(f"\nResultado final: {'TODOS OS TESTES PASSARAM' if all_passed else 'ALGUNS TESTES FALHARAM'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✓ IMPLEMENTAÇÃO DOS NOVOS AGENTES CONCLUÍDA COM SUCESSO!")
        print("\nResumo dos 4 novos agentes implementados:")
        print("1. BuyStopStrongMarketAgent: Compra stop quando o mercado estiver comprando forte")
        print("2. BuyLimitStrongMarketAgent: Compra limit até perceber que o mercado vai vender forte")
        print("3. SellStopStrongMarketAgent: Vende stop quando o mercado estiver vendendo forte")
        print("4. SellLimitStrongMarketAgent: Vende limit até perceber que o mercado vai comprar forte")
    else:
        print("\n✗ HOUVE PROBLEMAS NA IMPLEMENTAÇÃO DOS NOVOS AGENTES")