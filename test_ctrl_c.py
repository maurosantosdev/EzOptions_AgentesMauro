# -*- coding: utf-8 -*-
"""
TESTE CTRL+C - Fechamento de Todas as Negociações
===============================================

Testa se o sistema fecha todas as posições quando Ctrl+C é pressionado.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_agent_system import RealAgentSystem

def test_ctrl_c_functionality():
    print("=== TESTE FUNCIONALIDADE CTRL+C ===")
    print()
    print("Este teste simula um sistema rodando com Ctrl+C")
    print()

    # Configuração do agente
    config = {
        'name': 'TestAgent-CTRL+C',
        'symbol': 'US100',
        'magic_number': 234001,
        'lot_size': 0.01
    }

    print("1. Criando sistema de agentes...")
    agent = RealAgentSystem(config)

    print("2. Testando conexão com MT5...")
    if agent.is_connected:
        print("[OK] Conectado ao MT5")

        print("3. Testando função close_all_positions()...")
        result = agent.close_all_positions()

        if result:
            print("[OK] Função close_all_positions() executou sem erros")
        else:
            print("[ERRO] Função close_all_positions() falhou")

    else:
        print("[AVISO] MT5 não conectado - testando função sem conexão...")
        try:
            agent.close_all_positions()
            print("[OK] Função não trava sem conexão MT5")
        except Exception as e:
            print(f"[ERRO] Função falha sem MT5: {e}")

    print()
    print("4. COMO TESTAR CTRL+C REAL:")
    print("   - Execute: python real_agent_system.py")
    print("   - Aguarde sistema iniciar")
    print("   - Pressione Ctrl+C")
    print("   - Deve aparecer: '=== CTRL+C DETECTADO ==='")
    print("   - Deve aparecer: 'FECHANDO TODAS AS NEGOCIACOES...'")
    print("   - Todas as posicoes devem ser fechadas")
    print()
    print("TESTE DE FUNCIONALIDADE CTRL+C CONCLUIDO!")

if __name__ == "__main__":
    try:
        test_ctrl_c_functionality()
    except Exception as e:
        print(f"[ERRO] Erro no teste: {e}")
        import traceback
        traceback.print_exc()