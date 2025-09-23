# -*- coding: utf-8 -*-
"""
SISTEMA DE TRADING POR CORES
============================

🔴 VERMELHO = SELL
🟢 VERDE = BUY
Stop Loss fixo: -0.02%
"""

import MetaTrader5 as mt5
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('color_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ColorTrading')

class ColorTradingSystem:
    def __init__(self):
        self.symbol = 'US100'
        self.lot_size = 0.01
        self.magic_number = 234002
        self.stop_loss_percent = 0.02  # -0.02% sempre
        self.is_connected = False

        # Conectar ao MT5
        self.connect_mt5()

    def connect_mt5(self):
        """Conecta ao MT5"""
        if not mt5.initialize():
            logger.error("Falha ao inicializar MT5")
            return False

        # Configurações de login
        login = 103486755
        password = "iFZkEqMD"
        server = "FBS-Demo"

        if not mt5.login(login, password, server):
            logger.error("Falha ao conectar ao MT5")
            return False

        self.is_connected = True
        logger.info("✅ Conectado ao MT5 com sucesso!")
        return True

    def get_current_candle_color(self):
        """Determina a cor do candle atual"""
        try:
            # Pegar último candle (M1)
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 2)
            if rates is None or len(rates) < 2:
                return None

            current_candle = rates[-1]  # Candle atual
            open_price = current_candle['open']
            close_price = current_candle['close']

            if close_price > open_price:
                return "GREEN"  # Candle verde = alta
            elif close_price < open_price:
                return "RED"    # Candle vermelho = baixa
            else:
                return "NEUTRAL"  # Doji

        except Exception as e:
            logger.error(f"Erro ao obter cor do candle: {e}")
            return None

    def execute_trade(self, action):
        """Executa trade baseado na cor"""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return False

            current_price = tick.ask if action == "BUY" else tick.bid

            # Calcular stop loss fixo de -0.02%
            if action == "BUY":
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = current_price * (1 - self.stop_loss_percent / 100)  # -0.02%
                tp = None  # Sem take profit
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = current_price * (1 + self.stop_loss_percent / 100)  # +0.02% para SELL
                tp = None  # Sem take profit

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"Color-Trading-{action}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ TRADE EXECUTADO: {action} {self.lot_size} {self.symbol} @ {price:.2f}")
                logger.info(f"Stop Loss: {sl:.2f} (-0.02%)")
                return True
            else:
                logger.error(f"❌ Falha no trade: {result.retcode if result else 'None'}")
                return False

        except Exception as e:
            logger.error(f"Erro ao executar trade: {e}")
            return False

    def has_open_positions(self):
        """Verifica se há posições abertas"""
        positions = mt5.positions_get(magic=self.magic_number)
        return len(positions) > 0 if positions else False

    def run_color_trading(self):
        """Loop principal do trading por cores"""
        if not self.is_connected:
            logger.error("MT5 não conectado!")
            return

        logger.info("🚀 INICIANDO SISTEMA DE TRADING POR CORES")
        logger.info("🔴 VERMELHO = SELL | 🟢 VERDE = BUY")
        logger.info("🛡️ Stop Loss fixo: -0.02%")
        logger.info("📊 Timeframe: M1 (1 minuto)")
        print("\nPressione Ctrl+C para parar...\n")

        last_color = None

        try:
            while True:
                # Obter cor do candle atual
                current_color = self.get_current_candle_color()

                if current_color and current_color != last_color:
                    logger.info(f"📊 Candle: {current_color}")

                    # Verificar se já tem posições abertas
                    if self.has_open_positions():
                        logger.info("⏸️ Posição já aberta - aguardando...")
                    else:
                        # Executar trade baseado na cor
                        if current_color == "RED":
                            logger.info("🔴 CANDLE VERMELHO → EXECUTANDO SELL")
                            self.execute_trade("SELL")
                        elif current_color == "GREEN":
                            logger.info("🟢 CANDLE VERDE → EXECUTANDO BUY")
                            self.execute_trade("BUY")
                        elif current_color == "NEUTRAL":
                            logger.info("⚪ CANDLE NEUTRO → AGUARDANDO")

                    last_color = current_color

                # Aguardar 10 segundos
                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("\n🛑 SISTEMA PARADO PELO USUÁRIO")
            logger.info("✅ Trading por cores finalizado!")

if __name__ == "__main__":
    system = ColorTradingSystem()
    system.run_color_trading()