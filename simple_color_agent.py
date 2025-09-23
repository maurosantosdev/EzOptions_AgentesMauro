# -*- coding: utf-8 -*-
"""
AGENTE SIMPLES POR CORES
=======================

Sistema simplificado baseado no trading.png:
🔴 VERMELHO = SELL
🟢 VERDE = BUY
Stop Loss: -0.02% fixo
Sem limite máximo de compra
"""

import MetaTrader5 as mt5
import time
import logging
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_color_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SimpleColorAgent')

class SimpleColorAgent:
    def __init__(self):
        self.name = "SimpleColor-Agent"
        self.symbol = 'US100'
        self.lot_size = 0.01
        self.magic_number = 234003
        self.stop_loss_percent = 0.02  # -0.02%
        self.is_connected = False
        self.last_action = None
        self.last_candle_time = None

        # Conectar ao MT5
        self.connect_mt5()

    def connect_mt5(self):
        """Conecta ao MetaTrader5"""
        try:
            if not mt5.initialize():
                logger.error(f"[{self.name}] Falha ao inicializar MT5")
                return False

            # Configurações
            login = 103486755
            password = "iFZkEqMD"
            server = "FBS-Demo"

            logger.info(f"[{self.name}] Conectando ao MT5...")
            logger.info(f"[{self.name}] Server: {server}, Login: {login}")

            if not mt5.login(login, password, server):
                error = mt5.last_error()
                logger.error(f"[{self.name}] Login failed: {error}")
                return False

            self.is_connected = True
            logger.info(f"[{self.name}] Conectado ao MT5 com sucesso!")
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Erro na conexão: {e}")
            return False

    def get_candle_color(self):
        """Determina a cor do último candle fechado"""
        try:
            # Pegar últimos 2 candles M1
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)  # Candle anterior (fechado)
            if rates is None or len(rates) == 0:
                return None, None

            candle = rates[0]
            candle_time = candle['time']
            open_price = candle['open']
            close_price = candle['close']

            # Determinar cor
            if close_price > open_price:
                return "GREEN", candle_time  # Candle verde/bullish
            elif close_price < open_price:
                return "RED", candle_time    # Candle vermelho/bearish
            else:
                return "NEUTRAL", candle_time  # Doji

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao ler candle: {e}")
            return None, None

    def has_positions(self):
        """Verifica se há posições abertas"""
        try:
            positions = mt5.positions_get(magic=self.magic_number)
            return len(positions) > 0 if positions else False
        except:
            return False

    def execute_color_trade(self, color):
        """Executa trade baseado na cor do candle"""
        try:
            if self.has_positions():
                logger.info(f"[{self.name}] Posição já aberta - aguardando...")
                return False

            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return False

            # Determinar ação baseada na cor
            if color == "RED":
                action = "SELL"
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = price * (1 + self.stop_loss_percent / 100)  # +0.02% para SELL
            elif color == "GREEN":
                action = "BUY"
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = price * (1 - self.stop_loss_percent / 100)  # -0.02% para BUY
            else:
                return False

            # Executar ordem
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": None,  # Sem take profit
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"{self.name}-{action}-{color}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] TRADE EXECUTADO: {color} → {action}")
                logger.info(f"[{self.name}] {action} {self.lot_size} {self.symbol} @ {price:.2f}")
                logger.info(f"[{self.name}] Stop Loss: {sl:.2f} (-0.02%)")
                self.last_action = action
                return True
            else:
                logger.error(f"[{self.name}] Falha no trade: {result.retcode if result else 'None'}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar trade: {e}")
            return False

    def close_all_positions(self):
        """Fecha todas as posições - usado no Ctrl+C"""
        try:
            logger.info(f"[{self.name}] CTRL+C DETECTADO - Fechando todas as posições...")
            positions = mt5.positions_get(magic=self.magic_number)

            if not positions:
                logger.info(f"[{self.name}] Nenhuma posição aberta para fechar")
                return True

            closed_count = 0
            for position in positions:
                tick = mt5.symbol_info_tick(self.symbol)
                if not tick:
                    continue

                order_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
                price = tick.bid if position.type == 0 else tick.ask

                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.symbol,
                    "volume": position.volume,
                    "type": order_type,
                    "position": position.ticket,
                    "price": price,
                    "deviation": 20,
                    "magic": self.magic_number,
                    "comment": f"{self.name} - Close Position",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    closed_count += 1
                    logger.info(f"[{self.name}] Posição fechada: {position.ticket}")

            logger.info(f"[{self.name}] CTRL+C - {closed_count}/{len(positions)} posições fechadas")
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao fechar posições: {e}")
            return False

    def run(self):
        """Loop principal do sistema simples por cores"""
        if not self.is_connected:
            logger.error(f"[{self.name}] MT5 não conectado!")
            return

        logger.info(f"[{self.name}] ===============================")
        logger.info(f"[{self.name}] SISTEMA SIMPLES POR CORES")
        logger.info(f"[{self.name}] ===============================")
        logger.info(f"[{self.name}] 🔴 CANDLE VERMELHO = SELL")
        logger.info(f"[{self.name}] 🟢 CANDLE VERDE = BUY")
        logger.info(f"[{self.name}] 🛡️ Stop Loss fixo: -0.02%")
        logger.info(f"[{self.name}] 📊 Sem limite máximo de compra")
        logger.info(f"[{self.name}] ⏰ Timeframe: M1")
        logger.info(f"[{self.name}] ===============================")

        try:
            while True:
                # Obter cor do candle
                color, candle_time = self.get_candle_color()

                # Só processar candles novos
                if color and candle_time != self.last_candle_time:
                    self.last_candle_time = candle_time

                    logger.info(f"[{self.name}] Novo candle: {color}")

                    if color == "RED":
                        logger.info(f"[{self.name}] 🔴 CANDLE VERMELHO → EXECUTAR SELL")
                        self.execute_color_trade("RED")
                    elif color == "GREEN":
                        logger.info(f"[{self.name}] 🟢 CANDLE VERDE → EXECUTAR BUY")
                        self.execute_color_trade("GREEN")
                    elif color == "NEUTRAL":
                        logger.info(f"[{self.name}] ⚪ CANDLE NEUTRO → AGUARDANDO")

                # Aguardar 5 segundos
                time.sleep(5)

        except KeyboardInterrupt:
            logger.info(f"\n[{self.name}] === CTRL+C DETECTADO ===")
            logger.info(f"[{self.name}] FECHANDO TODAS AS NEGOCIACOES...")

            self.close_all_positions()

            logger.info(f"[{self.name}] Sistema parado com segurança")
            logger.info(f"[{self.name}] Trading por cores finalizado!")

if __name__ == "__main__":
    agent = SimpleColorAgent()
    agent.run()