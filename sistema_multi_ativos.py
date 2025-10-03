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

        # Sistema de 14 agentes distribuídos por ativo (trabalhando simultaneamente)
        self.agents_per_asset = 4  # 4 agentes por ativo = 16 agentes (usaremos 14)
        self.total_agents = 14  # Total de agentes trabalhando simultaneamente

        # Configurações
        self.min_confidence = 55.0
        self.max_positions = 10
        self.stop_loss_pct = 0.10
        self.take_profit_pct = 0.25

        # Estado
        self.is_connected = False
        self.running = False
        self.positions_count = 0

        # Controle de lucro/prejuízo diário (trader experiente)
        self.daily_pnl_target = 150.0       # Meta de lucro diário ($150) - fecha posições
        self.profit_protection_level = 80.0 # Nível de proteção de lucro ($80 positivo)
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
        logger.info(f'🛡️ Proteção de Lucro: ${self.profit_protection_level:.2f} (ativa quando lucro > $50)')
        logger.info(f'📊 Confianca mínima: {self.min_confidence}% | Max posições: {self.max_positions}')
        logger.info(f'🤖 Total de agentes: {self.total_agents} (trabalhando simultaneamente)')
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

            # Volatilidade
            vol = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100

            if vol <= 0.02:  # Volatilidade mínima
                return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': 14}}

            # Sistema de 14 agentes trabalhando simultaneamente
            agent_decisions = []
            agent_confidences = []

            # Distribuir agentes entre os ativos (US100: 4, US500: 3, US30: 3, DE30: 4)
            agents_for_this_asset = 4 if simbolo in ['US100', 'DE30'] else 3

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
                    if vol > 0.08:
                        direction = 'BUY' if current_price > prices[-1] else 'SELL'
                        agent_decisions.append(direction)
                        agent_confidences.append(min(60 + vol * 2, 85))
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

            # Completar com agentes adicionais se necessário (para manter 14 agentes totais)
            while len(agent_decisions) < self.total_agents:
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

                else:  # Volume/Price
                    avg_volume = np.mean(rates['tick_volume'][-10:])
                    current_volume = rates['tick_volume'][-1]
                    if current_volume > avg_volume * 1.5 and current_price > prices[-1]:
                        agent_decisions.append('BUY')
                        agent_confidences.append(70)
                    elif current_volume > avg_volume * 1.5 and current_price < prices[-1]:
                        agent_decisions.append('SELL')
                        agent_confidences.append(70)
                    else:
                        agent_decisions.append('HOLD')
                        agent_confidences.append(35)

            # Contar votos
            buy_votes = agent_decisions.count('BUY')
            sell_votes = agent_decisions.count('SELL')
            hold_votes = agent_decisions.count('HOLD')

            # Calcular confiança coletiva baseada nos votos e confiança individual
            total_confidence = sum(agent_confidences)
            avg_confidence = total_confidence / len(agent_confidences)

            # Decisão coletiva com threshold mais alto
            if buy_votes > sell_votes and buy_votes >= max(2, len(agent_decisions) // 3):
                confidence = min(avg_confidence + (buy_votes * 5), 95)
                return {'decision': 'BUY', 'confidence': confidence, 'agent_votes': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}}
            elif sell_votes > buy_votes and sell_votes >= max(2, len(agent_decisions) // 3):
                confidence = min(avg_confidence + (sell_votes * 5), 95)
                return {'decision': 'SELL', 'confidence': confidence, 'agent_votes': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}}

            return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}}

        except Exception as e:
            logger.error(f'Erro na análise de {simbolo}: {e}')
            return {'decision': 'HOLD', 'confidence': 0, 'agent_votes': {'BUY': 0, 'SELL': 0, 'HOLD': 14}}

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
        elif self.peak_pnl_today > self.profit_protection_level:
            # Ativar proteção quando lucro ultrapassar $50
            if not self.trailing_stop_active:
                self.trailing_stop_active = True
                self.trailing_stop_level = self.profit_protection_level
                logger.info(f'🛡️ PROTEÇÃO DE LUCRO ATIVADA: Lucro atual ${self.daily_pnl:.2f} > ${self.profit_protection_level:.2f}')
                logger.info(f'📈 Sistema protegerá lucro mínimo de ${self.profit_protection_level:.2f}')

            # Se o lucro caiu abaixo do nível de proteção, fechar posições
            if self.daily_pnl <= self.trailing_stop_level:
                logger.info(f'🛑 PROTEÇÃO DE LUCRO EXECUTADA: ${self.daily_pnl:.2f} <= ${self.trailing_stop_level:.2f}')
                logger.info(f'💰 Protegendo lucro - Pico do dia foi: ${self.peak_pnl_today:.2f}')
                self.close_all_positions("PROTECAO_LUCRO")
                self.limit_hit_today = True
                logger.info('✅ Sistema continua operando normalmente (pode abrir novas posições)')

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
        self.daily_pnl += pnl_change
        logger.info(f'💰 P&L Diário Atualizado: ${self.daily_pnl:.2f}')

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

        while self.running:
            try:
                # Verificar limites de lucro/prejuízo ANTES de operar
                self.check_daily_limits()

                # Sistema continua operando normalmente mesmo após atingir limites
                if self.is_trading_hours():
                    for simbolo in self.ativos:
                        # Usar análise com 14 agentes simultâneos
                        analysis = self.analyze_asset_with_agents(simbolo)
                        logger.info(f'{simbolo}: {analysis["decision"]} (Conf: {analysis["confidence"]:.1f}%) | Agentes: BUY={analysis["agent_votes"]["BUY"]} SELL={analysis["agent_votes"]["SELL"]} | P&L Diario: ${self.daily_pnl:.2f}')

                        if analysis['confidence'] >= self.min_confidence:
                            self.execute_trade(simbolo, analysis['decision'], analysis['confidence'])

                    # Gerenciar trailing stops para proteger lucros positivos
                    self.manage_trailing_stops()

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