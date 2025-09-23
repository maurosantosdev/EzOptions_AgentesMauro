# -*- coding: utf-8 -*-
"""
SISTEMA PREDITIVO INTELIGENTE
============================

🎯 ANÁLISE PREDITIVA DOS AGENTES:
- Se mercado VAI FICAR VERDE → COMPRA e PARA todos os SELL
- Se mercado VAI FICAR VERMELHO → VENDE e PARA todos os BUY

📊 CONFIGURAÇÕES:
- Stop Loss: -0.02%
- Take Profit: +50%
- Análise multi-agente para prever tendência
"""

import MetaTrader5 as mt5
import time
import logging
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('predictive_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PredictiveAgent')

class PredictiveAgentSystem:
    def __init__(self):
        self.name = "Predictive-Agent"
        self.symbol = 'US100'
        self.lot_size = 0.01
        self.magic_number = 234004
        self.stop_loss_percent = 0.02    # -0.02%
        self.take_profit_percent = 50.0  # +50%
        self.is_connected = False

        # Sistema multi-agente
        self.multi_agent_system = MultiAgentTradingSystem()

        # Estado do mercado
        self.current_trend_prediction = None
        self.last_analysis_time = None

        # Conectar ao MT5
        self.connect_mt5()

    def connect_mt5(self):
        """Conecta ao MetaTrader5"""
        try:
            if not mt5.initialize():
                logger.error(f"[{self.name}] Falha ao inicializar MT5")
                return False

            login = 103486755
            password = "iFZkEqMD"
            server = "FBS-Demo"

            logger.info(f"[{self.name}] Conectando ao MT5...")

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

    def get_market_data(self):
        """Coleta dados do mercado para análise"""
        try:
            # Pegar dados históricos para análise
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 50)
            if rates is None or len(rates) < 20:
                return None

            current_price = rates[-1]['close']

            # Calcular indicadores para os agentes
            prices = [r['close'] for r in rates]
            highs = [r['high'] for r in rates]
            lows = [r['low'] for r in rates]
            volumes = [r['tick_volume'] for r in rates]

            # Simular dados de Greeks (mock para análise)
            charm_values = []
            delta_values = []
            gamma_values = []

            # Calcular tendências baseadas nos preços
            for i in range(5, len(prices)):
                # CHARM: Taxa de mudança do Delta
                charm = (prices[i] - prices[i-5]) / prices[i-5] * 100
                charm_values.append(charm)

                # DELTA: Relação com preço (simulado)
                delta = (prices[i] - prices[i-1]) / prices[i-1]
                delta_values.append(delta)

                # GAMMA: Aceleração da mudança (simulado)
                if i >= 6:
                    gamma = ((prices[i] - prices[i-1]) - (prices[i-1] - prices[i-2]))
                    gamma_values.append(gamma * 1000)  # Escalar

            # VWAP simulado
            vwap = sum(prices[-20:]) / 20
            std_dev = (sum([(p - vwap) ** 2 for p in prices[-20:]]) / 20) ** 0.5

            # Criar MarketAnalysis
            market_analysis = MarketAnalysis(
                charm_data={'values': charm_values[-5:]},
                delta_data={'values': delta_values[-5:]},
                gamma_data={
                    'values': gamma_values[-4:] if gamma_values else [0, 0, 0, 0],
                    'strikes': [current_price - 20, current_price - 10, current_price + 10, current_price + 20]
                },
                vwap_data={
                    'vwap': vwap,
                    'std1_upper': vwap + std_dev,
                    'std1_lower': vwap - std_dev,
                    'std2_upper': vwap + (std_dev * 2),
                    'std2_lower': vwap - (std_dev * 2)
                },
                volume_data={
                    'current': volumes[-1],
                    'average': sum(volumes[-10:]) / 10
                },
                price_data={
                    'recent': prices[-4:]
                },
                current_price=current_price,
                timestamp=datetime.now()
            )

            return market_analysis

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao obter dados do mercado: {e}")
            return None

    def predict_market_trend(self):
        """Usa agentes para PREVER se mercado ficará VERDE ou VERMELHO"""
        try:
            market_data = self.get_market_data()
            if not market_data:
                return None

            # Análise multi-agente
            recommendation = self.multi_agent_system.analyze_market_collaborative(market_data)

            # PREVER tendência baseada na análise
            confidence = recommendation.confidence
            decision = recommendation.decision.value
            setup = recommendation.setup_type

            logger.info(f"[{self.name}] ANALISE PREDITIVA:")
            logger.info(f"[{self.name}] - Decisão: {decision}")
            logger.info(f"[{self.name}] - Confiança: {confidence:.1f}%")
            logger.info(f"[{self.name}] - Setup: {setup}")

            # PREDIÇÃO: Se confiança alta, prever tendência
            if confidence >= 70:
                if decision == "BUY":
                    prediction = "MERCADO_VAI_FICAR_VERDE"
                    logger.info(f"[{self.name}] 🔮 PREVISÃO: MERCADO VAI FICAR VERDE!")
                    logger.info(f"[{self.name}] ➡️ AÇÃO: COMPRAR e PARAR todos os SELL")
                elif decision == "SELL":
                    prediction = "MERCADO_VAI_FICAR_VERMELHO"
                    logger.info(f"[{self.name}] 🔮 PREVISÃO: MERCADO VAI FICAR VERMELHO!")
                    logger.info(f"[{self.name}] ➡️ AÇÃO: VENDER e PARAR todos os BUY")
                else:
                    prediction = "NEUTRO"
                    logger.info(f"[{self.name}] ⚪ PREVISÃO: MERCADO NEUTRO - AGUARDAR")
            else:
                prediction = "INCERTO"
                logger.info(f"[{self.name}] ❓ PREVISÃO: INCERTA (conf: {confidence:.1f}%)")

            return {
                'prediction': prediction,
                'confidence': confidence,
                'decision': decision,
                'setup': setup
            }

        except Exception as e:
            logger.error(f"[{self.name}] Erro na análise preditiva: {e}")
            return None

    def close_opposite_positions(self, keep_type):
        """Fecha posições opostas à previsão"""
        try:
            positions = mt5.positions_get(magic=self.magic_number)
            if not positions:
                return 0

            closed_count = 0

            for position in positions:
                # Se queremos manter BUY, fechar SELL (type=1)
                # Se queremos manter SELL, fechar BUY (type=0)
                should_close = False

                if keep_type == "BUY" and position.type == 1:  # Fechar SELL
                    should_close = True
                elif keep_type == "SELL" and position.type == 0:  # Fechar BUY
                    should_close = True

                if should_close:
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
                        "comment": f"{self.name} - Close Opposite",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }

                    result = mt5.order_send(request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        closed_count += 1
                        pos_type = "BUY" if position.type == 0 else "SELL"
                        logger.info(f"[{self.name}] ❌ FECHADO {pos_type}: {position.ticket}")

            return closed_count

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao fechar posições opostas: {e}")
            return 0

    def execute_predictive_trade(self, prediction_data):
        """Executa trade baseado na previsão"""
        try:
            prediction = prediction_data['prediction']

            if prediction == "MERCADO_VAI_FICAR_VERDE":
                # COMPRAR e PARAR todos os SELL
                closed = self.close_opposite_positions("BUY")
                if closed > 0:
                    logger.info(f"[{self.name}] 🛑 FECHADOS {closed} SELL(s) - Mercado vai ficar VERDE")

                # Executar BUY
                return self.execute_trade("BUY", "PREVISAO_VERDE")

            elif prediction == "MERCADO_VAI_FICAR_VERMELHO":
                # VENDER e PARAR todos os BUY
                closed = self.close_opposite_positions("SELL")
                if closed > 0:
                    logger.info(f"[{self.name}] 🛑 FECHADOS {closed} BUY(s) - Mercado vai ficar VERMELHO")

                # Executar SELL
                return self.execute_trade("SELL", "PREVISAO_VERMELHA")

            return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar trade preditivo: {e}")
            return False

    def execute_trade(self, action, reason):
        """Executa trade com stop loss -0.02% e take profit +50%"""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return False

            if action == "BUY":
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = price * (1 - self.stop_loss_percent / 100)      # -0.02%
                tp = price * (1 + self.take_profit_percent / 100)    # +50%
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = price * (1 + self.stop_loss_percent / 100)      # +0.02% para SELL
                tp = price * (1 - self.take_profit_percent / 100)    # -50% para SELL

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
                "comment": f"{self.name}-{reason}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] ✅ TRADE PREDITIVO EXECUTADO:")
                logger.info(f"[{self.name}] - {action} {self.lot_size} {self.symbol} @ {price:.2f}")
                logger.info(f"[{self.name}] - Stop Loss: {sl:.2f} (-0.02%)")
                logger.info(f"[{self.name}] - Take Profit: {tp:.2f} (+50%)")
                logger.info(f"[{self.name}] - Razão: {reason}")
                return True
            else:
                logger.error(f"[{self.name}] ❌ Falha no trade: {result.retcode if result else 'None'}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar trade: {e}")
            return False

    def close_all_positions(self):
        """Fecha todas as posições - Ctrl+C"""
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
                    "comment": f"{self.name} - Emergency Close",
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
        """Loop principal do sistema preditivo"""
        if not self.is_connected:
            logger.error(f"[{self.name}] MT5 não conectado!")
            return

        logger.info(f"[{self.name}] =======================================")
        logger.info(f"[{self.name}] SISTEMA PREDITIVO INTELIGENTE")
        logger.info(f"[{self.name}] =======================================")
        logger.info(f"[{self.name}] 🔮 PREVÊ se mercado ficará VERDE ou VERMELHO")
        logger.info(f"[{self.name}] 🟢 VERDE → COMPRA e PARA todos os SELL")
        logger.info(f"[{self.name}] 🔴 VERMELHO → VENDE e PARA todos os BUY")
        logger.info(f"[{self.name}] 🛡️ Stop Loss: -0.02%")
        logger.info(f"[{self.name}] 🎯 Take Profit: +50%")
        logger.info(f"[{self.name}] =======================================")

        try:
            while True:
                # Análise preditiva a cada 30 segundos
                prediction_data = self.predict_market_trend()

                if prediction_data:
                    prediction = prediction_data['prediction']

                    # Só atuar se previsão mudou
                    if prediction != self.current_trend_prediction and prediction in ['MERCADO_VAI_FICAR_VERDE', 'MERCADO_VAI_FICAR_VERMELHO']:
                        self.current_trend_prediction = prediction
                        logger.info(f"[{self.name}] 🚨 MUDANÇA DE PREVISÃO: {prediction}")

                        # Executar ação preditiva
                        self.execute_predictive_trade(prediction_data)

                # Aguardar 30 segundos para próxima análise
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info(f"\n[{self.name}] === CTRL+C DETECTADO ===")
            logger.info(f"[{self.name}] FECHANDO TODAS AS NEGOCIACOES...")

            self.close_all_positions()

            logger.info(f"[{self.name}] Sistema preditivo parado com segurança")

if __name__ == "__main__":
    agent = PredictiveAgentSystem()
    agent.run()