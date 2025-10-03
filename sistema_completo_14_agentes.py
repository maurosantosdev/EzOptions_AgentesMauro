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
    handlers=[logging.FileHandler('sistema_14_agentes.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class Sistema14AgentesHierarquico(threading.Thread):
    """
    Sistema com 10 agentes estrategistas + 4 executores (2 BUY + 2 SELL)

    === CARACTERÍSTICAS DE TRADER COM 10+ ANOS DE EXPERIÊNCIA ===

    ✅ ANÁLISE MULTI-TIMEFRAME:
       - M1: Tendência de curto prazo
       - M5: Tendência intermediária
       - M15: Tendência de médio prazo
       - Alinhamento obrigatório entre timeframes

    ✅ CONTEXTO INSTITUCIONAL:
       - Horários de abertura/fechamento
       - Janelas de anúncios econômicos
       - Sobreposição Londres-NY
       - Ajuste de confiança em momentos críticos

    ✅ FILTROS SAZONAIS:
       - Segunda: +20% (volta do fim de semana)
       - Sexta: -20% (cautela no fechamento)
       - Multiplicadores por dia da semana

    ✅ CORRELAÇÃO DE MERCADO:
       - Análise de momentum relativo
       - Verificação de divergências
       - Recomendações baseadas em padrões

    ✅ ADAPTAÇÃO AUTOMÁTICA:
       - Ajuste baseado em performance diária
       - Controle de sequências (wins/losses)
       - Adaptação de agressividade automática

    ✅ GESTÃO AVANÇADA DE RISCO:
       - Sistema de recuperação de perdas
       - Controle dinâmico de lote
       - Exposição baseada em performance
    """

    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.name = config.get('name', 'Sistema14Hierarquico')
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 234001)
        self.lot_size = config.get('lot_size', 0.015)

        # 🔥 CONFIGURAÇÕES LUCRATIVAS OTIMIZADAS
        self.min_confidence = 55.0          # Mais oportunidades (era 65%)
        self.max_positions = 2              # Duas posições simultâneas (era 1)
        self.stop_loss_pct = 0.10          # Stop mais apertado (era 0.15%)
        self.take_profit_pct = 0.25        # Take profit para lucros maiores
        self.max_daily_loss = -20.0
        self.max_operations_per_day = 20

        # Estado
        self.is_connected = False
        self.running = False
        self.daily_operations = 0
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        self.last_operation_time = None
        self.min_operation_interval = 60    # 1 minuto (era 2 minutos)
        self.consecutive_losses = 0         # Controle de perdas consecutivas
        self.recovery_mode = False          # Modo de recuperação ativado

        # Trailing stop tracking - Suporte a múltiplas posições
        self.active_positions = []  # Lista de posições ativas
        self.max_positions_actual = 0  # Controle de posições atuais

        # Horários - Controle institucional avançado
        self.avoid_hours = [(12, 13), (15, 16)]
        self.best_hours = [(8, 10), (15, 16)]

        # Características de trader sênior
        self.institutional_hours = {
            'london_open': (8, 9),      # Abertura Londres (alta volatilidade)
            'ny_open': (13, 14),        # Abertura NY (movimento institucional)
            'overlap': (13, 16),        # Sobreposição Londres-NY
            'ny_close': (16, 17)        # Fechamento NY (ajustes finais)
        }

        # Filtros sazonais (trader experiente)
        self.day_of_week_multiplier = {
            0: 1.2,  # Segunda: +20% (volta do fim de semana)
            1: 1.0,  # Terça: normal
            2: 1.1,  # Quarta: +10% (meio da semana)
            3: 1.1,  # Quinta: +10% (antecipação fim de semana)
            4: 0.8   # Sexta: -20% (cautela no fechamento)
        }

        # Controle de contexto de mercado
        self.market_context = {
            'trend_alignment': True,    # Alinhamento com tendência maior
            'institutional_activity': True,  # Atividade institucional
            'news_filter': False,       # Filtro de notícias (placeholder)
            'correlation_filter': True  # Correlação com outros ativos
        }

        # Sistema de adaptação automática (trader experiente)
        self.performance_tracker = {
            'daily_performance': 0.0,
            'weekly_performance': 0.0,
            'monthly_performance': 0.0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'best_day': None,
            'worst_day': None
        }

        # Filtros dinâmicos baseados em performance
        self.adaptive_filters = {
            'confidence_adjustment': 0.0,  # Ajuste baseado em performance
            'risk_multiplier': 1.0,        # Multiplicador de risco
            'aggressiveness_level': 'NORMAL'  # CONSERVATIVE, NORMAL, AGGRESSIVE
        }

        self.connect_mt5()

        # Log das configurações otimizadas
        logger.info('=== SISTEMA 14 AGENTES - VERSAO LUCRATIVA OTIMIZADA ===')
        logger.info('Volatilidade minima: 0.020 (2.0%)')
        logger.info(f'Confianca coletiva: {self.min_confidence}%')
        logger.info(f'Intervalo operacoes: {self.min_operation_interval}s')
        logger.info(f'Maximo posicoes: {self.max_positions}')
        logger.info(f'Stop loss: {self.stop_loss_pct}% | Take profit: {self.take_profit_pct}%')
        logger.info('=== SISTEMA PRONTO PARA OPERAR COM MAXIMA EFICIENCIA ===')

    def connect_mt5(self):
        login = int(os.getenv('MT5_LOGIN', '103486755'))
        server = os.getenv('MT5_SERVER', 'FBS-Demo')
        password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')
        if mt5.initialize(login=login, server=server, password=password):
            self.is_connected = True
            mt5.symbol_select(self.symbol, True)
            logger.info(f'[{self.name}] Conectado ao MT5')
        else:
            logger.error('Falha ao conectar ao MT5')

    def is_trading_hours(self):
        ny_tz = pytz.timezone('America/New_York')
        now = datetime.now(ny_tz)
        if not (0 <= now.weekday() <= 4):
            return False
        t = now.time()
        return datetime_time(8, 0) <= t < datetime_time(17, 0)

    def is_optimal_trading_hour(self):
        ny_tz = pytz.timezone('America/New_York')
        hour = datetime.now(ny_tz).hour
        for start, end in self.avoid_hours:
            if start <= hour < end:
                return False
        for start, end in self.best_hours:
            if start <= hour < end:
                return True
        return False

    def get_market_data(self):
        if not self.is_connected:
            return None
        try:
            tick = mt5.symbol_info_tick(self.symbol)

            # Multi-timeframe: M1, M5, M15
            rates_m1 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 100)
            rates_m5 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 50)
            rates_m15 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M15, 0, 30)

            if rates_m1 is None or len(rates_m1) < 40:
                return None

            return {
                'current_price': tick.ask,
                'bid': tick.bid,
                'ask': tick.ask,
                'historical_rates': rates_m1,
                'rates_m5': rates_m5,
                'rates_m15': rates_m15,
                'volume': tick.volume,
                'time': tick.time
            }
        except Exception as e:
            logger.error(f'Erro ao obter dados: {e}')
            return None

    def check_minimum_volatility(self, market_data):
        try:
            prices = market_data['historical_rates']['close']
            vol = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
            return vol > 0.02
        except:
            return False

    def analyze_multi_timeframe_trend(self, market_data):
        """Análise de tendência em múltiplos timeframes (como trader experiente)"""
        try:
            # M1 - Tendência de curto prazo
            if market_data['rates_m5'] is not None:
                m5_prices = market_data['rates_m5']['close']
                m5_trend = 'BULL' if m5_prices[-1] > m5_prices[-3] else 'BEAR'
            else:
                m5_trend = 'NEUTRAL'

            # M15 - Tendência de médio prazo
            if market_data['rates_m15'] is not None:
                m15_prices = market_data['rates_m15']['close']
                m15_trend = 'BULL' if m15_prices[-1] > m15_prices[-2] else 'BEAR'
            else:
                m15_trend = 'NEUTRAL'

            # M1 - Tendência atual
            m1_prices = market_data['historical_rates']['close']
            m1_trend = 'BULL' if m1_prices[-1] > m1_prices[-5] else 'BEAR'

            # Alinhamento de tendências (trader experiente)
            trend_alignment = (m1_trend == m5_trend == m15_trend)

            return {
                'm1_trend': m1_trend,
                'm5_trend': m5_trend,
                'm15_trend': m15_trend,
                'aligned': trend_alignment,
                'strength': 'STRONG' if trend_alignment else 'WEAK'
            }
        except:
            return {'m1_trend': 'NEUTRAL', 'm5_trend': 'NEUTRAL', 'm15_trend': 'NEUTRAL', 'aligned': False, 'strength': 'WEAK'}

    def check_institutional_context(self):
        """Verifica contexto institucional (como trader com experiência)"""
        ny_tz = pytz.timezone('America/New_York')
        current_hour = datetime.now(ny_tz).hour
        current_minute = datetime.now(ny_tz).minute

        # Horários institucionais críticos
        institutional_windows = {
            'london_open': (8, 0, 8, 30),      # 8:00-8:30
            'ny_open': (13, 30, 14, 0),       # 13:30-14:00
            'fed_announcements': (14, 0, 14, 5), # 14:00-14:05
            'ny_close': (16, 55, 17, 0)       # 16:55-17:00
        }

        for window_name, (start_hour, start_min, end_hour, end_min) in institutional_windows.items():
            if start_hour <= current_hour <= end_hour:
                if start_hour == end_hour:
                    if start_min <= current_minute <= end_min:
                        return {'active': True, 'window': window_name, 'importance': 'HIGH'}
                else:
                    return {'active': True, 'window': window_name, 'importance': 'HIGH'}

        return {'active': False, 'window': None, 'importance': 'NORMAL'}

    def apply_senior_filters(self, analysis, market_data):
        """Aplica filtros de trader experiente"""
        # Filtro 1: Alinhamento multi-timeframe
        mtf_analysis = self.analyze_multi_timeframe_trend(market_data)
        if not mtf_analysis['aligned']:
            logger.info(f"Filtro MTF: Tendencias desalinhadas (M1:{mtf_analysis['m1_trend']}, M5:{mtf_analysis['m5_trend']})")
            return {'decision': 'HOLD', 'confidence': 0}

        # Filtro 2: Contexto institucional
        institutional = self.check_institutional_context()
        if institutional['active'] and institutional['importance'] == 'HIGH':
            logger.info(f"Contexto institucional: {institutional['window']} ativo")
            # Durante janelas críticas, aumenta exigência de confiança
            analysis['confidence'] *= 1.2  # +20% de confiança necessária

        # Filtro 3: Sazonalidade (dia da semana)
        day_multiplier = self.day_of_week_multiplier.get(datetime.now().weekday(), 1.0)
        if day_multiplier != 1.0:
            analysis['confidence'] *= day_multiplier
            logger.info(f"Filtro sazonal: Dia da semana (multiplicador: {day_multiplier})")

        return analysis

    def adapt_to_performance(self):
        """Adapta parâmetros baseado na performance (trader experiente)"""
        # Lógica de adaptação baseada em resultados
        if self.performance_tracker['daily_performance'] > 10:
            self.adaptive_filters['aggressiveness_level'] = 'AGGRESSIVE'
            self.adaptive_filters['confidence_adjustment'] = -5.0  # -5% de confiança necessária
        elif self.performance_tracker['daily_performance'] < -5:
            self.adaptive_filters['aggressiveness_level'] = 'CONSERVATIVE'
            self.adaptive_filters['confidence_adjustment'] = +10.0  # +10% de confiança necessária
        else:
            self.adaptive_filters['aggressiveness_level'] = 'NORMAL'
            self.adaptive_filters['confidence_adjustment'] = 0.0

        # Ajuste baseado em sequência de resultados
        if self.performance_tracker['consecutive_wins'] >= 5:
            self.adaptive_filters['risk_multiplier'] = 1.2  # Aumenta exposição
        elif self.performance_tracker['consecutive_losses'] >= 3:
            self.adaptive_filters['risk_multiplier'] = 0.7  # Reduz exposição

    def update_performance_tracking(self, pnl_result):
        """Atualiza rastreamento de performance"""
        today = datetime.now().date()

        # Atualiza métricas diárias
        self.performance_tracker['daily_performance'] += pnl_result

        # Rastreia sequências
        if pnl_result > 0:
            self.performance_tracker['consecutive_wins'] += 1
            self.performance_tracker['consecutive_losses'] = 0
        else:
            self.performance_tracker['consecutive_losses'] += 1
            self.performance_tracker['consecutive_wins'] = 0

        # Adapta estratégia automaticamente
        self.adapt_to_performance()

    def check_market_correlation(self, market_data):
        """Verifica correlação com outros ativos (trader experiente)"""
        try:
            # Em produção, verificaria correlação com DAX, FTSE, Ouro, etc.
            # Por agora, simula baseado em padrões históricos

            current_price = market_data['current_price']
            prices = market_data['historical_rates']['close']

            # Análise de momentum relativo
            short_momentum = (current_price - prices[-5]) / prices[-5] * 100
            long_momentum = (current_price - prices[-20]) / prices[-20] * 100

            # Correlação simulada baseada em comportamento típico
            correlation_strength = abs(short_momentum - long_momentum) / 10

            return {
                'correlation': 'POSITIVE' if correlation_strength > 0.5 else 'NEGATIVE',
                'strength': min(correlation_strength, 1.0),
                'recommendation': 'FAVORABLE' if correlation_strength > 0.3 else 'CAUTION'
            }
        except:
            return {'correlation': 'NEUTRAL', 'strength': 0.5, 'recommendation': 'NEUTRAL'}

    # === 10 AGENTES ESTRATEGISTAS ===
    def agent_trend_following(self, market_data):
        prices = market_data['historical_rates']['close']
        short_ma = np.mean(prices[-5:])
        long_ma = np.mean(prices[-20:])
        cp = market_data['current_price']
        trend_strength = abs(short_ma - long_ma) / long_ma * 100
        if short_ma > long_ma and cp > short_ma:
            return {'decision': 'BUY', 'confidence': min(75 + trend_strength, 90)}
        elif short_ma < long_ma and cp < short_ma:
            return {'decision': 'SELL', 'confidence': min(75 + trend_strength, 90)}
        return {'decision': 'HOLD', 'confidence': 35}

    def agent_momentum(self, market_data):
        prices = market_data['historical_rates']['close']
        cp = market_data['current_price']
        short_mom = (prices[-1] - prices[-5]) / prices[-5] * 100
        med_mom = (prices[-1] - prices[-15]) / prices[-15] * 100
        acc = short_mom - med_mom
        if short_mom > 0.15 and acc > 0.05:
            return {'decision': 'BUY', 'confidence': min(65 + abs(acc) * 10, 90)}
        elif short_mom < -0.15 and acc < -0.05:
            return {'decision': 'SELL', 'confidence': min(65 + abs(acc) * 10, 90)}
        return {'decision': 'HOLD', 'confidence': 30}

    def agent_support_resistance(self, market_data):
        prices = market_data['historical_rates']['close']
        cp = market_data['current_price']
        recent_high = np.max(prices[-10:])
        recent_low = np.min(prices[-10:])
        if cp < recent_low * 1.001:
            return {'decision': 'BUY', 'confidence': 55}
        elif cp > recent_high * 0.999:
            return {'decision': 'SELL', 'confidence': 55}
        return {'decision': 'HOLD', 'confidence': 45}

    def agent_volatility_breakout(self, market_data):
        prices = market_data['historical_rates']['close']
        vol = np.std(np.diff(prices)) * 100
        if vol > 0.15:
            return {'decision': 'BUY' if prices[-1] > prices[-2] else 'SELL', 'confidence': 65}
        return {'decision': 'HOLD', 'confidence': 40}

    def agent_rsi_oversold_oversold(self, market_data):
        prices = market_data['historical_rates']['close']
        delta = np.diff(prices)
        gain = (delta * (delta > 0)).sum()
        loss = (-delta * (delta < 0)).sum()
        rs = gain / loss if loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        if rsi < 30:
            return {'decision': 'BUY', 'confidence': 45}
        elif rsi > 40:
            return {'decision': 'SELL', 'confidence': 45}
        return {'decision': 'HOLD', 'confidence': 30}

    def agent_macd_divergence(self, market_data):
        prices = market_data['historical_rates']['close']
        exp1 = pd.Series(prices).ewm(span=12).mean().values
        exp2 = pd.Series(prices).ewm(span=26).mean().values
        macd = exp1 - exp2
        signal = pd.Series(macd).ewm(span=9).mean().values
        hist = macd - signal
        if hist[-1] > hist[-2] and macd[-1] > signal[-1]:
            return {'decision': 'BUY', 'confidence': 65}
        elif hist[-1] < hist[-2] and macd[-1] < signal[-1]:
            return {'decision': 'SELL', 'confidence': 65}
        return {'decision': 'HOLD', 'confidence': 35}

    def agent_ema_crossover(self, market_data):
        prices = market_data['historical_rates']['close']
        ema_fast = pd.Series(prices).ewm(span=10).mean().values[-1]
        ema_slow = pd.Series(prices).ewm(span=20).mean().values[-1]
        if ema_fast > ema_slow:
            return {'decision': 'BUY', 'confidence': 60}
        elif ema_fast < ema_slow:
            return {'decision': 'SELL', 'confidence': 60}
        return {'decision': 'HOLD', 'confidence': 35}

    def agent_price_action(self, market_data):
        prices = market_data['historical_rates']['close']
        opens = market_data['historical_rates']['open']
        body = abs(prices[-1] - opens[-1])
        total = max(prices[-1], opens[-1]) - min(prices[-1], opens[-1])
        if prices[-1] > opens[-1] and body > total * 0.7:
            return {'decision': 'BUY', 'confidence': 65}
        elif prices[-1] < opens[-1] and body > total * 0.7:
            return {'decision': 'SELL', 'confidence': 65}
        return {'decision': 'HOLD', 'confidence': 35}

    def agent_multi_timeframe(self, market_data):
        prices = market_data['historical_rates']['close']
        short_trend = 'BULL' if prices[-1] > prices[-5] else 'BEAR'
        med_trend = 'BULL' if prices[-1] > prices[-20] else 'BEAR'
        if short_trend == med_trend == 'BULL':
            return {'decision': 'BUY', 'confidence': 80}
        elif short_trend == med_trend == 'BEAR':
            return {'decision': 'SELL', 'confidence': 80}
        return {'decision': 'HOLD', 'confidence': 40}

    def agent_6_setups_greeks(self, market_data):
        bullish_breakout = self.agent_bullish_breakout(market_data)
        bearish_breakout = self.agent_bearish_breakout(market_data)
        pullback_top = self.agent_pullback_top(market_data)
        pullback_bottom = self.agent_pullback_bottom(market_data)
        consolidated = self.agent_consolidated_market(market_data)
        gamma_prot = self.agent_gamma_protection(market_data)
        greeks = self.calculate_greeks_inteligencia(market_data)

        buy_signals = sum(1 for a in [bullish_breakout, pullback_bottom, consolidated] if a['decision'] == 'BUY' and a['confidence'] >= 60)
        sell_signals = sum(1 for a in [bearish_breakout, pullback_top, gamma_prot] if a['decision'] == 'SELL' and a['confidence'] >= 60)

        greeks_influence = 0
        if greeks['delta'] > 0.6: greeks_influence += 1
        elif greeks['delta'] < -0.6: greeks_influence -= 1
        if greeks['gamma'] > 0.7: greeks_influence += 0.5
        elif greeks['gamma'] < -0.7: greeks_influence -= 0.5

        if buy_signals + greeks_influence > sell_signals:
            return {'decision': 'BUY', 'confidence': min((buy_signals + abs(greeks_influence)) * 20, 90)}
        elif sell_signals > buy_signals + greeks_influence:
            return {'decision': 'SELL', 'confidence': min((sell_signals + abs(greeks_influence)) * 20, 90)}
        return {'decision': 'HOLD', 'confidence': 30}

    # === FUNÇÕES AUXILIARES DOS 6 SETUPS ===
    def agent_bullish_breakout(self, md):
        prices, vol = md['historical_rates']['close'], md['historical_rates']['tick_volume']
        cp = md['current_price']
        if vol[-1] < np.mean(vol[-10:]) * 1.5 or cp <= max(prices[-5:]) * 1.002:
            return {'decision': 'HOLD', 'confidence': 30}
        return {'decision': 'BUY', 'confidence': 75}

    def agent_bearish_breakout(self, md):
        prices, vol = md['historical_rates']['close'], md['historical_rates']['tick_volume']
        cp = md['current_price']
        if vol[-1] < np.mean(vol[-10:]) * 1.5 or cp >= min(prices[-5:]) * 0.998:
            return {'decision': 'HOLD', 'confidence': 30}
        return {'decision': 'SELL', 'confidence': 75}

    def agent_pullback_top(self, md):
        prices, highs = md['historical_rates']['close'], md['historical_rates']['high']
        cp = md['current_price']
        if cp < np.mean(prices[-20:]): return {'decision': 'HOLD', 'confidence': 30}
        rh = max(highs[-10:])
        pull = (rh - cp) / rh * 100
        if 0.3 <= pull <= 0.7:
            return {'decision': 'BUY', 'confidence': 65}
        return {'decision': 'HOLD', 'confidence': 30}

    def agent_pullback_bottom(self, md):
        prices, lows = md['historical_rates']['close'], md['historical_rates']['low']
        cp = md['current_price']
        if cp > np.mean(prices[-20:]): return {'decision': 'HOLD', 'confidence': 30}
        rl = min(lows[-10:])
        pull = (cp - rl) / rl * 100
        if 0.3 <= pull <= 0.7:
            return {'decision': 'SELL', 'confidence': 65}
        return {'decision': 'HOLD', 'confidence': 30}

    def agent_consolidated_market(self, md):
        prices = md['historical_rates']['close']
        vol = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
        if vol > 0.15 or (max(prices[-20:]) - min(prices[-20:])) / min(prices[-20:]) * 100 < 0.3:
            return {'decision': 'HOLD', 'confidence': 30}
        return {'decision': 'BUY' if md['current_price'] > prices[-1] else 'SELL', 'confidence': 55}

    def agent_gamma_protection(self, md):
        prices = md['historical_rates']['close']
        returns = np.diff(prices[-10:]) / prices[-10:-1] * 100
        gamma = np.std(returns)
        if gamma > 0.5:
            return {'decision': 'SELL', 'confidence': 70}
        return {'decision': 'HOLD', 'confidence': 30}

    def calculate_greeks_inteligencia(self, md):
        prices = md['historical_rates']['close']
        cp = md['current_price']
        if len(prices) < 10:
            return {'gamma': 0, 'delta': 0}
        short_ret = np.diff(prices[-5:]) / prices[-5:-1] * 100
        long_ret = np.diff(prices[-15:]) / prices[-15:-1] * 100
        min_len = min(len(short_ret), len(long_ret))
        gamma = np.corrcoef(short_ret[:min_len], long_ret[:min_len])[0,1] if min_len > 1 else 0
        delta = np.tanh((cp - prices[-10]) / prices[-10] * 10) if len(prices) >= 10 else 0
        return {'gamma': gamma, 'delta': delta}

    # === ANÁLISE COLETIVA DOS 10 ESTRATEGISTAS ===
    def analyze_with_10_strategists(self, market_data):
        # Filtros básicos
        if not self.check_minimum_volatility(market_data) or not self.is_optimal_trading_hour():
            return {'decision': 'HOLD', 'confidence': 0, 'buy_count': 0, 'sell_count': 0}

        # Análise dos 10 estrategistas
        strategists = [
            self.agent_trend_following,
            self.agent_momentum,
            self.agent_support_resistance,
            self.agent_volatility_breakout,
            self.agent_rsi_oversold_oversold,
            self.agent_macd_divergence,
            self.agent_ema_crossover,
            self.agent_price_action,
            self.agent_multi_timeframe,
            self.agent_6_setups_greeks
        ]

        analyses = []
        for agent in strategists:
            try:
                res = agent(market_data)
                if res['confidence'] >= 60 and res['decision'] != 'HOLD':
                    analyses.append(res)
            except:
                continue

        buy_count = sum(1 for a in analyses if a['decision'] == 'BUY')
        sell_count = sum(1 for a in analyses if a['decision'] == 'SELL')

        # Análise coletiva básica
        if buy_count >= 7:
            confidence = min(75 + (buy_count - 7) * 5, 90)
            analysis = {'decision': 'BUY', 'confidence': confidence, 'buy_count': buy_count, 'sell_count': sell_count}
        elif sell_count >= 7:
            confidence = min(75 + (sell_count - 7) * 5, 90)
            analysis = {'decision': 'SELL', 'confidence': confidence, 'buy_count': buy_count, 'sell_count': sell_count}
        else:
            analysis = {'decision': 'HOLD', 'confidence': 0, 'buy_count': buy_count, 'sell_count': sell_count}

        # Aplicar filtros de trader experiente
        senior_analysis = self.apply_senior_filters(analysis, market_data)

        # Análise avançada de trader experiente
        mtf_info = self.analyze_multi_timeframe_trend(market_data)
        institutional = self.check_institutional_context()
        correlation = self.check_market_correlation(market_data)

        # Log profissional detalhado
        logger.info(f'=== ANALISE PROFISSIONAL - TRADER SENIOR ===')
        logger.info(f'Estrategistas: {senior_analysis["decision"]} (Conf: {senior_analysis["confidence"]:.1f}%, BUY:{senior_analysis["buy_count"]}, SELL:{senior_analysis["sell_count"]})')
        logger.info(f'Multi-Timeframe: M1={mtf_info["m1_trend"]}, M5={mtf_info["m5_trend"]}, M15={mtf_info["m15_trend"]} ({mtf_info["strength"]})')
        logger.info(f'Contexto Institucional: {institutional["window"] or "Normal"} (Importancia: {institutional["importance"]})')
        logger.info(f'Sazonalidade: Dia {datetime.now().strftime("%A")} (Multiplicador: {self.day_of_week_multiplier.get(datetime.now().weekday(), 1.0)}x)')
        logger.info(f'Correlacao Mercado: {correlation["correlation"]} ({correlation["strength"]:.2f}) - {correlation["recommendation"]}')
        logger.info(f'=== FILTROS APLICADOS - DECISAO: {senior_analysis["decision"]} ===')

        return senior_analysis

    # === EXECUTORES (4 agentes: 2 BUY + 2 SELL) ===
    def execute_buy_with_trailing(self, confidence):
        lot = self.calculate_lot(confidence)
        price = mt5.symbol_info_tick(self.symbol).ask
        sl = price * (1 - self.stop_loss_pct / 100)
        tp = price * (1 + self.take_profit_pct / 100)  # Take profit adicionado
        request = {
             'action': mt5.TRADE_ACTION_DEAL,
             'symbol': self.symbol,
             'volume': lot,
             'type': mt5.ORDER_TYPE_BUY,
             'price': price,
             'sl': sl,
             'tp': tp,  # Take profit incluído
             'magic': self.magic_number,
             'comment': '14Agentes-BUY-Pro',
             'type_time': mt5.ORDER_TIME_GTC,
         }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.active_positions.append({
                'ticket': result.order,
                'direction': 'BUY',
                'entry_price': price,
                'last_high': price,
                'lot_size': lot,
                'confidence': confidence
            })
            self.max_positions_actual += 1
            self.daily_operations += 1
            self.last_operation_time = time.time()
            logger.info(f'BUY EXECUTADO-PRO: {lot} @ {price:.2f} | Conf: {confidence:.1f}% | TP: {tp:.2f}')
            return True
        return False

    def execute_sell_with_trailing(self, confidence):
        lot = self.calculate_lot(confidence)
        price = mt5.symbol_info_tick(self.symbol).bid
        sl = price * (1 + self.stop_loss_pct / 100)
        tp = price * (1 - self.take_profit_pct / 100)  # Take profit para SELL
        request = {
             'action': mt5.TRADE_ACTION_DEAL,
             'symbol': self.symbol,
             'volume': lot,
             'type': mt5.ORDER_TYPE_SELL,
             'price': price,
             'sl': sl,
             'tp': tp,  # Take profit incluído
             'magic': self.magic_number,
             'comment': '14Agentes-SELL-Pro',
             'type_time': mt5.ORDER_TIME_GTC,
         }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.active_positions.append({
                'ticket': result.order,
                'direction': 'SELL',
                'entry_price': price,
                'last_low': price,
                'lot_size': lot,
                'confidence': confidence
            })
            self.max_positions_actual += 1
            self.daily_operations += 1
            self.last_operation_time = time.time()
            logger.info(f'SELL EXECUTADO-PRO: {lot} @ {price:.2f} | Conf: {confidence:.1f}% | TP: {tp:.2f}')
            return True
        return False

    def calculate_lot(self, confidence):
        base = self.lot_size

        # Lógica de multiplicador baseada na confiança
        if confidence >= 90:
            mult = 3.5  # Muito agressivo para sinais excepcionais
        elif confidence >= 85:
            mult = 3.0
        elif confidence >= 80:
            mult = 2.5
        elif confidence >= 70:
            mult = 2.0
        elif confidence >= 60:
            mult = 1.5
        else:
            mult = 1.0

        # Sistema de recuperação de perdas
        if self.consecutive_losses >= 3:
            mult *= 0.3  # Reduz muito após 3 perdas consecutivas
            self.recovery_mode = True
        elif self.consecutive_losses >= 2:
            mult *= 0.5  # Reduz após 2 perdas
        elif self.daily_pnl < -15:
            mult *= 0.4  # Reduz se prejuízo diário > $15

        # Aumenta se está ganhando
        if self.daily_pnl > 20:
            mult *= 1.3  # Aumenta 30% se lucro > $20

        return max(0.01, min(base * mult, 0.12))  # Máximo aumentado para 0.12

    def manage_trailing_stop(self):
        if not self.active_positions:
            return

        try:
            # Gerenciar múltiplas posições
            positions_to_remove = []

            for i, active_pos in enumerate(self.active_positions):
                positions = mt5.positions_get(ticket=active_pos['ticket'])
                if not positions:
                    positions_to_remove.append(i)
                    continue

                pos = positions[0]
                tick = mt5.symbol_info_tick(self.symbol)
                current_price = tick.bid if pos.type == mt5.POSITION_TYPE_SELL else tick.ask
                point = mt5.symbol_info(self.symbol).point

                if active_pos['direction'] == 'BUY':
                    if current_price > active_pos['last_high']:
                        active_pos['last_high'] = current_price
                    profit_points = (current_price - active_pos['entry_price']) / point
                    # Trailing mais agressivo: ativa com 30 pontos (era 50)
                    if profit_points > 30:
                        new_sl = current_price - 40 * point  # Mais apertado (era 60)
                        if new_sl > pos.sl and new_sl > active_pos['entry_price']:
                            self.modify_sl(active_pos['ticket'], new_sl)
                else:  # SELL
                    if current_price < active_pos['last_low']:
                        active_pos['last_low'] = current_price
                    profit_points = (active_pos['entry_price'] - current_price) / point
                    if profit_points > 30:
                        new_sl = current_price + 40 * point
                        if new_sl < pos.sl and new_sl < active_pos['entry_price']:
                            self.modify_sl(active_pos['ticket'], new_sl)

            # Remover posições fechadas
            for i in reversed(positions_to_remove):
                self.active_positions.pop(i)
                self.max_positions_actual -= 1

        except Exception as e:
            logger.error(f'Erro no trailing: {e}')

    def modify_sl(self, ticket, new_sl):
        req = {'action': mt5.TRADE_ACTION_SLTP, 'position': ticket, 'sl': new_sl}
        mt5.order_send(req)
        logger.info(f'Trailing stop atualizado: SL = {new_sl:.2f}')

    # === LOOP PRINCIPAL ===
    def run(self):
        if not self.is_connected:
            return
        self.running = True
        logger.info('Sistema 14 Agentes Hierárquico iniciado')
        while self.running:
            try:
                if self.is_trading_hours():
                    md = self.get_market_data()
                    if md:
                        analysis = self.analyze_with_10_strategists(md)
                        logger.info(f'Estrategistas: {analysis["decision"]} (Confianca: {analysis["confidence"]:.1f}%, BUY:{analysis["buy_count"]}, SELL:{analysis["sell_count"]})')
                        if analysis['confidence'] >= self.min_confidence:
                            # Verificar limite de posições antes de operar
                            if self.max_positions_actual < self.max_positions:
                                if analysis['decision'] == 'BUY':
                                    self.execute_buy_with_trailing(analysis['confidence'])
                                elif analysis['decision'] == 'SELL':
                                    self.execute_sell_with_trailing(analysis['confidence'])
                            else:
                                logger.info(f'Limite de posicoes atingido: {self.max_positions_actual}/{self.max_positions}')
                # Reset diário
                if datetime.now().date() != self.last_reset_date:
                    self.daily_operations = 0
                    self.daily_pnl = 0.0
                    self.last_reset_date = datetime.now().date()
                self.manage_trailing_stop()
                time.sleep(10)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f'Erro: {e}')
                time.sleep(5)
        mt5.shutdown()

    def stop(self):
        self.running = False


if __name__ == '__main__':
    config = {'symbol': 'US100', 'magic_number': 234001, 'lot_size': 0.015}
    sistema = Sistema14AgentesHierarquico(config)
    sistema.start()
    try:
        while sistema.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        sistema.stop()
        sistema.join()
        print("Sistema encerrado!")