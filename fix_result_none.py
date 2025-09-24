#!/usr/bin/env python3
"""
CORREÇÃO IMEDIATA - RESULT É NONE
"""

import MetaTrader5 as mt5
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - FIX - %(message)s')
logger = logging.getLogger(__name__)

def test_and_fix():
    """Testa e corrige o problema Result é None"""

    logger.info("🔧 INICIANDO CORREÇÃO 'Result é None'...")

    # 1. REINICIALIZAR CONEXÃO MT5
    logger.info("1️⃣ Desconectando e reconectando MT5...")
    mt5.shutdown()
    time.sleep(2)

    if not mt5.initialize():
        logger.error("❌ FALHA CRÍTICA: Não conseguiu reconectar ao MT5!")
        return False

    logger.info("✅ MT5 Reconectado")

    # 2. VERIFICAR STATUS BÁSICO
    account_info = mt5.account_info()
    if account_info:
        logger.info(f"✅ Conta: {account_info.login} - Saldo: ${account_info.balance:.2f}")
        logger.info(f"✅ Trading Permitido: {account_info.trade_allowed}")
    else:
        logger.error("❌ Não conseguiu obter info da conta")
        return False

    # 3. TESTE SIMPLES SEM STOPS
    logger.info("3️⃣ Testando ordem SIMPLES (sem SL/TP)...")

    tick = mt5.symbol_info_tick("US100")
    if not tick:
        logger.error("❌ Não conseguiu obter preços")
        return False

    logger.info(f"📊 Preço Ask: {tick.ask}, Bid: {tick.bid}")

    # Ordem super simples sem stops
    simple_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "US100",
        "volume": 0.01,  # Volume mínimo
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "deviation": 100,  # Desvio bem grande
        "magic": 999999,
        "comment": "TESTE SIMPLES",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    logger.info("📤 Enviando ordem SIMPLES...")
    result = mt5.order_send(simple_request)

    if result is None:
        logger.error("❌ AINDA É NONE! Problema grave na conexão/configuração")
        return False
    elif result.retcode == 10030:  # Unsupported filling mode
        logger.error("❌ MODO DE PREENCHIMENTO NÃO SUPORTADO!")

        # Tentar ORDER_FILLING_RETURN
        logger.info("🔄 Tentando ORDER_FILLING_RETURN...")
        simple_request["type_filling"] = mt5.ORDER_FILLING_RETURN
        result2 = mt5.order_send(simple_request)

        if result2 is None:
            logger.error("❌ RETURN também é NONE!")
            return False
        elif result2.retcode == 10030:
            logger.error("❌ RETURN também não suportado!")
            return False
        else:
            result = result2
            logger.info("✅ ORDER_FILLING_RETURN funcionou!")

    if result:
        logger.info(f"✅ RESULTADO RECEBIDO!")
        logger.info(f"   Retcode: {result.retcode}")
        logger.info(f"   Comment: {result.comment}")

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info("🎉 ORDEM EXECUTADA COM SUCESSO!")
            logger.info("✅ PROBLEMA 'Result é None' RESOLVIDO!")

            # Fechar posição de teste
            logger.info("🔄 Fechando posição de teste...")
            positions = mt5.positions_get(symbol="US100")
            if positions:
                for pos in positions:
                    if pos.magic == 999999:
                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": "US100",
                            "volume": pos.volume,
                            "type": mt5.ORDER_TYPE_SELL,
                            "position": pos.ticket,
                            "price": tick.bid,
                            "deviation": 100,
                            "magic": 999999,
                            "comment": "FECHAR TESTE",
                        }
                        close_result = mt5.order_send(close_request)
                        if close_result and close_result.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info("✅ Posição de teste fechada")

            return True
        else:
            logger.error(f"❌ ORDEM REJEITADA: {result.retcode} - {result.comment}")
            return False

    logger.error("❌ Resultado ainda é None após todas as tentativas")
    return False

if __name__ == "__main__":
    try:
        if test_and_fix():
            logger.info("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
            logger.info("   O sistema principal deve funcionar agora")
        else:
            logger.error("💥 CORREÇÃO FALHOU - PROBLEMA CRÍTICO DETECTADO")
    except Exception as e:
        logger.error(f"ERRO NA CORREÇÃO: {e}")
    finally:
        mt5.shutdown()