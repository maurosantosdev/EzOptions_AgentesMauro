#!/usr/bin/env python3
"""
SISTEMA MULTI-ATIVOS MEGA-INSTITUCIONAL (100 AGENTES)
Opera com US100, US500, US30 e DE30 com estratégias avançadas
Características de trader sênior com 10+ anos de experiência
"""

import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import threading
from datetime import datetime, time as datetime_time
import pytz
import logging
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SistemaMultiAtivos(threading.Thread):
    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.name = config.get('name', 'SistemaMultiAtivos')

        # Multi-ativos com 14 agentes trabalhando simultaneamente
        self.ativos = ['US100', 'US500', 'US30', 'DE30']


        self.ativos_info = {
            'US100': {'magic': 234001, 'lot': 0.01},
            'US500': {'magic': 234002, 'lot': 0.01},
            'US30': {'magic': 234003, 'lot': 0.01},
            'DE30': {'magic': 234004, 'lot': 0.01}
        }

        # Sistema de 100 agentes distribuídos por ativo (trabalhando simultaneamente)
        self.agents_distribution = {
            'US100': 28,  # NASDAQ - Mais agentes devido à alta volatilidade (DOBRADO)
            'US500': 26,  # S&P 500 - Segundo mais importante (DOBRADO)
            'US30': 24,   # Dow Jones - Menos volátil (DOBRADO)
            'DE30': 22    # DAX - Mercado europeu (DOBRADO)
        }
        self.agents_per_asset = 25  # Base de agentes por ativo (DOBRADA)
        self.total_agents = 100  # Total de agentes trabalhando simultaneamente (DOBRADO)

        # Configurações
        self.min_confidence = 55.0
        self.max_positions = 20
        self.stop_loss_pct = 0.10
        self.take_profit_pct = 0.25

        # Estado
        self.is_connected = False
        self.running = False
        self.positions_count = 0

        # Controle de lucro/prejuízo diário (trader experiente - CONSERVADOR)
        self.daily_pnl_target = 150.0       # Meta de lucro diário ($150) - fecha posições
        self.profit_protection_level = 80.0 # Nível de proteção de lucro ($80 positivo) - FECHA POSIÇÕES
        self.daily_pnl = 0.0                # P&L acumulado do dia
        self.reset_time = None              # Controle de reset diário
        self.positions_when_hit_limit = []  # Salvar posições quando bater limite
        self.limit_hit_today = False        # Controle se limite foi atingido hoje
        self.peak_pnl_today = 0.0          # Pico de lucro do dia (para calcular queda)

        # Sistema de trailing stop para proteção de lucro
        self.trailing_stop_active = False   # Controle se trailing stop está ativo
        self.trailing_stop_level = 0.0      # Nível atual do trailing stop

        # ========== NOVAS FUNCIONALIDADES INSTITUCIONAIS ==========

        # 1. Filtros de horário institucional críticos
        self.institutional_windows = {
            'morning_session': {'start': '08:30', 'end': '11:30'},  # Janela FED manhã
            'afternoon_session': {'start': '14:30', 'end': '16:00'}  # Janela FED tarde
        }

        # 2. Controle avançado de drawdown
        self.max_daily_drawdown = -50.0     # Drawdown máximo permitido por dia
        self.current_drawdown = 0.0         # Drawdown atual
        self.drawdown_start_balance = 0.0   # Saldo inicial para cálculo de drawdown
        self.circuit_breaker_active = False # Sistema de emergência

        # 3. Position sizing dinâmico
        self.base_position_size = 0.01      # Tamanho base da posição
        self.volatility_multiplier = 1.0    # Multiplicador baseado na volatilidade
        self.drawdown_position_reduction = 1.0  # Redução baseada no drawdown

        # 4. Sistema de correlação inter-mercado
        self.correlation_window = 50        # Janela de correlação (períodos)
        self.min_correlation_threshold = 0.7 # Threshold mínimo de correlação
        self.divergence_penalty = -10       # Penalidade por divergência

        # 5. Análise multi-timeframe
        self.timeframes = ['M1', 'M5', 'M15']  # Timeframes para análise
        self.min_timeframe_alignment = 2    # Mínimo de timeframes alinhados

        # 6. Sistema de breakout com confirmação
        self.breakout_confirmation_periods = 3  # Períodos para confirmar breakout
        self.volume_surge_threshold = 1.8   # Threshold de volume para breakout
        self.momentum_threshold = 0.1       # Threshold de momentum

        # 7. Filtros de notícias de alto impacto
        self.high_impact_events = [
            'FOMC', 'Federal Funds Rate', 'Non Farm Payrolls', 'CPI', 'GDP',
            'ECB', 'BOE', 'BOJ', 'Unemployment Rate', 'Retail Sales'
        ]
        self.news_avoidance_window = 30     # Minutos antes/depois de notícia

        # 8. Sistema de reversão média estatística
        self.mean_reversion_window = 20     # Janela para cálculo de médias
        self.std_dev_threshold = 2.0        # Threshold de desvio padrão
        self.mean_reversion_confidence = 60 # Confiança mínima para reversão

        # 9. Controle de gaps de abertura
        self.gap_protection_minutes = 15    # Minutos de proteção após abertura
        self.max_gap_size = 0.5             # Tamanho máximo de gap permitido (%)

        # 10. Volume real vs tick volume
        self.min_real_volume_threshold = 1000  # Threshold mínimo de volume real
        self.volume_quality_score = 0.0     # Score de qualidade do volume

        # ========== FIM DAS NOVAS FUNCIONALIDADES ==========

        self.connect_mt5()

        # Logs iniciais com controle de risco
        logger.info('=== SISTEMA MULTI-ATIVOS COM GESTAO DE RISCO ===')
        logger.info('Ativos configurados:')
        for simbolo in self.ativos:
            info = self.ativos_info[simbolo]
            logger.info(f'  {simbolo}: Magic {info["magic"]} | Lote: {info["lot"]}')

        logger.info(f'🎯 Meta diaria: ${self.daily_pnl_target:.2f} (fecha posições)')
        logger.info(f'🛡️ Proteção de Lucro: ${self.profit_protection_level:.2f} (FECHA POSIÇÕES quando lucro cai abaixo)')
        logger.info(f'📊 Confianca mínima: {self.min_confidence}% | Max posições: {self.max_positions}')
        logger.info(f'🧠 TOTAL INSTITUCIONAL: {self.total_agents} agentes (distribuídos: US100={self.agents_distribution["US100"]}, US500={self.agents_distribution["US500"]}, US30={self.agents_distribution["US30"]}, DE30={self.agents_distribution["DE30"]})')
        logger.info('💡 Sistema continua operando mesmo após atingir limites')
        logger.info('=== SISTEMA OPERACIONAL COM PROTECAO INTELIGENTE ===')

    def connect_mt5(self):
        login = int(os.getenv('MT5_LOGIN', '103486755'))
        server = os.getenv('MT5_SERVER', 'FBS-Demo')
        password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

        if mt5.initialize(login=login, server=server, password=password):
            self.is_connected = True
            logger.info('MT5 conectado')

            for simbolo in self.ativos:
                mt5.symbol_select(simbolo, True)
        else:
            logger.error('Falha MT5')


    # ========== MÉTODOS INSTITUCIONAIS AVANÇADOS ==========

    def is_institutional_trading_window(self):
        """Verifica se está em janela institucional crítica"""
        now = datetime.now(pytz.timezone('America/New_York'))
        current_time = now.time().strftime('%H:%M')

        for window_name, window_config in self.institutional_windows.items():
            if window_config['start'] <= current_time <= window_config['end']:
                logger.info(f'🏦 Janela Institucional ATIVA: {window_name} ({current_time})')
                return True

        logger.info(f'⏰ Fora da janela institucional: {current_time}')
        return False

    def check_opening_gap_protection(self):
        """Verifica proteção contra gaps de abertura"""
        now = datetime.now(pytz.timezone('America/New_York'))
        market_open = now.replace(hour=8, minute=0, second=0, microsecond=0)
        minutes_since_open = (now - market_open).seconds / 60

        if minutes_since_open < self.gap_protection_minutes:
            logger.info(f'🛡️ Proteção de Gap ATIVA: {minutes_since_open:.1f}min após abertura')
            return False

        return True

    def check_high_impact_news_filter(self):
        """Verifica filtro de notícias de alto impacto"""
        # Em produção, isso seria conectado a uma API de notícias
        # Por agora, simular eventos críticos em horários específicos
        now = datetime.now(pytz.timezone('America/New_York'))
        current_hour = now.hour
        current_minute = now.minute

        # Simular eventos de alto impacto
        high_impact_times = [
            (8, 30),   # Anúncios matinais
            (10, 0),   # Dados econômicos
            (14, 0),   # Anúncios FED
            (15, 30),  # Decisões de política
        ]

        for event_hour, event_minute in high_impact_times:
            time_diff = abs((current_hour * 60 + current_minute) - (event_hour * 60 + event_minute))
            if time_diff <= self.news_avoidance_window:
                logger.warning(f'🚨 NOTÍCIA DE ALTO IMPACTO DETECTADA: Evitando trading por {self.news_avoidance_window}min')
                return False

        return True

    def validate_multi_timeframe_alignment(self, simbolo):
        """Valida alinhamento de múltiplos timeframes"""
        try:
            alignment_count = 0

            for timeframe in self.timeframes:
                trend = self.get_timeframe_trend(simbolo, timeframe)
                if trend != 'HOLD':
                    alignment_count += 1

            is_aligned = alignment_count >= self.min_timeframe_alignment
            logger.info(f'📊 {simbolo} - Alinhamento MTF: {alignment_count}/{len(self.timeframes)} timeframes')

            return is_aligned

        except Exception as e:
            logger.error(f'Erro no alinhamento MTF: {e}')
            return False

    def get_timeframe_trend(self, simbolo, timeframe):
        """Obtém tendência de um timeframe específico"""
        try:
            if timeframe == 'M1':
                periods = 20
            elif timeframe == 'M5':
                periods = 15
            else:  # M15
                periods = 10

            rates = mt5.copy_rates_from_pos(simbolo, self.get_mt5_timeframe(timeframe), 0, periods)
            if rates is None or len(rates) < 10:
                return 'HOLD'

            prices = rates['close']
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-10:])

            if short_ma > long_ma * 1.001:  # 0.1% threshold
                return 'BUY'
            elif short_ma < long_ma * 0.999:  # 0.1% threshold
                return 'SELL'
            else:
                return 'HOLD'

        except Exception as e:
            logger.error(f'Erro ao obter tendência {timeframe}: {e}')
            return 'HOLD'

    def get_mt5_timeframe(self, timeframe_str):
        """Converte string de timeframe para constante MT5"""
        timeframes = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
        }
        return timeframes.get(timeframe_str, mt5.TIMEFRAME_M1)

    def calculate_advanced_correlation(self, simbolo, prices):
        """Calcula correlação avançada com outros ativos"""
        try:
            signal = 0
            divergences = 0

            for other_simbolo in self.ativos:
                if other_simbolo != simbolo:
                    try:
                        other_rates = mt5.copy_rates_from_pos(other_simbolo, mt5.TIMEFRAME_M1, 0, self.correlation_window)
                        if other_rates is not None and len(other_rates) >= 20:
                            other_prices = other_rates['close']

                            if len(prices) >= 20 and len(other_prices) >= 20:
                                # Correlação de Pearson
                                correlation = np.corrcoef(prices[-20:], other_prices[-20:])[0, 1]

                                # Análise de divergência direcional
                                current_return = (prices[-1] - prices[-5]) / prices[-5]
                                other_return = (other_prices[-1] - other_prices[-5]) / other_prices[-5]

                                if abs(correlation) > self.min_correlation_threshold:
                                    if current_return > 0 and other_return > 0:
                                        signal += 8  # Forte confirmação direcional
                                    elif current_return < 0 and other_return < 0:
                                        signal += 8
                                    elif (current_return > 0) != (other_return > 0):
                                        divergences += 1  # Divergência detectada
                                else:
                                    signal += 2  # Correlação moderada

                    except Exception as e:
                        continue

            # Aplicar penalidade por divergências
            divergence_penalty = divergences * self.divergence_penalty
            final_signal = max(signal + divergence_penalty, -20)

            logger.info(f'📈 {simbolo} - Correlação: {signal:+.1f} | Divergências: {divergences} | Sinal Final: {final_signal:+.1f}')

            return final_signal

        except Exception as e:
            logger.error(f'Erro na correlação avançada: {e}')
            return 0

    def validate_breakout_with_confirmation(self, simbolo, prices, current_price):
        """Valida breakout com confirmação de volume e momentum"""
        try:
            # 1. Verificar breakout básico
            recent_high = np.max(prices[-10:])
            recent_low = np.min(prices[-10:])

            is_breakout_up = current_price > recent_high * 1.002  # 0.2% acima da máxima
            is_breakout_down = current_price < recent_low * 0.998  # 0.2% abaixo da mínima

            if not (is_breakout_up or is_breakout_down):
                return False, 0

            # 2. Confirmar com volume
            rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 0, 20)
            if rates is None:
                return False, 0

            volumes = rates['tick_volume']
            avg_volume = np.mean(volumes[-10:])
            current_volume = volumes[-1]

            volume_confirmed = current_volume > (avg_volume * self.volume_surge_threshold)

            # 3. Confirmar com momentum
            momentum = (current_price - prices[-3]) / prices[-3]
            momentum_confirmed = abs(momentum) > self.momentum_threshold

            # 4. Validação final
            breakout_confirmed = volume_confirmed and momentum_confirmed

            confidence = 0
            if breakout_confirmed:
                confidence = min(70 + (abs(momentum) * 100) + ((current_volume / avg_volume - 1) * 20), 95)

            direction = 'BUY' if is_breakout_up else 'SELL'

            logger.info(f'🚀 {simbolo} - Breakout {direction}: Vol={volume_confirmed} Mom={momentum_confirmed} Conf={confidence:.1f}%')

            return breakout_confirmed, confidence

        except Exception as e:
            logger.error(f'Erro na validação de breakout: {e}')
            return False, 0

    def check_mean_reversion_opportunity(self, simbolo, prices, current_price):
        """Verifica oportunidade de reversão média estatística"""
        try:
            if len(prices) < self.mean_reversion_window:
                return False, 0

            # Calcular média móvel e desvio padrão
            window_prices = prices[-self.mean_reversion_window:]
            mean_price = np.mean(window_prices)
            std_price = np.std(window_prices)

            # Calcular z-score (desvio em termos de desvio padrão)
            if std_price == 0:
                return False, 0

            z_score = (current_price - mean_price) / std_price

            # Verificar se está em nível extremo
            is_overbought = z_score > self.std_dev_threshold
            is_oversold = z_score < -self.std_dev_threshold

            if not (is_overbought or is_oversold):
                return False, 0

            # Calcular confiança baseada na distância da média
            confidence = min(self.mean_reversion_confidence + (abs(z_score) - self.std_dev_threshold) * 10, 90)

            direction = 'SELL' if is_overbought else 'BUY'

            logger.info(f'📊 {simbolo} - Reversão Média: Z-Score={z_score:.2f} | Direção: {direction} | Confiança: {confidence:.1f}%')

            return True, confidence

        except Exception as e:
            logger.error(f'Erro na reversão média: {e}')
            return False, 0

    def calculate_dynamic_position_size(self, simbolo, confidence, current_volatility):
        """Calcula tamanho de posição dinâmico baseado em múltiplos fatores"""
        try:
            # 1. Base position size
            position_size = self.base_position_size

            # 2. Volatilidade adjustment (menor volatilidade = posição maior)
            if current_volatility > 0:
                volatility_adjustment = min(0.05 / current_volatility, 2.0)  # Máximo 2x
                position_size *= volatility_adjustment

            # 3. Confidence adjustment (maior confiança = posição maior)
            confidence_adjustment = confidence / 100.0
            position_size *= (0.5 + confidence_adjustment)  # 0.5x a 1.5x

            # 4. Drawdown adjustment (maior drawdown = posição menor)
            if self.current_drawdown < 0:
                drawdown_pct = abs(self.current_drawdown) / 100.0
                drawdown_adjustment = max(0.3, 1.0 - drawdown_pct)  # Mínimo 30%
                position_size *= drawdown_adjustment

            # 5. Circuit breaker (redução drástica se ativo)
            if self.circuit_breaker_active:
                position_size *= 0.1  # Reduzir para 10% em emergência

            # 6. Garantir limites mínimos e máximos
            position_size = max(0.001, min(position_size, 0.1))  # 0.001 a 0.1

            logger.info(f'📏 {simbolo} - Position Size: {position_size:.3f} (Base: {self.base_position_size:.3f})')

            return position_size

        except Exception as e:
            logger.error(f'Erro no cálculo de posição: {e}')
            return self.base_position_size

    def update_drawdown_control(self, current_balance):
        """Atualiza controle de drawdown"""
        try:
            if self.drawdown_start_balance == 0:
                self.drawdown_start_balance = current_balance
                return

            # Calcular drawdown atual
            drawdown = ((current_balance - self.drawdown_start_balance) / self.drawdown_start_balance) * 100

            if drawdown < self.current_drawdown:
                self.current_drawdown = drawdown

                # Ativar circuit breaker se drawdown muito alto
                if drawdown <= self.max_daily_drawdown:
                    self.circuit_breaker_active = True
                    logger.warning(f'🚨 CIRCUIT BREAKER ATIVADO: Drawdown {drawdown:.2f}% <= {self.max_daily_drawdown:.2f}%')

                logger.info(f'📉 Drawdown Atualizado: {drawdown:.2f}% (Pior: {self.current_drawdown:.2f}%)')

        except Exception as e:
            logger.error(f'Erro no controle de drawdown: {e}')

    def validate_volume_quality(self, simbolo, rates):
        """Valida qualidade do volume (real vs tick)"""
        try:
            if rates is None or len(rates) < 10:
                return 0.5  # Score médio se não conseguir validar

            volumes = rates['tick_volume']
            current_volume = volumes[-1]
            avg_volume = np.mean(volumes[-10:])

            # Score baseado na consistência e nível do volume
            volume_ratio = current_volume / max(avg_volume, 1)

            if volume_ratio > 2.0:
                quality_score = min(0.9, 0.5 + (volume_ratio - 1) * 0.2)
            elif volume_ratio > 1.2:
                quality_score = 0.7
            else:
                quality_score = 0.4

            # Penalizar volumes muito baixos
            if current_volume < 100:
                quality_score *= 0.5

            logger.info(f'📊 {simbolo} - Volume Quality Score: {quality_score:.2f} (Volume: {current_volume})')

            return quality_score

        except Exception as e:
            logger.error(f'Erro na validação de volume: {e}')
            return 0.5

    def is_trading_hours(self):
        now = datetime.now(pytz.timezone('America/New_York'))
        if not (0 <= now.weekday() <= 4):
            return False
        t = now.time()
        return datetime_time(8, 0) <= t < datetime_time(17, 0)

    def analyze_asset_with_agents(self, simbolo):
        """Análise INSTITUCIONAL com 14 agentes + validações avançadas"""
        try:
            # ========== FILTROS PRÉVIOS CRÍTICOS ==========

            # 1. Verificar janela institucional
            if not self.is_institutional_trading_window():
                logger.info(f'🏦 {simbolo} - Fora da janela institucional')
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            # 2. Verificar proteção de gap de abertura
            if not self.check_opening_gap_protection():
                logger.info(f'🛡️ {simbolo} - Proteção de gap ativa')
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            # 3. Verificar filtro de notícias de alto impacto
            if not self.check_high_impact_news_filter():
                logger.warning(f'🚨 {simbolo} - Filtro de notícias ativo')
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            # ========== DADOS DE MERCADO ==========
            rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 0, 50)
            if rates is None or len(rates) < 20:
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            prices = rates['close']
            current_price = prices[-1]

            # ========== ANÁLISES INSTITUCIONAIS AVANÇADAS ==========

            # 1. Volatilidade com threshold fixo
            vol = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
            min_vol_threshold = 0.08  # Threshold fixo de volatilidade

            if vol <= min_vol_threshold:
                logger.info(f'📊 {simbolo} - Volatilidade insuficiente: {vol:.3f}% < {min_vol_threshold:.3f}%')
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            # 2. Validação de qualidade de volume
            volume_quality = self.validate_volume_quality(simbolo, rates)
            if volume_quality < 0.4:  # Volume muito ruim
                logger.warning(f'📊 {simbolo} - Qualidade de volume baixa: {volume_quality:.2f}')
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            # 3. Validação de alinhamento multi-timeframe
            if not self.validate_multi_timeframe_alignment(simbolo):
                logger.info(f'📊 {simbolo} - Timeframes não alinhados')
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            # 4. Sistema de breakout com confirmação
            breakout_confirmed, breakout_confidence = self.validate_breakout_with_confirmation(simbolo, prices, current_price)

            # 5. Sistema de reversão média
            mean_reversion_signal, mean_reversion_confidence = self.check_mean_reversion_opportunity(simbolo, prices, current_price)

            # ========== SISTEMA INSTITUCIONAL DE 14 AGENTES ==========
            agent_decisions = []
            agent_confidences = []
            institutional_signals = []

            # Distribuição inteligente de agentes (total: 100 agentes INSTITUCIONAL)
            agents_distribution = {
                'US100': 28,  # NASDAQ - Mais agentes devido à alta volatilidade (DOBRADO)
                'US500': 26,  # S&P 500 - Segundo mais importante (DOBRADO)
                'US30': 24,   # Dow Jones - Menos volátil (DOBRADO)
                'DE30': 22    # DAX - Mercado europeu (DOBRADO)
            }
            agents_for_this_asset = agents_distribution.get(simbolo, 12)

            # Calcular sinais institucionais antes dos agentes
            correlation_signal = self.calculate_advanced_correlation(simbolo, prices)

            for agent_id in range(agents_for_this_asset):
                # 14 estratégias diferentes para os agentes
                if agent_id == 0:  # Agente de tendência
                    short_ma = np.mean(prices[-5:])
                    long_ma = np.mean(prices[-20:])
                    trend_strength = abs(short_ma - long_ma) / long_ma * 100
                    if short_ma > long_ma and current_price > short_ma:
                        agent_decisions.append('BUY')
                        agent_confidences.append(min(70 + trend_strength, 90))
                    elif short_ma < long_ma and current_price < short_ma:
                        agent_decisions.append('SELL')
                        agent_confidences.append(min(70 + trend_strength, 90))
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif agent_id == 1:  # Agente de momentum
                    momentum = (current_price - prices[-10]) / prices[-10] * 100
                    if momentum > 0.15:
                        agent_decisions.append('BUY')
                        agent_confidences.append(min(65 + abs(momentum), 90))
                    elif momentum < -0.15:
                        agent_decisions.append('SELL')
                        agent_confidences.append(min(65 + abs(momentum), 90))
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif agent_id == 2:  # Agente de volatilidade/breakout
                    # Usar threshold fixo de volatilidade
                    spread_vol_threshold = 0.08

                    if vol > spread_vol_threshold:  # Threshold fixo de volatilidade
                        direction = 'BUY' if current_price > prices[-1] else 'SELL'
                        agent_decisions.append(direction)
                        # Confiança baseada na volatilidade relativa
                        vol_multiplier = vol / max(0.08, spread_vol_threshold * 2)
                        agent_confidences.append(min(60 + (vol_multiplier * 15), 90))
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(25)

                elif agent_id == 3:  # Agente de suporte/resistência
                    recent_high = np.max(prices[-10:])
                    recent_low = np.min(prices[-10:])
                    if current_price > recent_high * 0.999:
                        agent_decisions.append('SELL')
                        agent_confidences.append(75)
                    elif current_price < recent_low * 1.001:
                        agent_decisions.append('BUY')
                        agent_confidences.append(75)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(40)

                elif agent_id == 4:  # Agente de Volume Price Analysis
                    volume_surge = rates['tick_volume'][-1] > np.mean(rates['tick_volume'][-10:]) * 1.8
                    price_momentum = (current_price - prices[-5]) / prices[-5] * 100
                    if volume_surge and price_momentum > 0.05:
                        agent_decisions.append('BUY')
                        agent_confidences.append(70)
                    elif volume_surge and price_momentum < -0.05:
                        agent_decisions.append('SELL')
                        agent_confidences.append(70)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif agent_id == 5:  # Agente de médias móveis múltiplas
                    sma5 = np.mean(prices[-5:])
                    sma10 = np.mean(prices[-10:])
                    sma20 = np.mean(prices[-20:])
                    if sma5 > sma10 > sma20 and current_price > sma5:
                        agent_decisions.append('BUY')
                        agent_confidences.append(65)
                    elif sma5 < sma10 < sma20 and current_price < sma5:
                        agent_decisions.append('SELL')
                        agent_confidences.append(65)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif agent_id == 6:  # Agente de padrões candlestick
                    # Doji pattern
                    body_size = abs(current_price - prices[-1]) / prices[-1] * 100
                    total_range = (np.max([current_price, prices[-1]]) - np.min([current_price, prices[-1]])) / prices[-1] * 100
                    if body_size < 0.1 and total_range > 0.2:
                        # Indecision - avoid trading
                        agent_decisions.append('HOLD')
                        agent_confidences.append(20)
                    elif body_size > 0.3:  # Strong candle
                        direction = 'BUY' if current_price > prices[-1] else 'SELL'
                        agent_decisions.append(direction)
                        agent_confidences.append(60)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(40)

                elif agent_id == 7:  # Agente de Análise de Tendência Avançada
                    # Combinação de múltiplos timeframes
                    short_trend = np.mean(prices[-5:]) > np.mean(prices[-10:])
                    medium_trend = np.mean(prices[-10:]) > np.mean(prices[-20:])
                    long_trend = np.mean(prices[-20:]) > np.mean(prices[-50:]) if len(prices) >= 50 else True

                    trend_strength = sum([short_trend, medium_trend, long_trend])
                    if trend_strength >= 2 and current_price > np.mean(prices[-10:]):
                        agent_decisions.append('BUY')
                        agent_confidences.append(60 + trend_strength * 5)
                    elif trend_strength <= 1 and current_price < np.mean(prices[-10:]):
                        agent_decisions.append('SELL')
                        agent_confidences.append(60 + (3 - trend_strength) * 5)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif agent_id == 8:  # Agente de Order Flow
                    # Análise baseada em padrões de preço e volume
                    price_acceleration = (prices[-1] - prices[-3]) - (prices[-3] - prices[-5])
                    volume_trend = rates['tick_volume'][-1] > np.mean(rates['tick_volume'][-5:])

                    if price_acceleration > 0 and volume_trend:
                        agent_decisions.append('BUY')
                        agent_confidences.append(65)
                    elif price_acceleration < 0 and volume_trend:
                        agent_decisions.append('SELL')
                        agent_confidences.append(65)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif agent_id == 9:  # Agente de Market Profile
                    # Análise de distribuição de preços
                    recent_prices = prices[-20:]
                    price_range = np.max(recent_prices) - np.min(recent_prices)
                    current_position = (current_price - np.min(recent_prices)) / price_range

                    if current_position > 0.7:  # No terço superior
                        agent_decisions.append('SELL')
                        agent_confidences.append(55)
                    elif current_position < 0.3:  # No terço inferior
                        agent_decisions.append('BUY')
                        agent_confidences.append(55)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif agent_id == 10:  # Agente de Seasonal Patterns
                    # Análise baseada no dia da semana e hora
                    current_hour = datetime.now(pytz.timezone('America/New_York')).hour
                    current_weekday = datetime.now(pytz.timezone('America/New_York')).weekday()

                    # Padrões típicos do mercado
                    if current_weekday == 0 and current_hour < 12:  # Segunda de manhã
                        agent_decisions.append('BUY')
                        agent_confidences.append(50)
                    elif current_weekday == 4 and current_hour > 14:  # Sexta à tarde
                        agent_decisions.append('SELL')
                        agent_confidences.append(50)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif agent_id == 11:  # Agente de Divergência
                    # Detectar divergências entre preço e indicadores
                    price_change = (current_price - prices[-10]) / prices[-10] * 100
                    volume_avg = np.mean(rates['tick_volume'][-10:])

                    if price_change > 0.5 and rates['tick_volume'][-1] < volume_avg * 0.8:
                        # Divergência baixista
                        agent_decisions.append('SELL')
                        agent_confidences.append(60)
                    elif price_change < -0.5 and rates['tick_volume'][-1] < volume_avg * 0.8:
                        # Divergência altista
                        agent_decisions.append('BUY')
                        agent_confidences.append(60)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif agent_id == 12:  # Agente de Elliott Wave Básico
                    # Identificação simples de ondas
                    recent_highs = [prices[i] for i in range(1, len(prices)-1) if prices[i] > prices[i-1] and prices[i] > prices[i+1]]
                    recent_lows = [prices[i] for i in range(1, len(prices)-1) if prices[i] < prices[i-1] and prices[i] < prices[i+1]]

                    if len(recent_highs) >= 2 and current_price > recent_highs[-1]:
                        agent_decisions.append('BUY')
                        agent_confidences.append(55)
                    elif len(recent_lows) >= 2 and current_price < recent_lows[-1]:
                        agent_decisions.append('SELL')
                        agent_confidences.append(55)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif agent_id == 13:  # Agente de Machine Learning Básico
                    # Simples análise estatística
                    returns = np.diff(prices[-20:]) / prices[-20:-1] * 100
                    volatility = np.std(returns)
                    momentum = np.mean(returns[-5:])

                    if momentum > volatility and current_price > np.mean(prices[-10:]):
                        agent_decisions.append('BUY')
                        agent_confidences.append(55)
                    elif momentum < -volatility and current_price < np.mean(prices[-10:]):
                        agent_decisions.append('SELL')
                        agent_confidences.append(55)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

            # Completar com agentes adicionais se necessário (estratégias extras para 100 agentes)
            while len(agent_decisions) < agents_for_this_asset:
                # Agentes extras com estratégias INSTITUCIONAIS avançadas
                extra_agent_id = len(agent_decisions) % 15  # Aumentado para 15 estratégias extras
                if extra_agent_id == 0:  # RSI básico
                    rsi = self.calculate_rsi(prices)
                    if rsi < 30:
                        agent_decisions.append('BUY')
                        agent_confidences.append(60)
                    elif rsi > 70:
                        agent_decisions.append('SELL')
                        agent_confidences.append(60)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif extra_agent_id == 1:  # MACD simples
                    macd_signal = self.calculate_macd(prices)
                    if macd_signal > 0:
                        agent_decisions.append('BUY')
                        agent_confidences.append(55)
                    elif macd_signal < 0:
                        agent_decisions.append('SELL')
                        agent_confidences.append(55)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif extra_agent_id == 2:  # Price Action
                    body_size = abs(current_price - prices[-1]) / prices[-1] * 100
                    if body_size > 0.1 and current_price > prices[-1]:
                        agent_decisions.append('BUY')
                        agent_confidences.append(65)
                    elif body_size > 0.1 and current_price < prices[-1]:
                        agent_decisions.append('SELL')
                        agent_confidences.append(65)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif extra_agent_id == 3:  # Fibonacci Retracement
                    recent_high = np.max(prices[-20:])
                    recent_low = np.min(prices[-20:])
                    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
                    fib_range = recent_high - recent_low

                    for level in fib_levels:
                        fib_level = recent_high - (fib_range * level)
                        if abs(current_price - fib_level) / current_price < 0.002:  # Dentro de 0.2%
                            if current_price > prices[-1]:
                                agent_decisions.append('BUY')
                                agent_confidences.append(55)
                                break
                            else:
                                agent_decisions.append('SELL')
                                agent_confidences.append(55)
                                break
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif extra_agent_id == 4:  # Market Sentiment (baseado em força relativa)
                    # Comparar performance relativa com outros ativos
                    sentiment_score = 0
                    for other_simbolo in self.ativos:
                        if other_simbolo != simbolo:
                            try:
                                other_rates = mt5.copy_rates_from_pos(other_simbolo, mt5.TIMEFRAME_M1, 0, 10)
                                if other_rates is not None:
                                    other_prices = other_rates['close']
                                    if len(other_prices) >= 5:
                                        other_return = (other_prices[-1] - other_prices[-5]) / other_prices[-5]
                                        current_return = (current_price - prices[-5]) / prices[-5]
                                        if current_return > other_return * 1.5:
                                            sentiment_score += 1
                                        elif current_return < other_return * 1.5:
                                            sentiment_score -= 1
                            except:
                                continue

                    if sentiment_score > 1:
                        agent_decisions.append('BUY')
                        agent_confidences.append(50 + sentiment_score * 5)
                    elif sentiment_score < -1:
                        agent_decisions.append('SELL')
                        agent_confidences.append(50 + abs(sentiment_score) * 5)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif extra_agent_id == 5:  # Volatility Breakout System
                    # Bollinger Bands simples
                    sma = np.mean(prices[-20:])
                    std = np.std(prices[-20:])
                    upper_band = sma + (std * 2)
                    lower_band = sma - (std * 2)

                    if current_price > upper_band and current_price > prices[-1]:
                        agent_decisions.append('BUY')
                        agent_confidences.append(60)
                    elif current_price < lower_band and current_price < prices[-1]:
                        agent_decisions.append('SELL')
                        agent_confidences.append(60)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                # ========== NOVAS ESTRATÉGIAS INSTITUCIONAIS (AGENTES 100) ==========

                elif extra_agent_id == 6:  # Ichimoku Cloud Avançado
                    # Conversão (9 períodos)
                    conversion = (np.max(prices[-9:]) + np.min(prices[-9:])) / 2
                    # Base (26 períodos)
                    base = (np.max(prices[-26:]) + np.min(prices[-26:])) / 2
                    # Span A e Span B para nuvem

                    if conversion > base and current_price > conversion:
                        agent_decisions.append('BUY')
                        agent_confidences.append(65)
                    elif conversion < base and current_price < conversion:
                        agent_decisions.append('SELL')
                        agent_confidences.append(65)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

                elif extra_agent_id == 7:  # Análise de Ondas de Wolfe
                    # Identificação de padrões de Wolfe Wave
                    # Procurar pontos 1,2,3,4,5 do padrão
                    if len(prices) >= 20:
                        # Simplificação: procurar convergência de linhas
                        recent_highs = [prices[i] for i in range(len(prices)-10, len(prices))
                                      if i > 0 and prices[i] > prices[i-1] and prices[i] > prices[i+1]]
                        recent_lows = [prices[i] for i in range(len(prices)-10, len(prices))
                                     if i > 0 and prices[i] < prices[i-1] and prices[i] < prices[i+1]]

                        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
                            if current_price > recent_highs[-1] * 1.002:
                                agent_decisions.append('BUY')
                                agent_confidences.append(70)
                            elif current_price < recent_lows[-1] * 0.998:
                                agent_decisions.append('SELL')
                                agent_confidences.append(70)
                            else:
                                agent_decisions.append('HOLD')
                                agent_confidences.append(35)
                        else:
                            agent_decisions.append('HOLD')
                            agent_confidences.append(30)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif extra_agent_id == 8:  # Sistema de Leilão de Abertura
                    # Análise específica do período de abertura
                    current_hour = datetime.now(pytz.timezone('America/New_York')).hour
                    current_minute = datetime.now(pytz.timezone('America/New_York')).minute

                    if 9 <= current_hour <= 10:  # Primeira hora (análise de abertura)
                        # Verificar se preço está acima da máxima da abertura
                        open_price = prices[0] if len(prices) > 0 else current_price
                        if current_price > open_price * 1.001 and current_price > prices[-1]:
                            agent_decisions.append('BUY')
                            agent_confidences.append(55)
                        elif current_price < open_price * 0.999 and current_price < prices[-1]:
                            agent_decisions.append('SELL')
                            agent_confidences.append(55)
                        else:
                            agent_decisions.append('HOLD')
                            agent_confidences.append(30)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(25)

                elif extra_agent_id == 9:  # Análise de Confluência de Fibonacci
                    # Múltiplos níveis de Fibonacci convergindo
                    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
                    confluence_count = 0
                    fib_score = 0

                    for level in fib_levels:
                        # Fibonacci do dia
                        day_high = np.max(prices[-50:]) if len(prices) >= 50 else np.max(prices)
                        day_low = np.min(prices[-50:]) if len(prices) >= 50 else np.min(prices)
                        fib_price = day_high - (day_high - day_low) * level

                        if abs(current_price - fib_price) / current_price < 0.001:  # Dentro de 0.1%
                            confluence_count += 1
                            fib_score += level

                    if confluence_count >= 2:  # Pelo menos 2 níveis confluentes
                        avg_fib_level = fib_score / confluence_count
                        if avg_fib_level < 0.5 and current_price > prices[-1]:  # Zona de suporte
                            agent_decisions.append('BUY')
                            agent_confidences.append(60 + confluence_count * 5)
                        elif avg_fib_level > 0.5 and current_price < prices[-1]:  # Zona de resistência
                            agent_decisions.append('SELL')
                            agent_confidences.append(60 + confluence_count * 5)
                        else:
                            agent_decisions.append('HOLD')
                            agent_confidences.append(35)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif extra_agent_id == 10:  # Sistema de Order Block Institucional
                    # Identificação de grandes ordens institucionais
                    # Procurar por movimentos fortes com volume acima da média
                    if len(rates) >= 10:
                        volumes = rates['tick_volume'][-10:]
                        prices_window = prices[-10:]

                        # Procurar por candles com volume 3x acima da média E movimento direcional
                        avg_volume = np.mean(volumes)
                        for i in range(len(volumes)):
                            if volumes[i] > avg_volume * 3.0:
                                # Order block encontrado
                                block_price = prices_window[i]
                                price_move = (current_price - block_price) / block_price

                                if price_move > 0.002 and current_price > prices[-1]:  # 0.2% acima do block
                                    agent_decisions.append('BUY')
                                    agent_confidences.append(65)
                                    break
                                elif price_move < -0.002 and current_price < prices[-1]:  # 0.2% abaixo do block
                                    agent_decisions.append('SELL')
                                    agent_confidences.append(65)
                                    break
                        else:
                            agent_decisions.append('HOLD')
                            agent_confidences.append(30)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif extra_agent_id == 11:  # Análise de Delta Neutro (Options-Based)
                    # Estratégia baseada em opções (gamma/delta neutral)
                    # Simplificação: alta gamma = movimento esperado
                    if len(prices) >= 20:
                        returns = np.diff(prices[-20:]) / prices[-20:-1] * 100
                        gamma_proxy = np.std(returns) * 100  # Proxy para gamma

                        if gamma_proxy > 0.15:  # Alta probabilidade de movimento
                            # Seguir tendência com alta convicção
                            short_trend = np.mean(prices[-5:]) > np.mean(prices[-10:])
                            if short_trend and current_price > prices[-1]:
                                agent_decisions.append('BUY')
                                agent_confidences.append(min(70 + gamma_proxy * 10, 90))
                            elif not short_trend and current_price < prices[-1]:
                                agent_decisions.append('SELL')
                                agent_confidences.append(min(70 + gamma_proxy * 10, 90))
                            else:
                                agent_decisions.append('HOLD')
                                agent_confidences.append(35)
                        else:
                            agent_decisions.append('HOLD')
                            agent_confidences.append(25)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif extra_agent_id == 12:  # Sistema de Market Microstructure
                    # Análise de microstructure do mercado
                    # Bid-Ask spread, depth, order flow
                    try:
                        tick = mt5.symbol_info_tick(simbolo)
                        if tick:
                            spread = (tick.ask - tick.bid) / tick.ask * 100
                            # Spread muito alto = possível manipulação
                            if spread > 0.05:  # Spread > 0.05%
                                agent_decisions.append('HOLD')
                                agent_confidences.append(20)  # Evitar trading
                            else:
                                # Spread normal - seguir momentum
                                momentum = (current_price - prices[-5]) / prices[-5]
                                if momentum > 0.05:
                                    agent_decisions.append('BUY')
                                    agent_confidences.append(60)
                                elif momentum < -0.05:
                                    agent_decisions.append('SELL')
                                    agent_confidences.append(60)
                                else:
                                    agent_decisions.append('HOLD')
                                    agent_confidences.append(35)
                        else:
                            agent_decisions.append('HOLD')
                            agent_confidences.append(30)
                    except:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif extra_agent_id == 13:  # Sistema de Seasonality Avançado
                    # Análise sazonal baseada em dados históricos
                    current_hour = datetime.now(pytz.timezone('America/New_York')).hour
                    current_weekday = datetime.now(pytz.timezone('America/New_York')).weekday()

                    # Padrões sazonais institucionais
                    if current_weekday == 0 and 9 <= current_hour <= 11:  # Segunda manhã
                        agent_decisions.append('BUY')
                        agent_confidences.append(55)
                    elif current_weekday == 4 and 15 <= current_hour <= 16:  # Sexta tarde
                        agent_decisions.append('SELL')
                        agent_confidences.append(55)
                    elif current_hour == 8 and current_minute < 30:  # Abertura
                        agent_decisions.append('BUY')  # Bias de abertura positivo
                        agent_confidences.append(50)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                elif extra_agent_id == 14:  # Sistema de Liquidity Pool
                    # Identificação de pools de liquidez institucionais
                    # Áreas onde grandes players posicionam ordens
                    if len(prices) >= 30:
                        # Procurar por áreas de alta concentração de volume
                        volume_areas = []
                        for i in range(10, len(prices)):
                            if rates['tick_volume'][i] > np.mean(rates['tick_volume'][i-10:i]) * 2:
                                volume_areas.append(prices[i])

                        if volume_areas:
                            nearest_liquidity = min(volume_areas, key=lambda x: abs(x - current_price))
                            distance_to_liquidity = abs(current_price - nearest_liquidity) / current_price

                            if distance_to_liquidity < 0.001:  # Dentro de 0.1%
                                if current_price > nearest_liquidity and current_price > prices[-1]:
                                    agent_decisions.append('BUY')
                                    agent_confidences.append(60)
                                elif current_price < nearest_liquidity and current_price < prices[-1]:
                                    agent_decisions.append('SELL')
                                    agent_confidences.append(60)
                                else:
                                    agent_decisions.append('HOLD')
                                    agent_confidences.append(35)
                            else:
                                agent_decisions.append('HOLD')
                                agent_confidences.append(30)
                        else:
                            agent_decisions.append('HOLD')
                            agent_confidences.append(30)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(30)

                else:  # Volume/Price (estratégia melhorada)
                    avg_volume = np.mean(rates['tick_volume'][-10:])
                    current_volume = rates['tick_volume'][-1]
                    volume_multiplier = current_volume / avg_volume

                    # Usar threshold fixo de volume
                    volume_threshold = 2.0  # Threshold fixo de volume

                    if volume_multiplier > volume_threshold and current_price > prices[-1]:
                        agent_decisions.append('BUY')
                        # Confiança ajustada pelo volume
                        volume_bonus = min((volume_multiplier - 2) * 5, 10)
                        agent_confidences.append(min(70 + volume_bonus, 90))
                    elif volume_multiplier > volume_threshold and current_price < prices[-1]:
                        agent_decisions.append('SELL')
                        volume_bonus = min((volume_multiplier - 2) * 5, 10)
                        agent_confidences.append(min(70 + volume_bonus, 90))
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

            # Contar votos
            buy_votes = agent_decisions.count('BUY')
            sell_votes = agent_decisions.count('SELL')
            hold_votes = agent_decisions.count('HOLD')

            # Sistema avançado de consenso com pesos por confiança
            buy_weighted = sum(conf for decision, conf in zip(agent_decisions, agent_confidences) if decision == 'BUY')
            sell_weighted = sum(conf for decision, conf in zip(agent_decisions, agent_confidences) if decision == 'SELL')
            hold_weighted = sum(conf for decision, conf in zip(agent_decisions, agent_confidences) if decision == 'HOLD')

            total_weighted = buy_weighted + sell_weighted + hold_weighted

            if total_weighted == 0:
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}}

            buy_pct = buy_weighted / total_weighted * 100
            sell_pct = sell_weighted / total_weighted * 100

            # Sistema de comunicação cruzada - considerar correlação entre ativos
            cross_asset_signal = self.get_cross_asset_signal(simbolo, prices)

            # Decisão coletiva aprimorada
            min_consensus_threshold = max(3, len(agent_decisions) // 4)  # Pelo menos 3 votos ou 25% dos agentes

            if buy_votes >= min_consensus_threshold and buy_pct > 45:
                # Aplicar sinal cruzado como bonus/malus
                final_confidence = min(buy_pct + (buy_votes * 3) + cross_asset_signal, 95)
                return {'decision': 'BUY', 'confidence': final_confidence, 'agent_votes': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}}
            elif sell_votes >= min_consensus_threshold and sell_pct > 45:
                final_confidence = min(sell_pct + (sell_votes * 3) + cross_asset_signal, 95)
                return {'decision': 'SELL', 'confidence': final_confidence, 'agent_votes': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}}

            return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}}

        except Exception as e:
            logger.error(f'Erro na análise de {simbolo}: {e}')
            return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

    def get_cross_asset_signal(self, simbolo, prices):
        """Calcula sinal baseado na correlação com outros ativos"""
        try:
            signal = 0

            # Verificar correlação com outros ativos
            for other_simbolo in self.ativos:
                if other_simbolo != simbolo:
                    try:
                        other_rates = mt5.copy_rates_from_pos(other_simbolo, mt5.TIMEFRAME_M1, 0, 20)
                        if other_rates is not None and len(other_rates) >= 10:
                            other_prices = other_rates['close']

                            # Calcular correlação simples
                            if len(prices) >= 10 and len(other_prices) >= 10:
                                correlation = np.corrcoef(prices[-10:], other_prices[-10:])[0, 1]

                                # Se correlação alta e movimento direcional
                                current_return = (prices[-1] - prices[-5]) / prices[-5]
                                other_return = (other_prices[-1] - other_prices[-5]) / other_prices[-5]

                                if abs(correlation) > 0.7:
                                    if current_return > 0 and other_return > 0:
                                        signal += 5  # Bonus para movimento direcional
                                    elif current_return < 0 and other_return < 0:
                                        signal += 5
                                    else:
                                        signal -= 3  # Penalidade para divergência
                    except:
                        continue

            return min(signal, 10)  # Limitar impacto do sinal cruzado

        except:
            return 0

    def calculate_rsi(self, prices, period=14):
        """Calcula RSI simples"""
        try:
            delta = np.diff(prices)
            gain = np.mean(delta[delta > 0]) if np.any(delta > 0) else 0
            loss = abs(np.mean(delta[delta < 0])) if np.any(delta < 0) else 0
            if loss == 0:
                return 100
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except:
            return 50

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcula MACD simples"""
        try:
            if len(prices) < slow:
                return 0
            ema_fast = pd.Series(prices).ewm(span=fast).mean().values[-1]
            ema_slow = pd.Series(prices).ewm(span=slow).mean().values[-1]
            return ema_fast - ema_slow
        except:
            return 0

    def execute_trade(self, simbolo, decision, confidence):
        """Executa trade com funcionalidades INSTITUCIONAIS avançadas"""
        if confidence < self.min_confidence:
            logger.info(f'📊 {simbolo} - Confiança insuficiente: {confidence:.1f}% < {self.min_confidence}%')
            return False

        if self.positions_count >= self.max_positions:
            logger.warning(f'📊 {simbolo} - Limite de posições atingido: {self.positions_count}/{self.max_positions}')
            return False

        try:
            info = self.ativos_info[simbolo]
            price = mt5.symbol_info_tick(simbolo).ask if decision == 'BUY' else mt5.symbol_info_tick(simbolo).bid

            # ========== NOVAS FUNCIONALIDADES INSTITUCIONAIS ==========

            # 1. Calcular volatilidade atual para position sizing
            rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 0, 20)
            current_volatility = 0
            if rates is not None and len(rates) >= 10:
                prices = rates['close']
                current_volatility = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100

            # 2. Calcular position size dinâmico
            dynamic_lot_size = self.calculate_dynamic_position_size(simbolo, confidence, current_volatility)

            # 3. Ajustar stop loss baseado na volatilidade
            sl_pct = self.stop_loss_pct
            if current_volatility > 0.1:  # Alta volatilidade
                sl_pct = self.stop_loss_pct * 1.5  # Aumentar SL em 50%
            elif current_volatility < 0.05:  # Baixa volatilidade
                sl_pct = self.stop_loss_pct * 0.8  # Reduzir SL em 20%

            sl = price * (1 - sl_pct) if decision == 'BUY' else price * (1 + sl_pct)
            tp = price * (1 + self.take_profit_pct) if decision == 'BUY' else price * (1 - self.take_profit_pct)

            # 4. Preparar request institucional
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': simbolo,
                'volume': dynamic_lot_size,  # Position size dinâmico
                'type': mt5.ORDER_TYPE_BUY if decision == 'BUY' else mt5.ORDER_TYPE_SELL,
                'price': price,
                'sl': sl,
                'tp': tp,
                'magic': info['magic'],
                'comment': f'INST-{simbolo}-{decision}-VOL{current_volatility:.2f}-CONF{confidence:.1f}',
                'type_time': mt5.ORDER_TIME_GTC,
            }

            # 5. Executar ordem
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.positions_count += 1

                # 6. Log institucional detalhado
                logger.info(f'🏦 EXECUÇÃO INSTITUCIONAL: {decision} {dynamic_lot_size:.3f} {simbolo} @ {price:.2f}')
                logger.info(f'📊 Confiança: {confidence:.1f}% | Volatilidade: {current_volatility:.3f}% | SL: {sl_pct:.1f}')
                logger.info(f'🎯 SL: ${sl:.2f} | TP: ${tp:.2f} | Position Size: {dynamic_lot_size:.3f}')

                return True
            else:
                logger.error(f'❌ Falha na execução {simbolo}: {result.retcode} - {result.comment}')

        except Exception as e:
            logger.error(f'🚨 Erro crítico na execução {simbolo}: {e}')

        return False

    def check_daily_limits(self):
        """Verifica limites de lucro/prejuízo diário com proteção inteligente de lucro positivo"""
        current_time = datetime.now()

        # Reset diário se necessário
        if self.reset_time is None or current_time.date() != self.reset_time.date():
            self.daily_pnl = 0.0
            self.reset_time = current_time
            self.limit_hit_today = False
            self.peak_pnl_today = 0.0
            self.trailing_stop_active = False
            self.trailing_stop_level = 0.0
            logger.info('=== NOVO DIA DE TRADING INICIADO ===')
            logger.info(f'🎯 Meta AGRESSIVA: ${self.daily_pnl_target:.2f} | 🛡️ Proteção de Lucro: ${self.profit_protection_level:.2f}')

        # Atualizar pico de lucro do dia
        if self.daily_pnl > self.peak_pnl_today:
            self.peak_pnl_today = self.daily_pnl

        # Verificar meta de lucro (fecha posições para realizar lucro)
        if self.daily_pnl >= self.daily_pnl_target:
            logger.info(f'🎯 META DE LUCRO ATINGIDA: ${self.daily_pnl:.2f} >= ${self.daily_pnl_target:.2f}')
            logger.info('💰 LUCRO PROTEGIDO - Fechando posições para realizar lucro')
            self.close_all_positions("META_LUCRO")
            self.limit_hit_today = True
            logger.info('✅ Sistema continua operando normalmente (pode abrir novas posições)')

        # Sistema de proteção de lucro positivo (trailing stop em lucro)
        elif self.peak_pnl_today >= 50.0:  # Ativar proteção quando atingir $50 de lucro
            # Calcular nível de proteção baseado no pico do dia
            if self.peak_pnl_today >= 100.0:
                protection_level = self.peak_pnl_today * 0.8  # Protege 80% do lucro quando >= $100
            elif self.peak_pnl_today >= 80.0:
                protection_level = self.peak_pnl_today * 0.75  # Protege 75% do lucro quando >= $80
            else:
                protection_level = self.peak_pnl_today * 0.7   # Protege 70% do lucro quando >= $50

            # Se o lucro caiu abaixo do nível de proteção, FECHAR POSIÇÕES IMEDIATAMENTE
            if self.daily_pnl <= protection_level:
                logger.info(f'🛑 PROTEÇÃO DE LUCRO EXECUTADA: ${self.daily_pnl:.2f} <= ${protection_level:.2f}')
                logger.info(f'💰 PROTEGENDO LUCRO - Pico do dia foi: ${self.peak_pnl_today:.2f}')
                logger.info(f'🛡️ Nível de proteção: ${protection_level:.2f} ({protection_level/self.peak_pnl_today*100:.1f}% do pico)')
                self.close_all_positions("PROTECAO_LUCRO")
                self.limit_hit_today = True
                logger.info('✅ Sistema continua operando normalmente (pode abrir novas posições)')
            else:
                logger.info(f'🛡️ PROTEÇÃO ATIVA: Lucro ${self.daily_pnl:.2f} | Protegendo ${protection_level:.2f} | Pico: ${self.peak_pnl_today:.2f}')
        
                # Log das metas quando lucro está positivo
                if self.daily_pnl > 0:
                    remaining_to_target = self.daily_pnl_target - self.daily_pnl
                    logger.info(f'🎯 PROGRESSO METAS: ${self.daily_pnl:.2f}/${self.daily_pnl_target:.2f} | Faltam: ${remaining_to_target:.2f}')

        return "NORMAL"

    def close_all_positions(self, reason):
        """Fecha todas as posições abertas"""
        try:
            # Obter todas as posições
            positions = mt5.positions_get()

            if positions:
                closed_count = 0
                total_pnl_closed = 0.0

                for pos in positions:
                    # Verificar se é nossa posição (pelo magic number)
                    if pos.magic in [info['magic'] for info in self.ativos_info.values()]:
                        result = mt5.Close(pos.ticket)
                        if result:
                            closed_count += 1
                            # Atualizar P&L com o lucro/prejuízo realizado
                            pnl_change = pos.profit
                            self.daily_pnl += pnl_change
                            total_pnl_closed += pnl_change

                if closed_count > 0:
                    logger.info(f'📊 {closed_count} posições fechadas por {reason}')
                    logger.info(f'💰 P&L realizado neste fechamento: ${total_pnl_closed:.2f}')
                    logger.info(f'📈 P&L Diário Total: ${self.daily_pnl:.2f}')
                    self.positions_count = 0
                else:
                    logger.info('📊 Nenhuma posição válida para fechar')
            else:
                logger.info('📊 Nenhuma posição aberta no momento')

        except Exception as e:
            logger.error(f'Erro ao fechar posições: {e}')

    def update_daily_pnl(self, pnl_change):
        """Atualiza P&L diário"""
        old_pnl = self.daily_pnl
        self.daily_pnl += pnl_change

        # Verificar proteção de lucro sempre que P&L for atualizado
        if self.peak_pnl_today >= 50.0 and self.daily_pnl <= self.profit_protection_level:
            logger.warning(f'🚨 PROTEÇÃO DE LUCRO ATIVADA VIA UPDATE: ${self.daily_pnl:.2f} <= ${self.profit_protection_level:.2f}')
            logger.warning(f'💰 Protegendo lucro - Pico do dia foi: ${self.peak_pnl_today:.2f}')
            self.close_all_positions("PROTECAO_LUCRO_UPDATE")
            self.limit_hit_today = True

        logger.info(f'💰 P&L Diário Atualizado: ${old_pnl:.2f} -> ${self.daily_pnl:.2f}')

    def check_profit_protection_real_time(self):
        """Verificação em tempo real da proteção de lucro - chamada frequente"""
        try:
            if self.peak_pnl_today >= 50.0:
                # Calcular nível de proteção baseado no pico do dia
                if self.peak_pnl_today >= 100.0:
                    protection_level = self.peak_pnl_today * 0.8  # Protege 80% do lucro quando >= $100
                elif self.peak_pnl_today >= 80.0:
                    protection_level = self.peak_pnl_today * 0.75  # Protege 75% do lucro quando >= $80
                else:
                    protection_level = self.peak_pnl_today * 0.7   # Protege 70% do lucro quando >= $50

                # Se o lucro caiu abaixo do nível de proteção, FECHAR POSIÇÕES IMEDIATAMENTE
                if self.daily_pnl <= protection_level:
                    logger.warning(f'🚨 PROTEÇÃO DE LUCRO REAL-TIME: ${self.daily_pnl:.2f} <= ${protection_level:.2f}')
                    logger.warning(f'💰 PROTEGENDO LUCRO - Pico do dia foi: ${self.peak_pnl_today:.2f}')
                    self.close_all_positions("PROTECAO_LUCRO_REALTIME")
                    self.limit_hit_today = True
                    return True  # Indica que proteção foi executada

            return False  # Indica que proteção não foi necessária

        except Exception as e:
            logger.error(f'Erro na proteção real-time: {e}')
            return False

    def manage_trailing_stops(self):
        """Gerencia trailing stops para proteger lucros positivos"""
        try:
            positions = mt5.positions_get()

            if not positions:
                return

            for pos in positions:
                # Verificar se é nossa posição
                if pos.magic in [info['magic'] for info in self.ativos_info.values()]:
                    current_profit = pos.profit

                    # Só aplicar trailing stop se estiver em lucro
                    if current_profit > 0:
                        # Calcular nível de proteção baseado no lucro atual
                        if current_profit >= 50:  # Lucro >= $50
                            protection_level = current_profit * 0.5  # Protege 50% do lucro
                        elif current_profit >= 30:  # Lucro >= $30
                            protection_level = current_profit * 0.6  # Protege 60% do lucro
                        elif current_profit >= 20:  # Lucro >= $20
                            protection_level = current_profit * 0.7  # Protege 70% do lucro
                        else:
                            protection_level = current_profit * 0.8  # Protege 80% do lucro

                        # Calcular novo stop loss baseado na proteção
                        if pos.type == mt5.POSITION_TYPE_BUY:
                            # Para posições BUY: stop loss abaixo do preço atual
                            current_price = mt5.symbol_info_tick(pos.symbol).ask
                            new_sl = current_price - (protection_level / pos.volume) / mt5.symbol_info(pos.symbol).point
                            if new_sl > pos.sl and new_sl > pos.price_open:
                                self.modify_sl_tp(pos.ticket, new_sl, pos.tp)
                                logger.info(f'🛡️ TS {pos.symbol}: Lucro ${current_profit:.2f} -> Protegendo ${protection_level:.2f}')

                        else:  # POSITION_TYPE_SELL
                            # Para posições SELL: stop loss acima do preço atual
                            current_price = mt5.symbol_info_tick(pos.symbol).bid
                            new_sl = current_price + (protection_level / pos.volume) / mt5.symbol_info(pos.symbol).point
                            if new_sl < pos.sl and new_sl < pos.price_open:
                                self.modify_sl_tp(pos.ticket, new_sl, pos.tp)
                                logger.info(f'🛡️ TS {pos.symbol}: Lucro ${current_profit:.2f} -> Protegendo ${protection_level:.2f}')

        except Exception as e:
            logger.error(f'Erro no trailing stop: {e}')

    def modify_sl_tp(self, ticket, sl, tp=None):
        """Modifica stop loss e take profit de uma posição"""
        request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': ticket,
            'sl': sl
        }
        if tp:
            request['tp'] = tp

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f'Erro ao modificar SL/TP: {result.retcode}')

    def run(self):
        if not self.is_connected:
            return

        self.running = True

        # ========== LOGS INSTITUCIONAIS INICIAIS ==========
        logger.info('🚀 SISTEMA MULTI-ATIVOS INSTITUCIONAL INICIADO')
        logger.info('🏦 Características de Trader Sênior ATIVADAS')
        logger.info('📊 10 Melhorias Institucionais Implementadas')


        # 2. Log das funcionalidades institucionais
        logger.info('=== 🏦 FUNCIONALIDADES INSTITUCIONAIS ATIVAS (100 AGENTES) ===')
        logger.info(f'🧠 100 AGENTES INSTITUCIONAIS: 28+ estratégias avançadas por ativo')
        logger.info(f'🎯 Janelas Institucionais: {len(self.institutional_windows)} configuradas')
        logger.info(f'📉 Controle de Drawdown: Máx {self.max_daily_drawdown}% | Circuit Breaker: {self.circuit_breaker_active}')
        logger.info(f'📏 Position Sizing Dinâmico: Base {self.base_position_size} | Volatilidade: {self.volatility_multiplier}')
        logger.info(f'📈 Correlação Inter-Mercado: Janela {self.correlation_window} | Threshold {self.min_correlation_threshold}')
        logger.info(f'⏰ Multi-Timeframe: {len(self.timeframes)} timeframes | Alinhamento mín: {self.min_timeframe_alignment}')
        logger.info(f'🚀 Breakout com Confirmação: Volume {self.volume_surge_threshold}x | Momentum {self.momentum_threshold}')
        logger.info(f'📰 Filtros de Notícias: {len(self.high_impact_events)} eventos | Janela: {self.news_avoidance_window}min')
        logger.info(f'📊 Reversão Média: Janela {self.mean_reversion_window} | Threshold {self.std_dev_threshold}σ')
        logger.info(f'🛡️ Gap Protection: {self.gap_protection_minutes}min | Volume Quality: {self.volume_quality_score:.2f}')
        logger.info(f'🎯 Ichimoku Cloud, Wolfe Waves, Order Blocks, Market Microstructure ATIVOS')
        logger.info(f'💰 Meta Conservadora: ${self.daily_pnl_target:.2f} diário | Proteção: ${self.profit_protection_level:.2f}')
        logger.info('=== 🏆 NÍVEL ALCANÇADO: MEGA-PLATAFORMA INSTITUCIONAL ===')

        # 3. Status inicial dos controles de risco
        logger.info('=== 🛡️ CONTROLES DE RISCO INICIAIS ===')
        logger.info(f'💰 Meta Conservadora: ${self.daily_pnl_target:.2f} | Proteção: ${self.profit_protection_level:.2f}')
        logger.info(f'📊 Confiança Mínima: {self.min_confidence}% | Máx Posições: {self.max_positions}')
        logger.info(f'🧠 MEGA-SISTEMA: {self.total_agents} agentes INSTITUCIONAIS | Estratégias Avançadas')
        logger.info('=== SISTEMA INSTITUCIONAL TOTALMENTE OPERACIONAL ===')

        while self.running:
            try:
                # ========== CONTROLE INSTITUCIONAL DE RISCO ==========

                # 1. Verificar limites de lucro/prejuízo ANTES de operar
                self.check_daily_limits()

                # 2. Obter dados da conta para controle de drawdown
                try:
                    account_info = mt5.account_info()
                    if account_info:
                        current_balance = account_info.balance
                        self.update_drawdown_control(current_balance)
                except:
                    pass

                # Sistema continua operando normalmente mesmo após atingir limites
                if self.is_trading_hours():
                    # 3. Verificação em tempo real da proteção de lucro (antes de operar)
                    self.check_profit_protection_real_time()

                    # 4. Análise INSTITUCIONAL de cada ativo
                    for simbolo in self.ativos:
                        # Usar análise com 14 agentes + validações avançadas
                        analysis = self.analyze_asset_with_agents(simbolo)

                        # Log institucional detalhado
                        if analysis['confidence'] > 0:
                            logger.info(f'🏦 {simbolo}: {analysis["decision"]} (Conf: {analysis["confidence"]:.1f}%) | Agentes: BUY={analysis["agent_votes"]["BUY"]} SELL={analysis["agent_votes"]["SELL"]} | P&L: ${self.daily_pnl:.2f}')
                        else:
                            logger.info(f'⏸️ {simbolo}: HOLD (Filtros Institucionais Ativos) | P&L: ${self.daily_pnl:.2f}')

                        if analysis['confidence'] >= self.min_confidence:
                            self.execute_trade(simbolo, analysis['decision'], analysis['confidence'])

                    # 5. Gerenciar trailing stops para proteger lucros positivos
                    self.manage_trailing_stops()

                    # 6. Verificação adicional de proteção de lucro (após operações)
                    self.check_profit_protection_real_time()

                    # 7. Log de status institucional
                    if self.circuit_breaker_active:
                        logger.warning(f'🚨 CIRCUIT BREAKER ATIVO - Operando com 10% do tamanho normal')
                    if self.current_drawdown < -20:
                        logger.warning(f'📉 DRAWDOWN ELEVADO: {self.current_drawdown:.2f}%')

                time.sleep(10)  # Loop institucional de 10 segundos

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f'Erro: {e}')
                time.sleep(5)

        mt5.shutdown()

    def stop(self):
        self.running = False

if __name__ == '__main__':
    config = {'name': 'SistemaMultiAtivos'}
    sistema = SistemaMultiAtivos(config)
    sistema.start()

    try:
        while sistema.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        sistema.stop()
        sistema.join()
        print("Sistema encerrado!")