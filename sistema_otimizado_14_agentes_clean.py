import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import threading
from datetime import datetime, time as datetime_time
import pytz
import logging
import yfinance as yf
import pandas as pd
import numpy as np
from trading_setups import TradingSetupAnalyzer, SetupType

# Configurar logging sem emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_otimizado.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SistemaOtimizado14Agentes(threading.Thread):
    """Sistema otimizado com 14 agentes para MAXIMIZAR LUCROS"""
    
    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.name = config.get('name', 'SistemaOtimizado')
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 234001)
        self.lot_size = config.get('lot_size', 0.01)
        
        # CONFIGURAÇÕES OTIMIZADAS PARA LUCRO
        self.min_confidence = 80.0  # Aumentado para sinais mais confiáveis
        self.max_positions = 2  # Apenas 2 posições máximas para controle
        self.stop_loss_pct = 0.15  # SL mais apertado para proteger capital
        self.take_profit_pct = 2.0  # TP mais alto para maximizar lucros
        self.max_daily_loss = -15.0  # Stop loss diário mais conservador
        self.max_operations_per_day = 3  # Limite de operações por segurança
        
        # Controles avançados
        self.daily_operations = 0
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        self.position_count = 0
        self.current_positions = []
        
        # Conectar ao MT5
        self.is_connected = False
        self.connect_mt5()
        
        # Inicializar analisador de setups
        self.setup_analyzer = TradingSetupAnalyzer()
    
    def connect_mt5(self):
        """Conectar ao MT5 com as credenciais"""
        login = int(os.getenv('MT5_LOGIN', '103486755'))
        server = os.getenv('MT5_SERVER', 'FBS-Demo')
        password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')
        
        if mt5.initialize(login=login, server=server, password=password):
            self.is_connected = True
            logger.info(f'[{self.name}] Conectado ao MT5 com sucesso!')
            
            # Verificar se o símbolo está disponível
            if mt5.symbol_select(self.symbol, True):
                logger.info(f'[{self.name}] Símbolo {self.symbol} selecionado')
                
                # Verificar se o Auto Trading está habilitado
                account_info = mt5.account_info()
                if account_info:
                    if account_info.trade_expert and account_info.trade_allowed:
                        logger.info(f'[{self.name}] Auto Trading HABILITADO - Pronto para operar!')
                    else:
                        logger.warning(f'[{self.name}] Auto Trading DESABILITADO - verifique no MT5')
                else:
                    logger.error(f'[{self.name}] Não foi possível obter informações da conta')
            else:
                logger.error(f'[{self.name}] Não foi possível selecionar o símbolo {self.symbol}')
                self.is_connected = False
        else:
            logger.error(f'[{self.name}] Falha ao conectar ao MT5')
    
    def is_trading_hours(self):
        """Verifica se está no horário de trading ideal"""
        ny_tz = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(ny_tz)
        if not (0 <= current_time_ny.weekday() <= 4):  # Segunda a sexta
            return False
            
        # Horário comercial (09:00-16:00 NY) - horário de maior liquidez
        market_open = datetime_time(9, 0, 0)
        market_close = datetime_time(16, 0, 0)
        current_time = current_time_ny.time()
        
        return market_open <= current_time < market_close
    
    def get_market_data(self):
        """Obtém dados de mercado avançados"""
        if not self.is_connected:
            return None
            
        try:
            # Obter tick atual
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return None
                
            # Obter dados históricos de diferentes timeframes
            rates_m1 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 100)
            rates_m5 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 50)
            rates_m15 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M15, 0, 20)
            
            if rates_m1 is None or len(rates_m1) < 50:
                return None
                
            return {
                'current_price': tick.ask,
                'bid': tick.bid,
                'ask': tick.ask,
                'historical_m1': rates_m1,
                'historical_m5': rates_m5,
                'historical_m15': rates_m15,
                'volume': tick.volume,
                'spread': tick.ask - tick.bid,
                'time': tick.time
            }
        except Exception as e:
            logger.error(f'Erro ao obter dados de mercado: {e}')
            return None
    
    def calculate_vwap(self, rates):
        """Calcula VWAP para análise de força"""
        try:
            typical_price = (rates['high'] + rates['low'] + rates['close']) / 3
            volume = rates['tick_volume']
            
            vwap = (typical_price * volume).sum() / volume.sum() if volume.sum() > 0 else typical_price[-1]
            std1_upper = vwap + 1 * np.std(typical_price)
            std1_lower = vwap - 1 * np.std(typical_price)
            
            return {'vwap': vwap, 'std1_upper': std1_upper, 'std1_lower': std1_lower}
        except:
            return {'vwap': 0, 'std1_upper': 0, 'std1_lower': 0}
    
    def analyze_with_14_agentes(self, market_data):
        """Executa análise com 14 agentes especializados para lucro máximo"""
        if not market_data:
            return None
            
        # Calcular VWAP para análise
        vwap_data = self.calculate_vwap(market_data['historical_m1'])
        
        # Agentes de análise (criando 14 agentes a partir dos 10 existentes + variações)
        agentes = [
            # Agentes de Tendência
            self.agente_trend_following(market_data),
            self.agente_multi_timeframe(market_data),
            self.agente_ema_crossover(market_data),
            
            # Agentes de Força (Gamma, Delta, Charm)
            self.agente_gamma_analyzer(market_data),
            self.agente_delta_analyzer(market_data),
            self.agente_charm_analyzer(market_data),
            
            # Agentes de Volume e Momentum
            self.agente_volume_spike(market_data),
            self.agente_momentum(market_data),
            self.agente_rsi_oversold(market_data),
            
            # Agentes de Suporte/Resistência
            self.agente_support_resistance(market_data),
            self.agente_bollinger_breakout(market_data),
            self.agente_price_action(market_data),
            
            # Agentes de Previsão
            self.agente_prediction(market_data),
            self.agente_consolidation_detector(market_data)
        ]
        
        # Filtrar apenas agentes com alta confiança (>= 75%)
        high_conf_agents = [a for a in agentes if a['confidence'] >= 75.0]
        
        if not high_conf_agents:
            return None
        
        # Calcular decisão final baseada na maioria de agentes confiáveis
        buy_votes = sum(1 for a in high_conf_agents if a['decision'] == 'BUY')
        sell_votes = sum(1 for a in high_conf_agents if a['decision'] == 'SELL')
        hold_votes = sum(1 for a in high_conf_agents if a['decision'] == 'HOLD')
        
        # Calcular confiança final baseada na maioria e na força dos sinais
        total_votes = len(high_conf_agents)
        if total_votes == 0:
            return None
            
        if buy_votes > sell_votes:
            final_decision = 'BUY'
            final_confidence = (buy_votes / total_votes) * max(a['confidence'] for a in high_conf_agents)
        elif sell_votes > buy_votes:
            final_decision = 'SELL'
            final_confidence = (sell_votes / total_votes) * max(a['confidence'] for a in high_conf_agents)
        else:
            final_decision = 'HOLD'
            final_confidence = 0
            
        return {
            'decision': final_decision,
            'confidence': min(95.0, final_confidence),  # Limitar para proteção
            'buy_votes': buy_votes,
            'sell_votes': sell_votes,
            'hold_votes': hold_votes,
            'total_agents': total_votes,
            'high_conf_agents': high_conf_agents
        }
    
    def agente_trend_following(self, market_data):
        """Agente de tendência com análise multi-timeframe"""
        try:
            prices_m1 = market_data['historical_m1']['close']
            prices_m5 = market_data['historical_m5']['close']
            current_price = market_data['current_price']
            
            # Médias móveis curtas e longas em 2 timeframes
            short_ma1 = np.mean(prices_m1[-5:])
            long_ma1 = np.mean(prices_m1[-20:])
            short_ma5 = np.mean(prices_m5[-3:])
            long_ma5 = np.mean(prices_m5[-8:])
            
            # Verificar se as tendências estão alinhadas
            trend_m1 = 'BULL' if short_ma1 > long_ma1 else 'BEAR'
            trend_m5 = 'BULL' if short_ma5 > long_ma5 else 'BEAR'
            
            if trend_m1 == trend_m5 == 'BULL':
                return {'decision': 'BUY', 'confidence': 85.0, 'reason': 'Tendência alcista alinhada M1/M5'}
            elif trend_m1 == trend_m5 == 'BEAR':
                return {'decision': 'SELL', 'confidence': 85.0, 'reason': 'Tendência de queda alinhada M1/M5'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': 'Tendências desalinhadas'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente de tendência'}
    
    def agente_multi_timeframe(self, market_data):
        """Agente de múltiplos timeframes"""
        try:
            m1 = market_data['historical_m1']['close']
            m5 = market_data['historical_m5']['close']
            m15 = market_data['historical_m15']['close']
            
            # Tendências em 3 timeframes
            trend_m1 = 1 if m1[-1] > m1[-5] else -1
            trend_m5 = 1 if m5[-1] > m5[-3] else -1
            trend_m15 = 1 if m15[-1] > m15[-2] else -1
            
            alignment_score = trend_m1 + trend_m5 + trend_m15
            
            if alignment_score >= 2:  # Pelo menos 2 timeframes alinhados
                return {'decision': 'BUY' if alignment_score > 0 else 'SELL', 
                       'confidence': 80.0 if alignment_score == 3 else 75.0,
                       'reason': f'Alinhamento de {alignment_score}/3 timeframes'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'Timeframes não alinhados'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente multi-timeframe'}
    
    def agente_ema_crossover(self, market_data):
        """Agente EMA crossover"""
        try:
            prices = market_data['historical_m1']['close']
            ema_fast = pd.Series(prices).ewm(span=10).mean().values[-1]
            ema_slow = pd.Series(prices).ewm(span=20).mean().values[-1]
            ema_fast_prev = pd.Series(prices).ewm(span=10).mean().values[-2]
            ema_slow_prev = pd.Series(prices).ewm(span=20).mean().values[-2]
            
            # Detectar cross
            if ema_fast > ema_slow and ema_fast_prev <= ema_slow_prev:  # Golden cross
                return {'decision': 'BUY', 'confidence': 82.0, 'reason': 'Golden cross detectado'}
            elif ema_fast < ema_slow and ema_fast_prev >= ema_slow_prev:  # Death cross
                return {'decision': 'SELL', 'confidence': 82.0, 'reason': 'Death cross detectado'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': 'SEM crossover'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente EMA'}
    
    def agente_gamma_analyzer(self, market_data):
        """Agente Gamma - análise de volatilidade e força"""
        try:
            prices = market_data['historical_m1']['close']
            returns = np.diff(prices)
            gamma_value = np.std(returns) * 100  # Volatilidade como proxy para gamma
            
            if gamma_value > 0.2:  # Alta volatilidade
                # Verificar direção
                momentum = (prices[-1] - prices[-10]) / prices[-10]
                if momentum > 0:
                    return {'decision': 'SELL', 'confidence': 78.0, 'reason': 'Alta volatilidade - SELL'}
                else:
                    return {'decision': 'BUY', 'confidence': 78.0, 'reason': 'Alta volatilidade - BUY'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'Baixa volatilidade'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Gamma'}
    
    def agente_delta_analyzer(self, market_data):
        """Agente Delta - análise de momentum"""
        try:
            prices = market_data['historical_m1']['close']
            delta = (prices[-1] - prices[-5]) / prices[-5] * 100  # Momentum de 5 candles
            
            if abs(delta) > 0.3:  # Momentum significativo
                if delta > 0:
                    return {'decision': 'BUY', 'confidence': 75.0, 'reason': f'Momentum positivo: {delta:.2f}%'}
                else:
                    return {'decision': 'SELL', 'confidence': 75.0, 'reason': f'Momentum negativo: {delta:.2f}%'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': f'Momentum baixo: {delta:.2f}%'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Delta'}
    
    def agente_charm_analyzer(self, market_data):
        """Agente Charm - análise de aceleração de preço"""
        try:
            prices = market_data['historical_m1']['close']
            velocity = (prices[-1] - prices[-3]) / 3  # Velocidade
            acceleration = ((prices[-1] - prices[-2]) - (prices[-2] - prices[-3]))  # Aceleração
            
            if acceleration > 0 and velocity > 0:  # Acelerando para cima
                return {'decision': 'BUY', 'confidence': 80.0, 'reason': 'Aceleração positiva detectada'}
            elif acceleration < 0 and velocity < 0:  # Acelerando para baixo
                return {'decision': 'SELL', 'confidence': 80.0, 'reason': 'Aceleração negativa detectada'}
            else:
                return {'decision': 'HOLD', 'confidence': 45.0, 'reason': 'Sem aceleração clara'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Charm'}
    
    def agente_volume_spike(self, market_data):
        """Agente de spike de volume"""
        try:
            volumes = market_data['historical_m1']['tick_volume']
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]
            
            if current_volume > avg_volume * 3:  # Spike significativo
                # Verificar direção do preço
                prices = market_data['historical_m1']['close']
                direction = 'BUY' if prices[-1] > prices[-2] else 'SELL'
                return {'decision': direction, 'confidence': 88.0, 'reason': f'Spike de volume: {current_volume/avg_volume:.1f}x média'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'Sem spike de volume'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Volume'}
    
    def agente_momentum(self, market_data):
        """Agente de momentum avançado"""
        try:
            prices = market_data['historical_m1']['close']
            roc = ((prices[-1] - prices[-10]) / prices[-10]) * 100  # ROC de 10 períodos
            rsi_values = self.calculate_rsi(prices, 14)
            rsi = rsi_values[-1] if rsi_values else 50
            
            if roc > 0.5 and 30 < rsi < 70:  # Momentum positivo e sem sobrecompra
                return {'decision': 'BUY', 'confidence': 85.0, 'reason': f'Momentum forte: {roc:.2f}%'}
            elif roc < -0.5 and 30 < rsi < 70:  # Momentum negativo e sem sobrevenda
                return {'decision': 'SELL', 'confidence': 85.0, 'reason': f'Momentum negativo: {roc:.2f}%'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': 'Momentum neutro'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Momentum'}
    
    def agente_rsi_oversold(self, market_data):
        """Agente RSI avançado"""
        try:
            prices = market_data['historical_m1']['close']
            rsi_values = self.calculate_rsi(prices, 14)
            if not rsi_values:
                return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'RSI falhou'}
                
            rsi = rsi_values[-1]
            rsi_prev = rsi_values[-2] if len(rsi_values) > 1 else rsi
            
            if rsi < 30 and rsi > rsi_prev:  # Oversold + subindo
                return {'decision': 'BUY', 'confidence': 87.0, 'reason': f'RSI oversold + subindo: {rsi:.2f}'}
            elif rsi > 70 and rsi < rsi_prev:  # Overbought + descendo
                return {'decision': 'SELL', 'confidence': 87.0, 'reason': f'RSI overbought + descendo: {rsi:.2f}'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': f'RSI neutro: {rsi:.2f}'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente RSI'}
    
    def agente_support_resistance(self, market_data):
        """Agente de suporte e resistência avançado"""
        try:
            prices = market_data['historical_m1']['close']
            current_price = market_data['current_price']
            
            # Identificar níveis importantes
            recent_high = np.max(prices[-20:])
            recent_low = np.min(prices[-20:])
            pivot = (recent_high + recent_low + prices[-1]) / 3
            resistance = 2 * pivot - recent_low
            support = 2 * pivot - recent_high
            
            # Verificar proximidade
            if abs(current_price - support) < (recent_high - recent_low) * 0.01:  # Muito perto do suporte
                return {'decision': 'BUY', 'confidence': 84.0, 'reason': 'Próximo ao suporte significativo'}
            elif abs(current_price - resistance) < (recent_high - recent_low) * 0.01:  # Muito perto da resistência
                return {'decision': 'SELL', 'confidence': 84.0, 'reason': 'Próximo à resistência significativa'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': 'Longe de níveis-chave'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente S/R'}
    
    def agente_bollinger_breakout(self, market_data):
        """Agente Bollinger Bands avançado"""
        try:
            prices = market_data['historical_m1']['close']
            current_price = market_data['current_price']
            
            ma20 = np.mean(prices[-20:])
            std20 = np.std(prices[-20:])
            upper_band = ma20 + 2 * std20
            lower_band = ma20 - 2 * std20
            middle_band = ma20
            
            # Verificar posição relativa e movimento
            if current_price > upper_band and prices[-1] > prices[-2]:  # Acima + subindo
                return {'decision': 'BUY', 'confidence': 83.0, 'reason': 'Breakout + momentum alcista'}
            elif current_price < lower_band and prices[-1] < prices[-2]:  # Abaixo + descendo
                return {'decision': 'SELL', 'confidence': 83.0, 'reason': 'Breakdown + momentum de queda'}
            else:
                return {'decision': 'HOLD', 'confidence': 45.0, 'reason': 'Dentro das bandas'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Bollinger'}
    
    def agente_price_action(self, market_data):
        """Agente Price Action avançado"""
        try:
            opens = market_data['historical_m1']['open']
            highs = market_data['historical_m1']['high']
            lows = market_data['historical_m1']['low']
            closes = market_data['historical_m1']['close']
            
            # Verificar padrões de candle
            current_body = abs(closes[-1] - opens[-1])
            current_range = highs[-1] - lows[-1]
            body_ratio = current_body / current_range if current_range > 0 else 0
            
            if body_ratio > 0.7:  # Candle forte
                if closes[-1] > opens[-1]:  # Bullish strong
                    # Confirmar com preço anterior
                    if closes[-1] > closes[-2]:
                        return {'decision': 'BUY', 'confidence': 90.0, 'reason': 'Candle bullish forte + continuidade'}
                elif closes[-1] < opens[-1]:  # Bearish strong
                    if closes[-1] < closes[-2]:
                        return {'decision': 'SELL', 'confidence': 90.0, 'reason': 'Candle bearish forte + continuidade'}
            
            return {'decision': 'HOLD', 'confidence': 45.0, 'reason': 'Candle neutro'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Price Action'}
    
    def agente_prediction(self, market_data):
        """Agente de predição de força"""
        try:
            prices = market_data['historical_m1']['close']
            # Calcular tendência de curto prazo
            short_trend = (prices[-1] - prices[-3]) / prices[-3]
            medium_trend = (prices[-1] - prices[-8]) / prices[-8]
            momentum = (prices[-1] - prices[-15]) / prices[-15]
            
            # Prever direção com base em múltiplos fatores
            score = short_trend + medium_trend + momentum
            conf = min(95.0, abs(score) * 100 + 60)  # Converter para confiança
            
            if score > 0.002:  # Limiar para confiança
                return {'decision': 'BUY', 'confidence': conf, 'reason': 'Predição de alta confiável'}
            elif score < -0.002:
                return {'decision': 'SELL', 'confidence': conf, 'reason': 'Predição de baixa confiável'}
            else:
                return {'decision': 'HOLD', 'confidence': 35.0, 'reason': 'Predição neutra'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Predição'}
    
    def agente_consolidation_detector(self, market_data):
        """Agente de detecção de consolidação"""
        try:
            prices = market_data['historical_m1']['close']
            # Calcular volatilidade de curto prazo
            volatility = np.std(np.diff(prices[-15:]))
            avg_range = np.mean(np.abs(np.diff(prices[-15:])))
            
            if volatility < 0.05 and avg_range < 0.1:  # Baixa volatilidade = consolidação
                # Prever breakout baseado na última direção
                direction = 'BUY' if prices[-1] > np.mean(prices[-5:]) else 'SELL'
                return {'decision': direction, 'confidence': 75.0, 'reason': 'Consolidação final - breakout iminente'}
            else:
                return {'decision': 'HOLD', 'confidence': 40.0, 'reason': 'Sem consolidação clara'}
        except:
            return {'decision': 'HOLD', 'confidence': 30.0, 'reason': 'Erro no agente Consolidação'}
    
    def calculate_rsi(self, prices, period=14):
        """Calcula RSI"""
        try:
            deltas = np.diff(prices)
            gain = (deltas * (deltas > 0)).sum()
            loss = (-deltas * (deltas < 0)).sum()
            if loss == 0:
                return [100] * len(prices)
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return [rsi] * len(prices)
        except:
            return []
    
    def should_execute_trade(self, analysis):
        """Verifica se deve executar o trade com proteção de risco"""
        if not analysis or analysis.get('confidence', 0) < self.min_confidence:
            return False
            
        # Verificar limites diários
        if self.daily_pnl <= self.max_daily_loss:
            logger.warning(f'Limite diário de perdas atingido: ${self.daily_pnl:.2f}')
            return False
            
        if self.daily_operations >= self.max_operations_per_day:
            logger.warning(f'Limite diário de operações atingido: {self.daily_operations}/{self.max_operations_per_day}')
            return False
            
        # Verificar número de posições
        if self.position_count >= self.max_positions:
            logger.info(f'Limite de posições atingido: {self.position_count}/{self.max_positions}')
            return False
            
        # Verificar força dos sinais
        if analysis['buy_votes'] < 3 and analysis['sell_votes'] < 3:
            logger.info('Força dos sinais insuficiente')
            return False
        
        return True
    
    def execute_trade(self, decision, analysis):
        """Executa operação com proteção avançada"""
        try:
            # Calcular volume baseado na confiança
            base_volume = self.lot_size
            confidence_multiplier = min(2.0, analysis['confidence'] / 80.0)  # Até 2x volume para alta confiança
            volume = base_volume * confidence_multiplier
            
            # Obter preço atual
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return False
                
            if decision == 'BUY':
                price = tick.ask
                order_type = mt5.ORDER_TYPE_BUY
            elif decision == 'SELL':
                price = tick.bid
                order_type = mt5.ORDER_TYPE_SELL
            else:
                return False
            
            # Calcular stops dinamicamente
            point = mt5.symbol_info(self.symbol).point
            sl_points = int((price * self.stop_loss_pct) / point)
            tp_points = int((price * self.take_profit_pct) / point)
            
            # Criar pedido
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': self.symbol,
                'volume': volume,
                'type': order_type,
                'price': price,
                'sl': price - sl_points * point if decision == 'BUY' else price + sl_points * point,
                'tp': price + tp_points * point if decision == 'BUY' else price - tp_points * point,
                'deviation': 20,
                'magic': self.magic_number,
                'comment': f'SistemaOtimizado-{decision}',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_FOK,
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                self.daily_operations += 1
                self.position_count += 1
                logger.info(f'SUCESSO - OPERACAO EXECUTADA: {decision} {volume:.2f} {self.symbol} @ {price:.2f}, SL: {request["sl"]:.2f}, TP: {request["tp"]:.2f}')
                return True
            else:
                logger.error(f'Falha na operacao: {result}')
                return False
                
        except Exception as e:
            logger.error(f'Erro ao executar operacao: {e}')
            return False
    
    def monitor_positions(self):
        """Monitora posições em tempo real para proteção"""
        try:
            positions = mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
            if positions:
                for pos in positions:
                    # Calcular P&L atual
                    profit = pos.profit
                    
                    # Proteção anti-perda
                    if profit <= -0.15:  # Stop loss de $0.15
                        self.close_position(pos)
                        logger.warning(f'Stop Loss ativado na posicao {pos.ticket}: ${profit:.2f}')
                        
        except Exception as e:
            logger.error(f'Erro no monitoramento de posicoes: {e}')
    
    def close_position(self, position):
        """Fecha posição"""
        try:
            order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(self.symbol).ask
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': self.symbol,
                'volume': position.volume,
                'type': order_type,
                'position': position.ticket,
                'price': price,
                'deviation': 20,
                'magic': self.magic_number,
                'comment': 'StopLoss',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                self.position_count -= 1
                logger.info(f'Posicao {position.ticket} fechada, P&L: ${position.profit:.2f}')
                return True
            return False
        except Exception as e:
            logger.error(f'Erro ao fechar posicao: {e}')
            return False
    
    def run(self):
        """Loop principal do sistema"""
        if not self.is_connected:
            logger.error('Sistema nao pode rodar - MT5 nao conectado')
            return
            
        logger.info(f'[{self.name}] SISTEMA OTIMIZADO COM 14 AGENTES INICIADO!')
        logger.info(f'Configuracoes: MinConf={self.min_confidence}%, MaxPos={self.max_positions}, SL={self.stop_loss_pct}%, TP={self.take_profit_pct}%')
        
        while True:
            try:
                if not self.is_connected:
                    self.connect_mt5()
                    if not self.is_connected:
                        time.sleep(10)
                        continue
                
                if self.is_trading_hours():
                    # Obter dados de mercado
                    market_data = self.get_market_data()
                    if market_data:
                        # Análise com 14 agentes
                        analysis = self.analyze_with_14_agentes(market_data)
                        
                        if analysis:
                            logger.info(f'ANALISE DOS 14 AGENTES: {analysis["decision"]} | Conf: {analysis["confidence"]:.1f}% | Votos(B/S/H): {analysis["buy_votes"]}/{analysis["sell_votes"]}/{analysis["hold_votes"]}')
                            
                            # Verificar se deve executar trade
                            if self.should_execute_trade(analysis):
                                success = self.execute_trade(analysis['decision'], analysis)
                                if success:
                                    logger.info(f'OPERACAO EXECUTADA COM SUCESSO: {analysis["decision"]} - Confianca {analysis["confidence"]:.1f}%')
                                else:
                                    logger.error('Falha ao executar operacao')
                        
                        # Monitorar posições abertas
                        self.monitor_positions()
                
                # Verificar reset diário
                current_date = datetime.now().date()
                if current_date != self.last_reset_date:
                    self.daily_operations = 0
                    self.daily_pnl = 0.0
                    self.last_reset_date = current_date
                    logger.info('Contadores diarios resetados')
                
                time.sleep(5)  # Verificar a cada 5 segundos (otimizado)
                
            except KeyboardInterrupt:
                logger.info('Interrupcao detectada - encerrando sistema')
                break
            except Exception as e:
                logger.error(f'Erro no loop principal: {e}')
                time.sleep(5)
        
        logger.info('Sistema otimizado encerrado')
    
    def stop(self):
        """Para o sistema"""
        pass  # O loop principal já lida com interrupções

if __name__ == '__main__':
    # Configuração do sistema otimizado
    config = {
        'name': 'SistemaOtimizado14Agentes',
        'symbol': 'US100',
        'magic_number': 234001,
        'lot_size': 0.01
    }
    
    logger.info('INICIANDO SISTEMA OTIMIZADO COM 14 AGENTES PARA MAXIMIZACAO DE LUCROS')
    logger.info('Configuracoes avancadas de protecao e otimizacao carregadas')
    
    sistema = SistemaOtimizado14Agentes(config)
    sistema.start()
    
    try:
        while sistema.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Interrupcao do usuario detectada')
        sistema.stop()
        sistema.join()
        
    logger.info('Sistema otimizado finalizado com sucesso')