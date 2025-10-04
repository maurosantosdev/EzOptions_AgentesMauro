#!/usr/bin/env python3
"""
SISTEMA MULTI-ATIVOS SIMPLIFICADO
Opera com US100, US500, US30 e DE30
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

        # Spreads base para cada ativo
        self.spreads_base = {
            'US100': 40,  # NASDAQ
            'US500': 60,  # S&P 500
            'US30': 50,   # Dow Jones
            'DE30': 45    # DAX
        }

        # Sistema de ajuste automático de spread por dia da semana
        self.spread_adjustments = {
            0: 1,  # Segunda: +1
            1: 2,  # Terça: +2
            2: 1,  # Quarta: +1
            3: 2,  # Quinta: +2
            4: 2   # Sexta: +2
        }

        self.ativos_info = {
            'US100': {'magic': 234001, 'lot': 0.01},
            'US500': {'magic': 234002, 'lot': 0.01},
            'US30': {'magic': 234003, 'lot': 0.01},
            'DE30': {'magic': 234004, 'lot': 0.01}
        }

        # Sistema de 50 agentes distribuídos por ativo (trabalhando simultaneamente)
        self.agents_distribution = {
            'US100': 14,  # NASDAQ - Mais agentes devido à alta volatilidade
            'US500': 13,  # S&P 500 - Segundo mais importante
            'US30': 12,   # Dow Jones - Menos volátil
            'DE30': 11    # DAX - Mercado europeu
        }
        self.agents_per_asset = 12  # Base de agentes por ativo
        self.total_agents = 50  # Total de agentes trabalhando simultaneamente

        # Configurações
        self.min_confidence = 55.0
        self.max_positions = 20
        self.stop_loss_pct = 0.10
        self.take_profit_pct = 0.25

        # Estado
        self.is_connected = False
        self.running = False
        self.positions_count = 0

        # Controle de lucro/prejuízo diário (trader experiente)
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
        logger.info(f'🤖 Total de agentes: {self.total_agents} (distribuídos: US100={self.agents_distribution["US100"]}, US500={self.agents_distribution["US500"]}, US30={self.agents_distribution["US30"]}, DE30={self.agents_distribution["DE30"]})')
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

    def get_dynamic_spread(self, simbolo):
        """Calcula spread dinâmico baseado no dia da semana"""
        current_weekday = datetime.now(pytz.timezone('America/New_York')).weekday()
        base_spread = self.spreads_base.get(simbolo, 50)
        adjustment = self.spread_adjustments.get(current_weekday, 0)

        dynamic_spread = base_spread + adjustment

        # Log do spread atual para monitoramento
        logger.info(f'📊 {simbolo} - Spread Base: {base_spread} | Ajuste Hoje: +{adjustment} | Spread Dinâmico: {dynamic_spread}')

        return dynamic_spread

    def is_trading_hours(self):
        now = datetime.now(pytz.timezone('America/New_York'))
        if not (0 <= now.weekday() <= 4):
            return False
        t = now.time()
        return datetime_time(8, 0) <= t < datetime_time(17, 0)

    def analyze_asset_with_agents(self, simbolo):
        """Análise com 14 agentes trabalhando simultaneamente"""
        try:
            rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 0, 50)
            if rates is None or len(rates) < 20:
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': 14}}

            prices = rates['close']
            current_price = prices[-1]

            # Volatilidade com spread dinâmico
            vol = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
            dynamic_spread = self.get_dynamic_spread(simbolo)

            # Converter spread dinâmico para threshold de volatilidade (spread/10000 para normalizar)
            min_vol_threshold = dynamic_spread / 10000.0

            if vol <= min_vol_threshold:  # Volatilidade mínima baseada no spread dinâmico
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': self.total_agents}}

            # Sistema de 14 agentes trabalhando simultaneamente
            agent_decisions = []
            agent_confidences = []

            # Distribuição inteligente de agentes (total: 50 agentes)
            agents_distribution = {
                'US100': 14,  # NASDAQ - Mais agentes devido à alta volatilidade
                'US500': 13,  # S&P 500 - Segundo mais importante
                'US30': 12,   # Dow Jones - Menos volátil
                'DE30': 11    # DAX - Mercado europeu
            }
            agents_for_this_asset = agents_distribution.get(simbolo, 12)

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

                elif agent_id == 2:  # Agente de volatilidade/breakout com spread dinâmico
                    dynamic_spread = self.get_dynamic_spread(simbolo)
                    # Usar spread dinâmico como threshold adicional (convertido para volatilidade)
                    spread_vol_threshold = dynamic_spread / 10000.0

                    if vol > max(0.08, spread_vol_threshold * 2):  # Combina threshold fixo com spread dinâmico
                        direction = 'BUY' if current_price > prices[-1] else 'SELL'
                        agent_decisions.append(direction)
                        # Confiança baseada na volatilidade relativa ao spread dinâmico
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

            # Completar com agentes adicionais se necessário (estratégias extras para 28 agentes)
            while len(agent_decisions) < agents_for_this_asset:
                # Agentes extras com estratégias variadas
                extra_agent_id = len(agent_decisions) % 5
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

                else:  # Volume/Price (estratégia melhorada com spread dinâmico)
                    avg_volume = np.mean(rates['tick_volume'][-10:])
                    current_volume = rates['tick_volume'][-1]
                    volume_multiplier = current_volume / avg_volume

                    # Ajustar threshold baseado no spread dinâmico
                    dynamic_spread = self.get_dynamic_spread(simbolo)
                    spread_adjustment = dynamic_spread / 100.0  # Convertendo para ajuste de volume
                    volume_threshold = max(2.0, 2.0 - spread_adjustment)  # Spread maior = threshold menor

                    if volume_multiplier > volume_threshold and current_price > prices[-1]:
                        agent_decisions.append('BUY')
                        # Confiança ajustada pelo spread dinâmico
                        spread_bonus = min(spread_adjustment * 5, 10)
                        agent_confidences.append(min(70 + (volume_multiplier - 2) * 10 + spread_bonus, 90))
                    elif volume_multiplier > volume_threshold and current_price < prices[-1]:
                        agent_decisions.append('SELL')
                        spread_bonus = min(spread_adjustment * 5, 10)
                        agent_confidences.append(min(70 + (volume_multiplier - 2) * 10 + spread_bonus, 90))
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
        if confidence < self.min_confidence:
            return False

        if self.positions_count >= self.max_positions:
            return False

        try:
            info = self.ativos_info[simbolo]
            price = mt5.symbol_info_tick(simbolo).ask if decision == 'BUY' else mt5.symbol_info_tick(simbolo).bid

            sl = price * (1 - self.stop_loss_pct) if decision == 'BUY' else price * (1 + self.stop_loss_pct)
            tp = price * (1 + self.take_profit_pct) if decision == 'BUY' else price * (1 - self.take_profit_pct)

            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': simbolo,
                'volume': info['lot'],
                'type': mt5.ORDER_TYPE_BUY if decision == 'BUY' else mt5.ORDER_TYPE_SELL,
                'price': price,
                'sl': sl,
                'tp': tp,
                'magic': info['magic'],
                'comment': f'Multi-{simbolo}-{decision}',
                'type_time': mt5.ORDER_TIME_GTC,
            }

            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.positions_count += 1
                logger.info(f'EXECUTADO: {decision} {info["lot"]} {simbolo} @ {price:.2f} | Conf: {confidence:.1f}%')
                return True

        except Exception as e:
            logger.error(f'Erro {simbolo}: {e}')

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
            logger.info(f'🎯 Meta de Lucro: ${self.daily_pnl_target:.2f} | 🛡️ Proteção de Lucro: ${self.profit_protection_level:.2f}')

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
        logger.info('Sistema Multi-Ativos com 14 Agentes iniciado')

        # Log dos spreads dinâmicos configurados para hoje
        logger.info('=== CONFIGURAÇÃO DE SPREADS DINÂMICOS ===')
        current_weekday = datetime.now(pytz.timezone('America/New_York')).weekday()
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        dia_atual = dias_semana[current_weekday] if 0 <= current_weekday <= 4 else 'Fim de Semana'
        logger.info(f'📅 Dia da Semana: {dia_atual}')

        for simbolo in self.ativos:
            base_spread = self.spreads_base[simbolo]
            adjustment = self.spread_adjustments.get(current_weekday, 0)
            dynamic_spread = base_spread + adjustment
            logger.info(f'📊 {simbolo}: Base {base_spread} + Ajuste +{adjustment} = Spread Dinâmico {dynamic_spread}')
        logger.info('=== SISTEMA OPERANDO COM SPREADS DINÂMICOS ===')

        while self.running:
            try:
                # Verificar limites de lucro/prejuízo ANTES de operar
                self.check_daily_limits()

                # Sistema continua operando normalmente mesmo após atingir limites
                if self.is_trading_hours():
                    # Verificação em tempo real da proteção de lucro (antes de operar)
                    self.check_profit_protection_real_time()

                    for simbolo in self.ativos:
                        # Usar análise com 14 agentes simultâneos
                        analysis = self.analyze_asset_with_agents(simbolo)
                        logger.info(f'{simbolo}: {analysis["decision"]} (Conf: {analysis["confidence"]:.1f}%) | Agentes: BUY={analysis["agent_votes"]["BUY"]} SELL={analysis["agent_votes"]["SELL"]} | P&L Diario: ${self.daily_pnl:.2f}')

                        if analysis['confidence'] >= self.min_confidence:
                            self.execute_trade(simbolo, analysis['decision'], analysis['confidence'])

                    # Gerenciar trailing stops para proteger lucros positivos
                    self.manage_trailing_stops()

                    # Verificação adicional de proteção de lucro (após operações)
                    self.check_profit_protection_real_time()

                time.sleep(10)  # Reduzido para 10 segundos para melhor responsividade

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