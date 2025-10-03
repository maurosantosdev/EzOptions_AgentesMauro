#!/usr/bin/env python3
"""
SISTEMA MULTI-ATIVOS COM CARACTERÍSTICAS DE TRADER SÊNIOR
Opera com US100, US500, US30 e DE30 simultaneamente
Com análise avançada de greeks e filtros institucionais
"""

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
    handlers=[logging.FileHandler('sistema_multi_ativos.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class SistemaMultiAtivosSenior(threading.Thread):
    """
    Sistema avançado com características de trader com 10+ anos de experiência
    Opera múltiplos ativos com estratégias específicas para cada
    """

    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.name = config.get('name', 'SistemaMultiAtivosSenior')

        # Carteira de ativos configurada
        self.ativos_config = {
            'US100': {  # NASDAQ 100 - Tecnologia
                'peso': 0.4,
                'simbolo': 'US100',
                'setups_ideais': ['bullish_breakout', 'bearish_breakout', 'gamma_protection'],
                'magic_base': 234001,
                'lot_size': 0.015,
                'timezone': 'America/New_York'
            },
            'DE30': {   # DAX Alemão - Europa
                'peso': 0.3,
                'simbolo': 'DE30',
                'setups_ideais': ['pullback_top', 'pullback_bottom'],
                'magic_base': 234002,
                'lot_size': 0.01,
                'timezone': 'Europe/Berlin'
            },
            'US500': {  # S&P 500 - Blue Chips
                'peso': 0.2,
                'simbolo': 'US500',
                'setups_ideais': ['consolidated_market'],
                'magic_base': 234003,
                'lot_size': 0.01,
                'timezone': 'America/New_York'
            },
            'US30': {   # Dow Jones - Industrial
                'peso': 0.1,
                'simbolo': 'US30',
                'setups_ideais': ['gamma_protection'],
                'magic_base': 234004,
                'lot_size': 0.01,
                'timezone': 'America/New_York'
            }
        }

        # Configurações gerais de trader sênior
        self.min_confidence = 55.0          # Confiança coletiva
        self.max_positions_total = 3        # Máximo de posições totais
        self.stop_loss_pct = 0.10           # Stop loss apertado
        self.take_profit_pct = 0.25         # Take profit lucrativo
        self.min_volatility = 0.02          # Volatilidade mínima

        # Estado do sistema
        self.is_connected = False
        self.running = False
        self.positions_by_symbol = {}       # Controle de posições por ativo
        self.performance_by_symbol = {}     # Performance por ativo

        # Características de trader experiente
        self.institutional_windows = {
            'london_open': (8, 0, 8, 30),
            'ny_open': (13, 30, 14, 0),
            'fed_time': (14, 0, 14, 5),
            'ny_close': (16, 55, 17, 0)
        }

        # Filtros sazonais
        self.day_multipliers = {
            0: 1.2,  # Segunda: +20%
            1: 1.0,  # Terça: normal
            2: 1.1,  # Quarta: +10%
            3: 1.1,  # Quinta: +10%
            4: 0.8   # Sexta: -20%
        }

        self.connect_mt5()

        # Logs iniciais de trader sênior
        logger.info('=== SISTEMA MULTI-ATIVOS - TRADER SENIOR ===')
        logger.info('Carteira configurada:')
        for simbolo, config in self.ativos_config.items():
            logger.info(f'  {simbolo}: {config["peso"]*100}% | Setups: {len(config["setups_ideais"])} | Lote: {config["lot_size"]}')
        logger.info(f'Confiança mínima: {self.min_confidence}% | Volatilidade: {self.min_volatility*100}%')
        logger.info('=== SISTEMA OPERACIONAL - CARTEIRA INSTITUCIONAL ===')

    def connect_mt5(self):
        """Conecta ao MT5"""
        login = int(os.getenv('MT5_LOGIN', '103486755'))
        server = os.getenv('MT5_SERVER', 'FBS-Demo')
        password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

        if mt5.initialize(login=login, server=server, password=password):
            self.is_connected = True
            logger.info('Conectado ao MT5 com sucesso')

            # Selecionar todos os símbolos
            for config in self.ativos_config.values():
                mt5.symbol_select(config['simbolo'], True)
        else:
            logger.error('Falha ao conectar ao MT5')

    def is_trading_hours(self):
        """Verifica se está em horário de operação para qualquer ativo"""
        now = datetime.now(pytz.timezone('America/New_York'))
        if not (0 <= now.weekday() <= 4):  # Dias úteis
            return False

        t = now.time()
        # Operação estendida: 8:00 às 17:00
        return datetime_time(8, 0) <= t < datetime_time(17, 0)

    def check_institutional_context(self):
        """Verifica contexto institucional (trader experiente)"""
        ny_tz = pytz.timezone('America/New_York')
        current_hour = datetime.now(ny_tz).hour
        current_minute = datetime.now(ny_tz).minute

        for window_name, (start_hour, start_min, end_hour, end_min) in self.institutional_windows.items():
            if start_hour <= current_hour <= end_hour:
                if start_hour == end_hour:
                    if start_min <= current_minute <= end_min:
                        return {'active': True, 'window': window_name, 'importance': 'HIGH'}
                else:
                    return {'active': True, 'window': window_name, 'importance': 'HIGH'}

        return {'active': False, 'window': None, 'importance': 'NORMAL'}

    def get_market_data_multi_asset(self, simbolo):
        """Obtém dados de mercado para um ativo específico"""
        if not self.is_connected:
            return None

        try:
            # Dados M1 para análise principal
            rates_m1 = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 0, 100)
            if rates_m1 is None or len(rates_m1) < 40:
                return None

            tick = mt5.symbol_info_tick(simbolo)

            return {
                'simbolo': simbolo,
                'current_price': tick.ask,
                'bid': tick.bid,
                'ask': tick.ask,
                'rates_m1': rates_m1,
                'volume': tick.volume,
                'time': tick.time
            }
        except Exception as e:
            logger.error(f'Erro ao obter dados de {simbolo}: {e}')
            return None

    def calculate_greeks_senior(self, market_data):
        """Calcula greeks com lógica de trader experiente"""
        try:
            simbolo = market_data['simbolo']
            prices = market_data['rates_m1']['close']
            current_price = market_data['current_price']

            if len(prices) < 20:
                return {'gamma': 0, 'delta': 0, 'charm': 0}

            # GAMMA - Volatilidade (trader experiente)
            returns = np.diff(prices[-20:]) / prices[-20:-1] * 100
            gamma = np.std(returns) * 15  # Multiplicador ajustado
            gamma = max(0, min(100, gamma))

            # DELTA - Tendência direcional
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-20:])
            delta_raw = ((current_price - short_ma) / short_ma) * 1000
            delta = max(-100, min(100, delta_raw))

            # CHARM - Decaimento temporal (trader experiente)
            current_hour = datetime.now().hour
            # Ajuste baseado no ativo
            if simbolo in ['US100', 'US500', 'US30']:
                base_hour = 8  # Abertura NY
            else:  # DE30
                base_hour = 9  # Abertura Europa

            charm = max(0, min(100, 100 - (current_hour - base_hour) * 8))

            return {
                'gamma': gamma,
                'delta': delta,
                'charm': charm
            }
        except:
            return {'gamma': 0, 'delta': 0, 'charm': 0}

    def analyze_asset_with_greeks(self, market_data):
        """Analisa um ativo específico com greeks"""
        simbolo = market_data['simbolo']
        config = self.ativos_config[simbolo]

        # Verificar volatilidade mínima
        prices = market_data['rates_m1']['close']
        volatilidade = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100

        if volatilidade < self.min_volatility * 100:
            return {'decision': 'HOLD', 'confidence': 0, 'simbolo': simbolo}

        # Calcular greeks
        greeks = self.calculate_greeks_senior(market_data)

        # Análise baseada nos setups ideais para este ativo
        analysis = self.analyze_specific_setups(market_data, greeks, config['setups_ideais'])

        # Aplicar filtros de trader sênior
        analysis = self.apply_senior_filters(analysis, market_data, greeks)

        return {
            'simbolo': simbolo,
            'decision': analysis.get('decision', 'HOLD'),
            'confidence': analysis.get('confidence', 0),
            'greeks': greeks,
            'volatilidade': volatilidade
        }

    def analyze_specific_setups(self, market_data, greeks, setups_ideais):
        """Analisa setups específicos para cada ativo"""
        prices = market_data['rates_m1']['close']
        current_price = market_data['current_price']

        # Setups básicos (simplificado)
        if 'bullish_breakout' in setups_ideais:
            if greeks['gamma'] > 70 and greeks['delta'] > 20:
                return {'decision': 'BUY', 'confidence': min(70 + greeks['gamma']/10, 90)}

        if 'bearish_breakout' in setups_ideais:
            if greeks['gamma'] > 70 and greeks['delta'] < -20:
                return {'decision': 'SELL', 'confidence': min(70 + greeks['gamma']/10, 90)}

        if 'pullback_top' in setups_ideais:
            if greeks['delta'] > 30 and current_price < np.mean(prices[-10:]):
                return {'decision': 'BUY', 'confidence': 65}

        if 'consolidated_market' in setups_ideais:
            if greeks['gamma'] < 30 and abs(greeks['delta']) < 20:
                return {'decision': 'BUY' if greeks['delta'] > 0 else 'SELL', 'confidence': 60}

        return {'decision': 'HOLD', 'confidence': 30}

    def apply_senior_filters(self, analysis, market_data, greeks):
        """Aplica filtros de trader experiente"""
        simbolo = market_data['simbolo']

        # Filtro institucional
        institutional = self.check_institutional_context()
        if institutional['active']:
            analysis['confidence'] *= 1.15  # +15% em janelas institucionais

        # Filtro sazonal
        day_multiplier = self.day_multipliers.get(datetime.now().weekday(), 1.0)
        analysis['confidence'] *= day_multiplier

        # Filtro de greeks específicos por ativo
        if simbolo == 'US100' and greeks['gamma'] < 20:
            analysis['confidence'] *= 0.7  # US100 precisa de gamma alto

        if simbolo == 'DE30' and abs(greeks['delta']) < 15:
            analysis['confidence'] *= 0.8  # DE30 precisa de tendência clara

        return analysis

    def execute_trade_for_asset(self, analysis):
        """Executa operação para um ativo específico"""
        simbolo = analysis['simbolo']
        config = self.ativos_config[simbolo]

        if analysis['confidence'] < self.min_confidence:
            return False

        # Verificar limite de posições totais
        total_positions = sum(len(positions) for positions in self.positions_by_symbol.values())
        if total_positions >= self.max_positions_total:
            logger.info(f'Limite de posições atingido: {total_positions}/{self.max_positions_total}')
            return False

        # Verificar posições existentes para este símbolo
        current_positions = self.positions_by_symbol.get(simbolo, [])
        if len(current_positions) >= 1:  # Máximo 1 posição por símbolo
            return False

        try:
            lot = config['lot_size']
            price = mt5.symbol_info_tick(simbolo).ask if analysis['decision'] == 'BUY' else mt5.symbol_info_tick(simbolo).bid

            sl = price * (1 - self.stop_loss_pct) if analysis['decision'] == 'BUY' else price * (1 + self.stop_loss_pct)
            tp = price * (1 + self.take_profit_pct) if analysis['decision'] == 'BUY' else price * (1 - self.take_profit_pct)

            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': simbolo,
                'volume': lot,
                'type': mt5.ORDER_TYPE_BUY if analysis['decision'] == 'BUY' else mt5.ORDER_TYPE_SELL,
                'price': price,
                'sl': sl,
                'tp': tp,
                'magic': config['magic_base'],
                'comment': f'Senior-{simbolo}-{analysis["decision"]}',
                'type_time': mt5.ORDER_TIME_GTC,
            }

            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                # Registrar posição
                if simbolo not in self.positions_by_symbol:
                    self.positions_by_symbol[simbolo] = []

                self.positions_by_symbol[simbolo].append({
                    'ticket': result.order,
                    'direction': analysis['decision'],
                    'entry_price': price,
                    'sl': sl,
                    'tp': tp,
                    'lot': lot
                })

                logger.info(f'OPERACAO EXECUTADA: {analysis["decision"]} {lot} {simbolo} @ {price:.2f} | Conf: {analysis["confidence"]:.1f}%')
                return True

        except Exception as e:
            logger.error(f'Erro ao executar {simbolo}: {e}')

        return False

    def manage_positions_senior(self):
        """Gerencia posições com lógica de trader experiente"""
        for simbolo, positions in self.positions_by_symbol.items():
            for i, pos in enumerate(positions[:]):  # Copy for safe removal
                try:
                    mt5_positions = mt5.positions_get(ticket=pos['ticket'])
                    if not mt5_positions:
                        # Posição fechada
                        logger.info(f'Posicao fechada: {simbolo} {pos["direction"]} Ticket {pos["ticket"]}')
                        positions.remove(pos)
                        continue

                    mt5_pos = mt5_positions[0]
                    current_price = mt5_pos.price_current

                    # Verificar stop loss/take profit
                    if pos['direction'] == 'BUY':
                        if current_price <= pos['sl'] or current_price >= pos['tp']:
                            self.close_position(pos['ticket'], simbolo)
                    else:  # SELL
                        if current_price >= pos['sl'] or current_price <= pos['tp']:
                            self.close_position(pos['ticket'], simbolo)

                except Exception as e:
                    logger.error(f'Erro ao gerenciar {simbolo}: {e}')

    def close_position(self, ticket, simbolo):
        """Fecha posição específica"""
        try:
            result = mt5.Close(ticket)
            if result:
                logger.info(f'Posicao fechada: {simbolo} Ticket {ticket}')
                return True
        except Exception as e:
            logger.error(f'Erro ao fechar posicao {ticket}: {e}')
        return False

    def run(self):
        """Loop principal do sistema multi-ativos"""
        if not self.is_connected:
            return

        self.running = True
        logger.info('Sistema Multi-Ativos Senior iniciado - Carteira Institucional')

        while self.running:
            try:
                if self.is_trading_hours():
                    # Analisar cada ativo
                    analyses = []

                    for config in self.ativos_config.values():
                        simbolo = config['simbolo']
                        market_data = self.get_market_data_multi_asset(simbolo)

                        if market_data:
                            analysis = self.analyze_asset_with_greeks(market_data)
                            analyses.append(analysis)

                            greeks = analysis.get("greeks", {})
                            logger.info(f'{simbolo}: {analysis["decision"]} (Conf: {analysis["confidence"]:.1f}%) | Greeks: G{greeks.get("gamma", 0):.1f} D{greeks.get("delta", 0):.1f} C{greeks.get("charm", 0):.1f}')

                    # Executar operações para ativos com sinais fortes
                    for analysis in analyses:
                        if analysis['confidence'] >= self.min_confidence:
                            self.execute_trade_for_asset(analysis)

                # Gerenciar posições abertas
                self.manage_positions_senior()

                time.sleep(10)  # Verificar a cada 10 segundos

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f'Erro no loop principal: {e}')
                time.sleep(5)

        mt5.shutdown()

    def stop(self):
        self.running = False

if __name__ == '__main__':
    config = {'name': 'SistemaMultiAtivosSenior'}
    sistema = SistemaMultiAtivosSenior(config)
    sistema.start()

    try:
        while sistema.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        sistema.stop()
        sistema.join()
        print("Sistema Multi-Ativos encerrado!")