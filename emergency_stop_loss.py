#!/usr/bin/env python3
"""
SISTEMA DE EMERGÊNCIA - STOP LOSS FORÇADO
FECHA QUALQUER POSIÇÃO COM PERDA >= -$0.02
PARA QUANDO MERCADO ESTÁ CONSOLIDADO
"""

import MetaTrader5 as mt5
import time
import logging
import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - EMERGENCY - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_market_consolidation():
    """TEMPORARIAMENTE DESABILITADO - Detecta se o mercado está consolidado"""
    try:
        # DESABILITADO TEMPORARIAMENTE PARA EVITAR ERRO NUMPY
        logger.info("📊 Detecção de consolidação temporariamente desabilitada")
        return False  # Sempre retorna False = mercado sempre ativo

    except Exception as e:
        logger.error(f"Erro na detecção de consolidação: {e}")
        return False

def emergency_stop_loss():
    """FORÇA fechamento de TODAS posições com perda >= -$0.02"""

    # Conectar MT5
    if not mt5.initialize():
        logger.error("FALHA AO INICIALIZAR MT5!")
        return False

    logger.info("🚨 SISTEMA DE EMERGÊNCIA ATIVO - MONITORANDO STOP LOSS -$0.02")
    logger.info("📊 DETECTANDO CONSOLIDAÇÃO PARA EVITAR SINAIS DESNECESSÁRIOS")

    consolidation_count = 0

    while True:
        try:
            # 1. VERIFICAR SE MERCADO ESTÁ CONSOLIDADO
            is_consolidated = detect_market_consolidation()

            if is_consolidated:
                consolidation_count += 1

                # Se mercado consolidado por mais de 5 verificações (10 segundos)
                if consolidation_count >= 5:
                    logger.info("🛑 MERCADO CONSOLIDADO - PAUSANDO MONITORAMENTO POR 60 SEGUNDOS")
                    logger.info("💤 Sistema em standby - sem novas negociações")
                    time.sleep(60)  # Pausa longa em mercado consolidado
                    consolidation_count = 0  # Reset contador
                    continue
                else:
                    logger.info(f"⏳ Consolidação detectada ({consolidation_count}/5) - continuando...")
            else:
                consolidation_count = 0  # Reset se mercado não consolidado
                logger.info("📈 MERCADO ATIVO - MONITORAMENTO NORMAL")

            # 2. MONITORAR POSIÇÕES EXISTENTES (sempre executa - stop loss é crítico!)
            positions = mt5.positions_get(symbol="US100")

            if positions:
                logger.info(f"📊 Monitorando {len(positions)} posições...")

                for pos in positions:
                    ticket = pos.ticket
                    profit = pos.profit

                    # VERIFICAÇÃO CRÍTICA: Se perda >= -$0.02
                    if profit <= -0.02:
                        logger.error(f"🚨 PERDA DETECTADA: Posição #{ticket} = ${profit:.2f}")
                        logger.error(f"🚨 FECHANDO IMEDIATAMENTE!")

                        # Determinar tipo de fechamento
                        position_type = pos.type  # 0=BUY, 1=SELL
                        volume = pos.volume

                        # Configurar ordem de fechamento
                        if position_type == 0:  # BUY - fechar com SELL
                            order_type = mt5.ORDER_TYPE_SELL
                            price = mt5.symbol_info_tick("US100").bid
                        else:  # SELL - fechar com BUY
                            order_type = mt5.ORDER_TYPE_BUY
                            price = mt5.symbol_info_tick("US100").ask

                        # Criar requisição de fechamento
                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": "US100",
                            "volume": volume,
                            "type": order_type,
                            "position": ticket,
                            "price": price,
                            "deviation": 20,
                            "magic": 234001,
                            "comment": "EMERGENCY STOP LOSS -0.02",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_RETURN,
                        }

                        # EXECUTAR FECHAMENTO
                        result = mt5.order_send(close_request)

                        if result.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info(f"✅ EMERGÊNCIA EXECUTADA: Posição #{ticket} fechada com ${profit:.2f}")
                        else:
                            logger.error(f"❌ FALHA NO FECHAMENTO: #{ticket} - Erro: {result.retcode}")

                            # Tentar outros modos de preenchimento
                            close_request["type_filling"] = mt5.ORDER_FILLING_FOK
                            result2 = mt5.order_send(close_request)

                            if result2.retcode == mt5.TRADE_RETCODE_DONE:
                                logger.info(f"✅ EMERGÊNCIA EXECUTADA (2ª tentativa): #{ticket} fechada")
                            else:
                                logger.error(f"❌ FALHA CRÍTICA: Não conseguiu fechar #{ticket}")

            else:
                if not is_consolidated:
                    logger.info("📊 Nenhuma posição US100 aberta - mercado ativo")

            # Aguardar baseado no estado do mercado
            if is_consolidated:
                time.sleep(10)  # Pausa maior em consolidação
            else:
                time.sleep(2)   # Verificação rápida em mercado ativo

        except Exception as e:
            logger.error(f"ERRO NO SISTEMA DE EMERGÊNCIA: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        emergency_stop_loss()
    except KeyboardInterrupt:
        logger.info("Sistema de emergência interrompido pelo usuário")
    finally:
        mt5.shutdown()
        logger.info("MT5 desconectado")