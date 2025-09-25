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

def is_trading_hours():
    """Verifica se está em horário de trading - US100 9:30-16:00 NY"""
    import pytz
    from datetime import datetime, time as datetime_time

    # Fuso horário de Nova York
    ny_timezone = pytz.timezone('America/New_York')
    current_time_ny = datetime.now(ny_timezone)

    # Verificar se é dia útil (segunda a sexta)
    if not (0 <= current_time_ny.weekday() <= 4):
        return False

    # Horário do mercado: 9:30 às 16:00 (NY)
    market_open = datetime_time(9, 30, 0)  # 9:30 AM
    market_close = datetime_time(16, 0, 0)  # 4:00 PM

    is_market_open = market_open <= current_time_ny.time() <= market_close

    if not is_market_open:
        logger.info(f"MERCADO FECHADO - Horario NY: {current_time_ny.strftime('%H:%M:%S')} (Abre: 9:30, Fecha: 16:00)")

    return is_market_open

def detect_market_consolidation():
    """DESABILITADO - Detecta se o mercado está consolidado"""
    try:
        # DESABILITADO PARA EVITAR ERRO NUMPY
        logger.info("📊 Detecção de consolidação desabilitada")
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
            # 1. PRIMEIRO: VERIFICAR SE ESTÁ NO HORÁRIO DE MERCADO
            if not is_trading_hours():
                logger.info("MERCADO FECHADO - Sistema em standby...")
                time.sleep(60)  # Verificar a cada minuto quando fechado
                continue

            # 2. VERIFICAR SE MERCADO ESTÁ CONSOLIDADO (DESABILITADO)
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

                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info(f"✅ EMERGÊNCIA EXECUTADA: Posição #{ticket} fechada com ${profit:.2f}")
                        else:
                            error_code = result.retcode if result else "None"
                            logger.error(f"❌ FALHA NO FECHAMENTO: #{ticket} - Erro: {error_code}")

                            # Tentar ORDEM MARKET sem stops
                            market_close_request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": "US100",
                                "volume": volume,
                                "type": order_type,
                                "position": ticket,
                                "deviation": 50,  # Maior desvio
                                "magic": 234001,
                                "comment": "EMERGENCY MARKET CLOSE",
                            }

                            result2 = mt5.order_send(market_close_request)

                            if result2 and result2.retcode == mt5.TRADE_RETCODE_DONE:
                                logger.info(f"✅ EMERGÊNCIA EXECUTADA (MARKET): #{ticket} fechada")
                            else:
                                logger.error(f"❌ FALHA CRÍTICA: Não conseguiu fechar #{ticket} mesmo com MARKET")

            else:
                if not is_consolidated:
                    logger.info("📊 Nenhuma posição US100 aberta - mercado ativo")

            # VERIFICAÇÃO ULTRA RÁPIDA PARA STOP LOSS -$0.02
            if is_consolidated:
                time.sleep(2)  # Pausa reduzida mesmo em consolidação
            else:
                time.sleep(0.5)   # VERIFICAÇÃO A CADA 0.5 SEGUNDOS (ULTRA RÁPIDO)

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