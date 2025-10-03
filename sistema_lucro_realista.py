import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import threading
from datetime import datetime, time as datetime_time
import pytz
import logging
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('sistema_lucro_realista.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class SistemaLucroRealista(threading.Thread):
    """Sistema com 14 agentes + 6 setups + greeks + trailing stop inteligente"""

    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 234001)
        self.lot_size = config.get('lot_size', 0.015)

        # CONFIGURAÇÕES LUCRATIVAS E SEGURAS
        self.min_confidence = 75.0          # Só opera com alta probabilidade
        self.stop_loss_pct = 0.12           # Stop robusto (12 pontos no US100)
        self.max_daily_loss = -20.0
        self.max_operations_per_day = 15

        # Estado
        self.is_connected = False
        self.running = False
        self.daily_operations = 0
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        self.active_position = None

        # Horários
        self.avoid_hours = [(12, 13), (15, 17)]
        self.best_hours = [(8, 11), (14, 15)]

        self.connect_mt5()

    def connect_mt5(self):
        login = int(os.getenv('MT5_LOGIN', '103486755'))
        server = os.getenv('MT5_SERVER', 'FBS-Demo')
        password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')
        if mt5.initialize(login=login, server=server, password=password):
            self.is_connected = True
            mt5.symbol_select(self.symbol, True)
            logger.info("Conectado ao MT5 com sucesso")
        else:
            logger.error("Falha ao conectar ao MT5")

    def get_market_data(self):
        if not self.is_connected:
            return None
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 100)
            if rates is None or len(rates) < 40:
                return None
            return {
                'current_price': tick.ask,
                'bid': tick.bid,
                'ask': tick.ask,
                'historical_rates': rates,
                'volume': tick.volume,
                'time': tick.time
            }
        except Exception as e:
            logger.error(f'Erro ao obter dados: {e}')
            return None

    def is_trading_hours(self):
        ny_tz = pytz.timezone('America/New_York')
        now = datetime.now(ny_tz)
        if not (0 <= now.weekday() <= 4):
            return False
        t = now.time()
        return datetime_time(8, 0) <= t < datetime_time(17, 0)

    def is_optimal_time(self):
        ny_tz = pytz.timezone('America/New_York')
        hour = datetime.now(ny_tz).hour
        for start, end in self.avoid_hours:
            if start <= hour < end:
                return False
        for start, end in self.best_hours:
            if start <= hour < end:
                return True
        return False

    def check_minimum_volatility(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            vol = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
            return vol > 0.05
        except:
            return False

    def calculate_greeks(self, market_data):
        prices = market_data['historical_rates']['close']
        cp = market_data['current_price']
        delta = (cp - prices[-10]) / prices[-10] * 100 if len(prices) >= 10 else 0
        returns = np.diff(prices[-20:]) / prices[-20:-1] * 100 if len(prices) >= 20 else [0]
        gamma = np.std(returns)
        ny_tz = pytz.timezone('America/New_York')
        hour = datetime.now(ny_tz).hour
        charm = 1.0 if 8 <= hour <= 11 else 0.7 if 14 <= hour <= 15 else 0.3
        return {'delta': delta, 'gamma': gamma, 'charm': charm}

    # === INCLUIR TODOS OS 14 AGENTES DO SEU ARQUIVO ORIGINAL ===
    # (Copiados exatamente do seu arquivo Pasted_Text_1759452716026.txt)
    def agent_trend_following(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-20:])
            current_price = market_data['current_price']
            trend_strength = abs(short_ma - long_ma) / long_ma * 100
            if short_ma > long_ma and current_price > short_ma:
                confidence = min(75.0 + trend_strength, 90.0)
                return {'decision': 'BUY', 'confidence': confidence, 'reason': f'Tendência de alta forte: MA5 > MA20 (força: {trend_strength:.2f}%)'}
            elif short_ma < long_ma and current_price < short_ma:
                confidence = min(75.0 + trend_strength, 90.0)
                return {'decision': 'SELL', 'confidence': confidence, 'reason': f'Tendência de baixa forte: MA5 < MA20 (força: {trend_strength:.2f}%)'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'Tendência fraca ou divergente'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo de médias móveis'}

    def agent_momentum(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            current_price = market_data['current_price']
            short_momentum = (prices[-1] - prices[-5]) / prices[-5] * 100
            medium_momentum = (prices[-1] - prices[-15]) / prices[-15] * 100
            momentum_acceleration = short_momentum - medium_momentum
            base_confidence = 65.0
            if short_momentum > 0.15 and momentum_acceleration > 0.05:
                confidence = min(base_confidence + abs(momentum_acceleration) * 10, 90.0)
                return {'decision': 'BUY', 'confidence': confidence, 'reason': f'Momentum positivo acelerando: {short_momentum:.2f}% (aceleração: {momentum_acceleration:.2f}%)'}
            elif short_momentum < -0.15 and momentum_acceleration < -0.05:
                confidence = min(base_confidence + abs(momentum_acceleration) * 10, 90.0)
                return {'decision': 'SELL', 'confidence': confidence, 'reason': f'Momentum negativo acelerando: {short_momentum:.2f}% (aceleração: {momentum_acceleration:.2f}%)'}
            else:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': f'Momentum fraco: {short_momentum:.2f}%'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo de momentum'}

    def agent_support_resistance(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            current_price = market_data['current_price']
            recent_high = np.max(prices[-10:])
            recent_low = np.min(prices[-10:])
            if current_price < recent_low * 1.001:
                return {'decision': 'BUY', 'confidence': 55.0, 'reason': 'Próximo do nível de suporte'}
            elif current_price > recent_high * 0.999:
                return {'decision': 'SELL', 'confidence': 55.0, 'reason': 'Próximo do nível de resistência'}
            else:
                return {'decision': 'HOLD', 'confidence': 45.0, 'reason': 'Longe de níveis-chave'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro na detecção de suportes/resistências'}

    def agent_volatility_breakout(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            volatility = np.std(np.diff(prices)) * 100
            if volatility > 0.15:
                return {'decision': 'BUY' if prices[-1] > prices[-2] else 'SELL', 
                       'confidence': 65.0, 'reason': f'Alta volatilidade detectada: {volatility:.2f}%'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': 'Baixa volatilidade'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo de volatilidade'}

    def agent_rsi_oversold_oversold(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            delta = np.diff(prices)
            gain = (delta * (delta > 0)).sum()
            loss = (-delta * (delta < 0)).sum()
            rs = gain / loss if loss != 0 else 100
            rsi = 100 - (100 / (1 + rs))
            if rsi < 30:
                return {'decision': 'BUY', 'confidence': 45.0, 'reason': f'RSI oversold: {rsi:.2f}'}
            elif rsi > 40:
                return {'decision': 'SELL', 'confidence': 45.0, 'reason': f'RSI overbought: {rsi:.2f}'}
            else:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': f'RSI neutro: {rsi:.2f}'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo RSI'}

    def agent_macd_divergence(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            exp1 = pd.Series(prices).ewm(span=12).mean().values
            exp2 = pd.Series(prices).ewm(span=26).mean().values
            macd = exp1 - exp2
            signal = pd.Series(macd).ewm(span=9).mean().values
            histogram = macd - signal
            if histogram[-1] > histogram[-2] and macd[-1] > signal[-1]:
                return {'decision': 'BUY', 'confidence': 65.0, 'reason': 'MACD crossover bullish'}
            elif histogram[-1] < histogram[-2] and macd[-1] < signal[-1]:
                return {'decision': 'SELL', 'confidence': 65.0, 'reason': 'MACD crossover bearish'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'Sem sinal claro MACD'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo MACD'}

    def agent_bollinger_breakout(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            current_price = market_data['current_price']
            ma20 = np.mean(prices[-20:])
            std20 = np.std(prices[-20:])
            upper_band = ma20 + 2 * std20
            lower_band = ma20 - 2 * std20
            if current_price > upper_band:
                return {'decision': 'SELL', 'confidence': 40.0, 'reason': 'Preço acima da banda superior'}
            elif current_price < lower_band:
                return {'decision': 'BUY', 'confidence': 40.0, 'reason': 'Preço abaixo da banda inferior'}
            else:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Preço dentro das bandas'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo Bollinger'}

    def agent_ema_crossover(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            ema_fast = pd.Series(prices).ewm(span=10).mean().values[-1]
            ema_slow = pd.Series(prices).ewm(span=20).mean().values[-1]
            if ema_fast > ema_slow:
                return {'decision': 'BUY', 'confidence': 60.0, 'reason': 'EMA rápida acima da lenta'}
            elif ema_fast < ema_slow:
                return {'decision': 'SELL', 'confidence': 60.0, 'reason': 'EMA rápida abaixo da lenta'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'EMAs próximas'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo EMA'}

    def agent_price_action(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            opens = market_data['historical_rates']['open']
            body_size = abs(prices[-1] - opens[-1])
            total_size = max(prices[-1], opens[-1]) - min(prices[-1], opens[-1])
            if prices[-1] > opens[-1] and body_size > total_size * 0.7:
                return {'decision': 'BUY', 'confidence': 65.0, 'reason': 'Candle bullish forte'}
            elif prices[-1] < opens[-1] and body_size > total_size * 0.7:
                return {'decision': 'SELL', 'confidence': 65.0, 'reason': 'Candle bearish forte'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'Candle neutro'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo Price Action'}

    def agent_multi_timeframe(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            short_trend = 'BULL' if prices[-1] > prices[-5] else 'BEAR'
            medium_trend = 'BULL' if prices[-1] > prices[-20] else 'BEAR'
            if short_trend == medium_trend == 'BULL':
                return {'decision': 'BUY', 'confidence': 80.0, 'reason': 'Tendências alinhadas para cima'}
            elif short_trend == medium_trend == 'BEAR':
                return {'decision': 'SELL', 'confidence': 80.0, 'reason': 'Tendências alinhadas para baixo'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': 'Tendências em direções opostas'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no cálculo Multi-timeframe'}

    def agent_6_setups_greeks(self, market_data):
        try:
            bullish_breakout = self.agent_bullish_breakout(market_data)
            bearish_breakout = self.agent_bearish_breakout(market_data)
            pullback_top = self.agent_pullback_top(market_data)
            pullback_bottom = self.agent_pullback_bottom(market_data)
            consolidated_market = self.agent_consolidated_market(market_data)
            gamma_protection = self.agent_gamma_protection(market_data)
            greeks = self.calculate_greeks(market_data)

            buy_signals = sum(1 for a in [bullish_breakout, pullback_bottom, consolidated_market]
                            if a['decision'] == 'BUY' and a['confidence'] >= 60)
            sell_signals = sum(1 for a in [bearish_breakout, pullback_top, gamma_protection]
                             if a['decision'] == 'SELL' and a['confidence'] >= 60)

            greeks_influence = 0
            if greeks['delta'] > 0.6:
                greeks_influence += 1
            elif greeks['delta'] < -0.6:
                greeks_influence -= 1
            if greeks['gamma'] > 0.7:
                greeks_influence += 0.5
            elif greeks['gamma'] < -0.7:
                greeks_influence -= 0.5

            final_decision = 'HOLD'
            if buy_signals + greeks_influence > sell_signals:
                final_decision = 'BUY'
            elif sell_signals > buy_signals + greeks_influence:
                final_decision = 'SELL'

            total_strength = buy_signals + sell_signals + abs(greeks_influence)
            confidence = (total_strength / 4) * 100 if total_strength > 0 else 0
            return {
                'decision': final_decision,
                'confidence': confidence,
                'reason': f'6 Setups + Greeks: Buy={buy_signals}, Sell={sell_signals}, Greeks={greeks_influence:.1f}'
            }
        except Exception as e:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': f'Erro na análise 6 setups + greeks: {e}'}

    def agent_bullish_breakout(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            volumes = market_data['historical_rates']['tick_volume']
            current_price = market_data['current_price']
            avg_volume = np.mean(volumes[-10:])
            current_volume = volumes[-1]
            if current_volume < avg_volume * 1.5:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Volume insuficiente'}
            recent_high = max(prices[-5:])
            if current_price <= recent_high * 1.002:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Sem rompimento'}
            return {'decision': 'BUY', 'confidence': 75.0, 'reason': 'Bullish breakout confirmado'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no bullish breakout'}

    def agent_bearish_breakout(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            volumes = market_data['historical_rates']['tick_volume']
            current_price = market_data['current_price']
            avg_volume = np.mean(volumes[-10:])
            current_volume = volumes[-1]
            if current_volume < avg_volume * 1.5:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Volume insuficiente'}
            recent_low = min(prices[-5:])
            if current_price >= recent_low * 0.998:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Sem rompimento'}
            return {'decision': 'SELL', 'confidence': 75.0, 'reason': 'Bearish breakout confirmado'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no bearish breakout'}

    def agent_pullback_top(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            highs = market_data['historical_rates']['high']
            current_price = market_data['current_price']
            ema20 = np.mean(prices[-20:])
            if current_price < ema20:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Não está em alta'}
            recent_high = max(highs[-10:])
            pullback_pct = (recent_high - current_price) / recent_high * 100
            if 0.3 <= pullback_pct <= 0.7:
                return {'decision': 'BUY', 'confidence': 65.0, 'reason': f'Pullback no topo: {pullback_pct:.1f}%'}
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Pullback fora do range ideal'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no pullback top'}

    def agent_pullback_bottom(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            lows = market_data['historical_rates']['low']
            current_price = market_data['current_price']
            ema20 = np.mean(prices[-20:])
            if current_price > ema20:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Não está em baixa'}
            recent_low = min(lows[-10:])
            pullback_pct = (current_price - recent_low) / recent_low * 100
            if 0.3 <= pullback_pct <= 0.7:
                return {'decision': 'SELL', 'confidence': 65.0, 'reason': f'Pullback no fundo: {pullback_pct:.1f}%'}
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Pullback fora do range ideal'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no pullback bottom'}

    def agent_consolidated_market(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            current_price = market_data['current_price']
            volatility = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
            if volatility > 0.15:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': f'Volatilidade alta: {volatility:.2f}%'}
            recent_high = max(prices[-20:])
            recent_low = min(prices[-20:])
            range_size = (recent_high - recent_low) / recent_low * 100
            if range_size < 0.3:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': f'Range pequeno: {range_size:.2f}%'}
            return {'decision': 'BUY' if current_price > prices[-1] else 'SELL',
                   'confidence': 55.0, 'reason': f'Mercado consolidado: {range_size:.2f}% range'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no consolidated market'}

    def agent_gamma_protection(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            current_price = market_data['current_price']
            returns = np.diff(prices[-10:]) / prices[-10:-1] * 100
            gamma = np.std(returns)
            if gamma > 0.5:
                return {'decision': 'SELL', 'confidence': 70.0, 'reason': f'Gamma alto: {gamma:.3f} - Proteção ativada'}
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': f'Gamma normal: {gamma:.3f}'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no gamma protection'}

    # === ANÁLISE COM 14 AGENTES ===
    def analyze_with_14_agents(self, market_data):
        if not self.check_minimum_volatility(market_data) or not self.is_optimal_time():
            return {'decision': 'HOLD', 'confidence': 0, 'buy_count': 0, 'sell_count': 0}

        agents = [
            self.agent_trend_following(market_data),
            self.agent_momentum(market_data),
            self.agent_support_resistance(market_data),
            self.agent_volatility_breakout(market_data),
            self.agent_rsi_oversold_oversold(market_data),
            self.agent_macd_divergence(market_data),
            self.agent_bollinger_breakout(market_data),
            self.agent_ema_crossover(market_data),
            self.agent_price_action(market_data),
            self.agent_multi_timeframe(market_data),
            self.agent_bullish_breakout(market_data),
            self.agent_bearish_breakout(market_data),
            self.agent_pullback_top(market_data),
            self.agent_6_setups_greeks(market_data)
        ]

        buy_count = sum(1 for a in agents if a['decision'] == 'BUY' and a['confidence'] >= 60)
        sell_count = sum(1 for a in agents if a['decision'] == 'SELL' and a['confidence'] >= 60)

        if buy_count >= 7:
            confidence = min(75 + (buy_count - 7) * 3, 90)
            return {'decision': 'BUY', 'confidence': confidence, 'buy_count': buy_count, 'sell_count': sell_count}
        elif sell_count >= 7:
            confidence = min(75 + (sell_count - 7) * 3, 90)
            return {'decision': 'SELL', 'confidence': confidence, 'buy_count': buy_count, 'sell_count': sell_count}
        else:
            return {'decision': 'HOLD', 'confidence': 0, 'buy_count': buy_count, 'sell_count': sell_count}

    # === EXECUÇÃO ===
    def execute_trade(self, decision, confidence):
        lot = self.lot_size * (2.5 if confidence > 85 else 2.0 if confidence > 80 else 1.5)
        if decision == 'BUY':
            price = mt5.symbol_info_tick(self.symbol).ask
            sl = price * (1 - self.stop_loss_pct / 100)
            req = {'action': mt5.TRADE_ACTION_DEAL, 'symbol': self.symbol, 'volume': lot, 'type': mt5.ORDER_TYPE_BUY, 'price': price, 'sl': sl, 'magic': self.magic_number, 'comment': 'LucroRealista-BUY'}
        else:
            price = mt5.symbol_info_tick(self.symbol).bid
            sl = price * (1 + self.stop_loss_pct / 100)
            req = {'action': mt5.TRADE_ACTION_DEAL, 'symbol': self.symbol, 'volume': lot, 'type': mt5.ORDER_TYPE_SELL, 'price': price, 'sl': sl, 'magic': self.magic_number, 'comment': 'LucroRealista-SELL'}

        result = mt5.order_send(req)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.active_position = {'ticket': result.order, 'direction': decision, 'entry': price, 'peak': price}
            self.daily_operations += 1
            logger.info(f"Operacao {decision} executada com confiança {confidence:.1f}%")
            return True
        return False

    # === TRAILING STOP INTELIGENTE ===
    def manage_trailing_stop(self):
        if not self.active_position:
            return
        try:
            pos = mt5.positions_get(ticket=self.active_position['ticket'])
            if not pos:
                self.active_position = None
                return
            pos = pos[0]
            tick = mt5.symbol_info_tick(self.symbol)
            current = tick.bid if pos.type == mt5.POSITION_TYPE_SELL else tick.ask
            point = mt5.symbol_info(self.symbol).point

            if self.active_position['direction'] == 'BUY':
                if current > self.active_position['peak']:
                    self.active_position['peak'] = current
                profit_points = (current - self.active_position['entry']) / point
                if profit_points > 60:
                    new_sl = current - 70 * point
                    if new_sl > pos.sl and new_sl > self.active_position['entry']:
                        mt5.order_send({'action': mt5.TRADE_ACTION_SLTP, 'position': pos.ticket, 'sl': new_sl})
                        logger.info(f"Trailing stop: SL = {new_sl:.2f}")
        except Exception as e:
            logger.error(f"Erro no trailing: {e}")

    # === LOOP PRINCIPAL ===
    def run(self):
        if not self.is_connected:
            return
        self.running = True
        logger.info("Sistema Lucro Realista iniciado com sucesso")
        while self.running:
            try:
                if self.is_trading_hours():
                    md = self.get_market_data()
                    if md:
                        analysis = self.analyze_with_14_agents(md)
                        logger.info(f"Analise: {analysis['decision']} (Conf: {analysis['confidence']:.1f}%, BUY:{analysis['buy_count']}, SELL:{analysis['sell_count']})")
                        if analysis['confidence'] >= self.min_confidence:
                            self.execute_trade(analysis['decision'], analysis['confidence'])
                if datetime.now().date() != self.last_reset_date:
                    self.daily_operations = 0
                    self.daily_pnl = 0.0
                    self.last_reset_date = datetime.now().date()
                self.manage_trailing_stop()
                time.sleep(10)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Erro: {e}")
                time.sleep(5)
        mt5.shutdown()

    def stop(self):
        self.running = False


if __name__ == '__main__':
    config = {'symbol': 'US100', 'magic_number': 234001, 'lot_size': 0.015}
    sistema = SistemaLucroRealista(config)
    sistema.start()
    try:
        while sistema.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        sistema.stop()
        sistema.join()
        print("Sistema encerrado com sucesso!")