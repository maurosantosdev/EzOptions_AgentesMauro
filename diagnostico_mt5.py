#!/usr/bin/env python3
"""
DIAGNÓSTICO MT5 - Investigar por que Result é None
"""

import MetaTrader5 as mt5
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - DIAGNOSTIC - %(message)s')
logger = logging.getLogger(__name__)

def diagnostico_mt5():
    """Diagnostica problemas de conexão e ordens MT5"""

    logger.info("🔍 INICIANDO DIAGNÓSTICO MT5...")

    # 1. TESTE DE CONEXÃO
    logger.info("1️⃣ TESTANDO CONEXÃO...")
    if not mt5.initialize():
        logger.error("❌ FALHA NA INICIALIZAÇÃO MT5!")
        return False

    logger.info("✅ MT5 Inicializado com sucesso")

    # 2. INFORMAÇÕES DA CONTA
    logger.info("2️⃣ VERIFICANDO CONTA...")
    account_info = mt5.account_info()
    if account_info:
        logger.info(f"✅ Conta: {account_info.login}")
        logger.info(f"   Servidor: {account_info.server}")
        logger.info(f"   Saldo: ${account_info.balance:.2f}")
        logger.info(f"   Equity: ${account_info.equity:.2f}")
        logger.info(f"   Margem Livre: ${account_info.margin_free:.2f}")
        logger.info(f"   Trading Permitido: {account_info.trade_allowed}")
        logger.info(f"   Expert Advisors: {account_info.trade_expert}")
    else:
        logger.error("❌ Não foi possível obter informações da conta")

    # 3. INFORMAÇÕES DO SÍMBOLO
    logger.info("3️⃣ VERIFICANDO SÍMBOLO US100...")
    symbol_info = mt5.symbol_info("US100")
    if symbol_info:
        logger.info(f"✅ Símbolo US100 encontrado")
        logger.info(f"   Spread: {symbol_info.spread}")
        logger.info(f"   Volume Mínimo: {symbol_info.volume_min}")
        logger.info(f"   Volume Máximo: {symbol_info.volume_max}")
        logger.info(f"   Volume Step: {symbol_info.volume_step}")
        logger.info(f"   Trade Mode: {symbol_info.trade_mode}")
        logger.info(f"   Stops Level: {symbol_info.trade_stops_level}")
        logger.info(f"   Fill Mode: {symbol_info.filling_mode}")
        logger.info(f"   Point: {symbol_info.point}")
    else:
        logger.error("❌ Símbolo US100 não encontrado")
        return False

    # 4. PREÇOS ATUAIS
    logger.info("4️⃣ VERIFICANDO PREÇOS...")
    tick = mt5.symbol_info_tick("US100")
    if tick:
        logger.info(f"✅ Preços obtidos")
        logger.info(f"   Bid: {tick.bid}")
        logger.info(f"   Ask: {tick.ask}")
        logger.info(f"   Spread: {tick.ask - tick.bid:.2f}")
        logger.info(f"   Time: {tick.time}")
    else:
        logger.error("❌ Não foi possível obter preços")
        return False

    # 5. TESTE DE ORDEM SIMPLES
    logger.info("5️⃣ TESTANDO ORDEM SIMPLES...")

    # Tentar ordem BUY muito pequena para testar
    test_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "US100",
        "volume": 0.01,  # Volume mínimo
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "deviation": 50,  # Desvio maior
        "magic": 234001,
        "comment": "TESTE DIAGNOSTICO",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    logger.info(f"📤 Enviando ordem de teste...")
    logger.info(f"   Preço: {tick.ask}")
    logger.info(f"   Volume: 0.01")
    logger.info(f"   Desvio: 50")

    result = mt5.order_send(test_request)

    if result is None:
        logger.error("❌ RESULTADO É NONE - PROBLEMA IDENTIFICADO!")
        logger.error("   Possíveis causas:")
        logger.error("   - Conexão instável com servidor")
        logger.error("   - Configuração incorreta da corretora")
        logger.error("   - Trading não permitido na conta")
        logger.error("   - Mercado fechado")

        # Verificar último erro
        error = mt5.last_error()
        logger.error(f"   Último erro MT5: {error}")

    else:
        logger.info(f"✅ Resultado recebido!")
        logger.info(f"   Retcode: {result.retcode}")
        logger.info(f"   Comment: {result.comment}")

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info("🎉 ORDEM DE TESTE EXECUTADA COM SUCESSO!")
            # Fechar posição imediatamente
            positions = mt5.positions_get(symbol="US100")
            if positions:
                for pos in positions:
                    if pos.comment == "TESTE DIAGNOSTICO":
                        logger.info("🔄 Fechando posição de teste...")
                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": "US100",
                            "volume": pos.volume,
                            "type": mt5.ORDER_TYPE_SELL,
                            "position": pos.ticket,
                            "price": tick.bid,
                            "deviation": 50,
                            "magic": 234001,
                            "comment": "FECHAR TESTE",
                        }
                        close_result = mt5.order_send(close_request)
                        if close_result and close_result.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info("✅ Posição de teste fechada")
        else:
            logger.error(f"❌ ORDEM REJEITADA: {result.retcode} - {result.comment}")

    # 6. TESTE COM DIFERENTES VOLUMES
    logger.info("6️⃣ TESTANDO DIFERENTES VOLUMES...")
    volumes_teste = [0.01, 0.02, 0.05, 0.1]

    for vol in volumes_teste:
        logger.info(f"🧪 Testando volume {vol}...")

        test_vol_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "US100",
            "volume": vol,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 50,
            "magic": 234001,
            "comment": f"TESTE VOL {vol}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        vol_result = mt5.order_send(test_vol_request)

        if vol_result is None:
            logger.error(f"   Volume {vol}: RESULT É NONE ❌")
        elif vol_result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"   Volume {vol}: SUCESSO ✅")
        else:
            logger.warning(f"   Volume {vol}: REJEITADO - {vol_result.retcode}")

        time.sleep(1)  # Pausa entre testes

    mt5.shutdown()
    logger.info("🔍 DIAGNÓSTICO CONCLUÍDO")

if __name__ == "__main__":
    diagnostico_mt5()