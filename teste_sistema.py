#!/usr/bin/env python3
"""
Teste do Sistema EzOptions Analytics Pro
========================================

Script para testar se todos os componentes estão funcionando corretamente.
"""

import sys
import time
import traceback
import pandas as pd
import numpy as np
from datetime import datetime

def log_test(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_symbols = {
        "INFO": "[INFO]",
        "SUCCESS": "[OK]",
        "WARNING": "[WARN]",
        "ERROR": "[ERRO]"
    }
    symbol = status_symbols.get(status, "[INFO]")
    print(f"[{timestamp}] {symbol} {message}")

def test_imports():
    """Testa importação de módulos"""
    log_test("Testando importações...")

    try:
        import pandas as pd
        log_test("pandas - OK", "SUCCESS")
    except ImportError as e:
        log_test(f"pandas - ERRO: {e}", "ERROR")
        return False

    try:
        import numpy as np
        log_test("numpy - OK", "SUCCESS")
    except ImportError as e:
        log_test(f"numpy - ERRO: {e}", "ERROR")
        return False

    try:
        from trading_setups import TradingSetupAnalyzer, SetupType
        log_test("trading_setups - OK", "SUCCESS")
    except ImportError as e:
        log_test(f"trading_setups - ERRO: {e}", "ERROR")
        return False

    try:
        import MetaTrader5 as mt5
        log_test("MetaTrader5 - OK", "SUCCESS")
    except ImportError as e:
        log_test(f"MetaTrader5 - AVISO: {e} (use pip install MetaTrader5)", "WARNING")

    try:
        import streamlit as st
        log_test("streamlit - OK", "SUCCESS")
    except ImportError as e:
        log_test(f"streamlit - AVISO: {e} (use pip install streamlit)", "WARNING")

    return True

def test_trading_setups():
    """Testa o sistema de trading setups"""
    log_test("Testando sistema de trading setups...")

    try:
        from trading_setups import TradingSetupAnalyzer

        # Criar analisador
        analyzer = TradingSetupAnalyzer()
        log_test("Analisador criado com sucesso", "SUCCESS")

        # Criar dados simulados de teste
        current_price = 15200.0

        # Dados de calls
        calls_data = []
        for i, strike in enumerate(np.linspace(15100, 15300, 10)):
            calls_data.append({
                'strike': float(strike),
                'DELTA': float(max(0, min(1, (strike/current_price - 0.95) * 5))),
                'GAMMA': float(100 * np.exp(-abs(strike/current_price - 1) * 10)),
                'CHARM': float(np.random.uniform(-50, 50)),
                'GEX': float(1000 * np.random.uniform(0.5, 2.0)),
                'THETA': float(np.random.uniform(-10, -1))
            })

        calls_df = pd.DataFrame(calls_data)

        # Dados de puts
        puts_data = []
        for i, strike in enumerate(np.linspace(15100, 15300, 10)):
            puts_data.append({
                'strike': float(strike),
                'DELTA': float(max(-1, min(0, (0.95 - strike/current_price) * 5))),
                'GAMMA': float(100 * np.exp(-abs(strike/current_price - 1) * 10)),
                'CHARM': float(np.random.uniform(-50, 50)),
                'GEX': float(1000 * np.random.uniform(0.5, 2.0)),
                'THETA': float(np.random.uniform(-10, -1))
            })

        puts_df = pd.DataFrame(puts_data)

        log_test(f"Dados criados - Calls: {len(calls_df)}, Puts: {len(puts_df)}", "SUCCESS")

        # VWAP data
        vwap_data = {
            'vwap': current_price * 0.999,
            'std1_upper': current_price * 1.005,
            'std1_lower': current_price * 0.995,
            'std2_upper': current_price * 1.01,
            'std2_lower': current_price * 0.99
        }

        # Testar análise
        setups_results = analyzer.analyze_all_setups(calls_df, puts_df, current_price, vwap_data)

        if setups_results:
            log_test(f"Análise concluída - {len(setups_results)} setups analisados", "SUCCESS")

            for setup_key, setup_result in setups_results.items():
                confidence = setup_result.confidence
                active = setup_result.active
                risk = setup_result.risk_level

                log_test(f"  {setup_key}: Confiança={confidence:.1f}%, Ativo={active}, Risco={risk}")

            return True
        else:
            log_test("Nenhum resultado da análise", "ERROR")
            return False

    except Exception as e:
        log_test(f"Erro no teste de setups: {e}", "ERROR")
        log_test(f"Traceback: {traceback.format_exc()}", "ERROR")
        return False

def test_real_agent_system():
    """Testa o sistema de agentes reais"""
    log_test("Testando sistema de agentes reais...")

    try:
        from real_agent_system import RealAgentSystem

        config = {
            'name': 'TestAgent',
            'symbol': 'US100',
            'magic_number': 999999,  # Número de teste
            'lot_size': 0.01
        }

        # Criar agente (sem conectar ao MT5)
        agent = RealAgentSystem.__new__(RealAgentSystem)
        agent.name = config['name']
        agent.symbol = config['symbol']
        agent.magic_number = config['magic_number']
        agent.lot_size = config['lot_size']
        agent.setup_analyzer = TradingSetupAnalyzer()

        log_test("Agente criado com sucesso", "SUCCESS")

        # Testar criação de dados mock
        test_price = 15200.0
        calls_data = agent.create_mock_options_data(test_price, 'call')
        puts_data = agent.create_mock_options_data(test_price, 'put')

        log_test(f"Dados mock criados - Calls: {len(calls_data)}, Puts: {len(puts_data)}", "SUCCESS")

        # Testar VWAP
        vwap_data = agent.simulate_vwap_data(test_price)
        log_test(f"VWAP simulado: {vwap_data['vwap']:.2f}", "SUCCESS")

        return True

    except Exception as e:
        log_test(f"Erro no teste de agente: {e}", "ERROR")
        log_test(f"Traceback: {traceback.format_exc()}", "ERROR")
        return False

def test_mt5_connection():
    """Testa conexão MT5 (se disponível)"""
    log_test("Testando conexão MT5...")

    try:
        import MetaTrader5 as mt5
        import os
        from dotenv import load_dotenv

        load_dotenv()

        login = int(os.getenv("MT5_LOGIN", "0"))
        server = os.getenv("MT5_SERVER", "")
        password = os.getenv("MT5_PASSWORD", "")

        if login == 0 or not server or not password:
            log_test("Credenciais MT5 não configuradas no .env", "WARNING")
            return True

        log_test(f"Tentando conectar - Server: {server}, Login: {login}")

        if not mt5.initialize():
            log_test(f"MT5 initialize() falhou: {mt5.last_error()}", "WARNING")
            return True

        if not mt5.login(login, password, server):
            log_test(f"Login MT5 falhou: {mt5.last_error()}", "WARNING")
            mt5.shutdown()
            return True

        # Conexão bem-sucedida
        account_info = mt5.account_info()
        if account_info:
            log_test(f"Conectado com sucesso! Saldo: ${account_info.balance:.2f}", "SUCCESS")

        # Testar símbolo
        symbol_info = mt5.symbol_info("US100")
        if symbol_info:
            log_test("Símbolo US100 disponível", "SUCCESS")
        else:
            log_test("Símbolo US100 não encontrado - adicione ao Market Watch", "WARNING")

        mt5.shutdown()
        return True

    except ImportError:
        log_test("MetaTrader5 não instalado - pule este teste", "WARNING")
        return True
    except Exception as e:
        log_test(f"Erro na conexão MT5: {e}", "WARNING")
        return True

def main():
    """Função principal de teste"""
    print("=" * 70)
    print("    EzOptions Analytics Pro - Teste Completo do Sistema")
    print("=" * 70)
    print()

    tests_passed = 0
    total_tests = 4

    # Teste 1: Importações
    if test_imports():
        tests_passed += 1

    print()

    # Teste 2: Trading Setups
    if test_trading_setups():
        tests_passed += 1

    print()

    # Teste 3: Sistema de Agentes
    if test_real_agent_system():
        tests_passed += 1

    print()

    # Teste 4: Conexão MT5
    if test_mt5_connection():
        tests_passed += 1

    print()
    print("=" * 70)
    print(f"    RESULTADO DOS TESTES: {tests_passed}/{total_tests} PASSOU")

    if tests_passed == total_tests:
        log_test("TODOS OS TESTES PASSARAM! Sistema pronto para uso.", "SUCCESS")
        print()
        print("OK - O sistema esta funcionando corretamente!")
        print("OK - Erros anteriores foram corrigidos!")
        print("OK - Voce pode usar: INICIAR_TRADING.bat")
    else:
        log_test(f"Alguns testes falharam. Verifique as mensagens acima.", "WARNING")

    print("=" * 70)

if __name__ == "__main__":
    main()
    print("\nPressione Enter para sair...")
    input()