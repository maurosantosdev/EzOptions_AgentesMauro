import MetaTrader5 as mt5
import time
import os
import signal
import sys
from dotenv import load_dotenv
import threading
from datetime import datetime, time as datetime_time
import pytz
import logging
from trading_setups import TradingSetupAnalyzer, SetupType
from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis, TradingDecision
from smart_order_system import SmartOrderSystem, TrendDirection

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class RealAgentSystem(threading.Thread):
    def __init__(self, config):
        super().__init__()
        load_dotenv()

        # Configurações
        self.name = config.get('name', 'RealAgent')
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 234001)
        self.lot_size = config.get('lot_size', 0.01)

        # Estado
        self.is_connected = False
        self.account_info = None
        self.active_positions = []
        self.total_pnl = 0
        self.running = False

        # Sistema de análise
        self.setup_analyzer = TradingSetupAnalyzer()
        self.current_setups = {}

        # Sistema multi-agente inteligente
        self.multi_agent_system = MultiAgentTradingSystem()

        # Sistema de ordens inteligentes (BUY+BUY_LIMIT e SELL+SELL_LIMIT)
        self.smart_order_system = SmartOrderSystem(
            symbol=self.symbol,
            magic_number=self.magic_number,
            lot_size=self.lot_size
        )

        # Histórico de trades para otimização
        self.trade_history = []
        self.current_pnl = 0.0

        # Configurações ANTI-PREJUIZO (otimizadas para PARAR PERDAS)
        self.min_confidence_to_trade = 30.0  # MUITO BAIXO para executar SELL rapidamente
        self.max_positions = 10  # Aumentado para mais SELLs simultâneos
        self.risk_per_trade = 0.008  # 0.8% menor risco por trade (stop mais próximo)
        self.profit_multiplier = 1.8  # Target menor mas mais atingível

        # Conectar ao MT5
        self.connect_mt5()

    def connect_mt5(self):
        """Conecta ao MetaTrader5"""
        try:
            login = int(os.getenv("MT5_LOGIN"))
            server = os.getenv("MT5_SERVER")
            password = os.getenv("MT5_PASSWORD")

            logger.info(f"[{self.name}] Tentando conectar ao MT5...")
            logger.info(f"[{self.name}] Server: {server}, Login: {login}")

            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"[{self.name}] MT5 initialize() failed: {error}")
                return False

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

    def update_account_state(self):
        """Atualiza informações da conta"""
        if not self.is_connected:
            return

        try:
            self.account_info = mt5.account_info()
            positions = mt5.positions_get(magic=self.magic_number)

            self.active_positions = list(positions) if positions else []
            self.total_pnl = sum(p.profit for p in self.active_positions)

            # Atualizar resumo de ordens inteligentes
            smart_orders = self.smart_order_system.get_current_orders_summary()

            logger.debug(f"[{self.name}] Conta atualizada - Saldo: {self.account_info.balance}, "
                        f"Posições: {len(self.active_positions)}, P&L: {self.total_pnl}")
            logger.debug(f"[{self.name}] Ordens SmartOrder - BUY: {smart_orders['buy_orders']}, SELL: {smart_orders['sell_orders']}, Total: {smart_orders['total']}")

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao atualizar conta: {e}")

    def is_trading_hours(self):
        """Verifica se está em horário de trading - US100 opera 24h"""
        # US100 (NASDAQ-100) opera 24h durante dias úteis
        # Só bloquear nos fins de semana
        current_time = datetime.now()
        weekday = current_time.weekday()

        # Segunda a sexta opera 24h (0=Monday, 4=Friday)
        if 0 <= weekday <= 4:
            return True

        # Sábado e domingo: não opera
        return False

    def analyze_market(self):
        """Analisa o mercado usando sistema multi-agente inteligente"""
        try:
            # Obter preço atual
            current_price = self.get_current_symbol_price()
            if not current_price:
                return {}

            # Criar dados para análise multi-agente
            mock_calls = self.create_mock_options_data(current_price, option_type='call')
            mock_puts = self.create_mock_options_data(current_price, option_type='put')
            vwap_data = self.simulate_vwap_data(current_price)

            # Obter dados REAIS primeiro para ajustar mock
            price_data = self.get_recent_price_data(current_price)
            volume_data = self.get_real_volume_data()

            # Detectar tendência real
            is_falling = False
            if price_data and 'recent' in price_data and len(price_data['recent']) >= 2:
                is_falling = price_data['recent'][-1] < price_data['recent'][0]

            # Preparar dados de mercado AJUSTADOS pela tendência real
            charm_data = self.extract_charm_data(mock_calls, mock_puts, trend_falling=is_falling)
            delta_data = self.extract_delta_data(mock_calls, mock_puts, trend_falling=is_falling)
            gamma_data = self.extract_gamma_data(mock_calls, mock_puts, trend_falling=is_falling)

            market_data = MarketAnalysis(
                charm_data=charm_data,
                delta_data=delta_data,
                gamma_data=gamma_data,
                vwap_data=vwap_data,
                volume_data=volume_data,
                price_data=price_data,
                current_price=current_price,
                timestamp=datetime.now()
            )

            # Análise colaborativa dos 10 agentes
            recommendation = self.multi_agent_system.analyze_market_collaborative(market_data)

            # Executar trade baseado na recomendação dos agentes
            if recommendation.confidence >= self.min_confidence_to_trade:
                self.execute_agent_recommendation(recommendation)

            # Também manter análise de setups tradicional para compatibilidade
            setups_results = self.setup_analyzer.analyze_all_setups(
                mock_calls, mock_puts, current_price, vwap_data)

            self.current_setups = setups_results

            logger.info(f"[{self.name}] Análise multi-agente concluída - Decisão: {recommendation.decision.value} (Conf: {recommendation.confidence:.1f}%)")

            return setups_results

        except Exception as e:
            logger.error(f"[{self.name}] Erro na análise multi-agente: {e}")
            return {}

    def get_current_symbol_price(self):
        """Obtém preço atual do símbolo"""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
                return (tick.bid + tick.ask) / 2
            return None
        except Exception as e:
            logger.error(f"[{self.name}] Erro ao obter preço: {e}")
            return None

    def create_mock_options_data(self, current_price, option_type='call'):
        """Cria dados simulados de opções para análise"""
        import pandas as pd
        import numpy as np

        # Garantir que current_price é float
        current_price = float(current_price)

        # Criar strikes de forma mais robusta
        strike_step = current_price * 0.005
        strikes = np.arange(current_price * 0.95, current_price * 1.05, strike_step)

        # Garantir que temos pelo menos alguns strikes
        if len(strikes) < 5:
            strikes = np.linspace(current_price * 0.95, current_price * 1.05, 10)

        data = []
        for strike in strikes:
            try:
                strike = float(strike)
                # Simular greeks baseados na proximidade do strike
                moneyness = strike / current_price

                if option_type == 'call':
                    delta = max(0.0, min(1.0, (moneyness - 0.95) * 5))
                    gamma = np.exp(-abs(moneyness - 1) * 10) * 100
                    charm = np.random.uniform(-50, 50)
                else:  # put
                    delta = max(-1.0, min(0.0, (0.95 - moneyness) * 5))
                    gamma = np.exp(-abs(moneyness - 1) * 10) * 100
                    charm = np.random.uniform(-50, 50)

                # GEX (Gamma Exposure) simulado
                gex = float(gamma * np.random.uniform(100, 1000))

                data.append({
                    'strike': float(strike),
                    'DELTA': float(delta),
                    'GAMMA': float(gamma),
                    'CHARM': float(charm),
                    'GEX': float(gex),
                    'THETA': float(np.random.uniform(-10, -1))
                })
            except Exception as e:
                logger.error(f"Erro ao criar dados para strike {strike}: {e}")
                continue

        if len(data) == 0:
            # Fallback: criar dados mínimos
            data.append({
                'strike': float(current_price),
                'DELTA': 0.5 if option_type == 'call' else -0.5,
                'GAMMA': 100.0,
                'CHARM': 0.0,
                'GEX': 1000.0,
                'THETA': -5.0
            })

        return pd.DataFrame(data)

    def simulate_vwap_data(self, current_price):
        """Simula dados VWAP"""
        return {
            'vwap': current_price * 0.999,
            'std1_upper': current_price * 1.005,
            'std1_lower': current_price * 0.995,
            'std2_upper': current_price * 1.01,
            'std2_lower': current_price * 0.99
        }

    def extract_charm_data(self, calls_df, puts_df, trend_falling=False):
        """Extrai dados CHARM - AJUSTADO pela tendência real"""
        try:
            charm_values = []
            if not calls_df.empty and 'CHARM' in calls_df.columns:
                charm_values.extend(calls_df['CHARM'].tolist())
            if not puts_df.empty and 'CHARM' in puts_df.columns:
                charm_values.extend(puts_df['CHARM'].tolist())

            # AJUSTAR CHARM baseado na tendência real
            if trend_falling:
                # Mercado caindo = CHARM negativo (indica venda)
                charm_values = [-abs(val) for val in charm_values] if charm_values else [-0.5, -0.3, -0.1]
                logger.info(f"[{self.name}] QUEDA - CHARM AJUSTADO: {charm_values[-3:]}")
            else:
                # Mercado subindo = CHARM positivo
                charm_values = [abs(val) for val in charm_values] if charm_values else [0.1, 0.3, 0.5]

            return {'values': charm_values[-10:] if charm_values else [0]}
        except:
            return {'values': [0]}

    def extract_delta_data(self, calls_df, puts_df, trend_falling=False):
        """Extrai dados DELTA - AJUSTADO pela tendência real"""
        try:
            delta_values = []
            if not calls_df.empty and 'DELTA' in calls_df.columns:
                delta_values.extend(calls_df['DELTA'].tolist())
            if not puts_df.empty and 'DELTA' in puts_df.columns:
                delta_values.extend(puts_df['DELTA'].tolist())

            # AJUSTAR DELTA baseado na tendência real
            if trend_falling:
                # Mercado caindo = DELTA alto (puts ficam mais caros)
                delta_values = [min(1.0, abs(val) + 0.3) for val in delta_values] if delta_values else [0.8, 0.9, 1.0]
                logger.info(f"[{self.name}] QUEDA - DELTA AJUSTADO: {delta_values[-3:]}")

            return {'values': delta_values[-10:] if delta_values else [0]}
        except:
            return {'values': [0]}

    def extract_gamma_data(self, calls_df, puts_df, trend_falling=False):
        """Extrai dados GAMMA - AJUSTADO pela tendência real"""
        try:
            gamma_values = []
            strikes = []

            if not calls_df.empty and 'GAMMA' in calls_df.columns:
                gamma_values.extend(calls_df['GAMMA'].tolist())
                strikes.extend(calls_df['strike'].tolist())
            if not puts_df.empty and 'GAMMA' in puts_df.columns:
                gamma_values.extend(puts_df['GAMMA'].tolist())
                strikes.extend(puts_df['strike'].tolist())

            # AJUSTAR GAMMA baseado na tendência real
            if trend_falling:
                # Mercado caindo = GAMMA negativo (volatilidade bearish)
                gamma_values = [-abs(val) for val in gamma_values] if gamma_values else [-200, -150, -100]
                logger.info(f"[{self.name}] QUEDA - GAMMA AJUSTADO: {gamma_values[-3:]}")

            return {
                'values': gamma_values[-10:] if gamma_values else [100],
                'strikes': strikes[-10:] if strikes else [15250]
            }
        except:
            return {'values': [100], 'strikes': [15250]}

    def get_real_volume_data(self):
        """Obtém dados REAIS de volume do MT5"""
        try:
            # Obter dados de volume dos últimos 10 candles M1
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 10)

            if rates is not None and len(rates) > 0:
                # Extrair volumes reais
                volumes = [int(rate['tick_volume']) for rate in rates]
                current_volume = volumes[-1]
                average_volume = sum(volumes) / len(volumes)

                # Analisar volume
                if current_volume > average_volume * 1.5:
                    logger.info(f"[{self.name}] VOLUME ALTO: {current_volume} (média: {average_volume:.0f})")
                elif current_volume < average_volume * 0.5:
                    logger.info(f"[{self.name}] VOLUME BAIXO: {current_volume} (média: {average_volume:.0f})")

                return {
                    'current': current_volume,
                    'average': average_volume,
                    'profile': {'volumes': volumes}
                }
            else:
                # Fallback se não conseguir dados
                return {
                    'current': 1000,
                    'average': 1000,
                    'profile': {}
                }

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao obter volume: {e}")
            return {
                'current': 1000,
                'average': 1000,
                'profile': {}
            }

    def get_recent_price_data(self, current_price):
        """Obtém dados REAIS de preço do MT5"""
        try:
            # Obter dados históricos REAIS dos últimos 10 candles M1
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 10)

            if rates is not None and len(rates) > 0:
                # Extrair preços de fechamento reais
                recent_prices = [float(rate['close']) for rate in rates]

                # Verificar tendência real
                if len(recent_prices) >= 2:
                    if recent_prices[-1] < recent_prices[0]:  # Preço atual < primeiro preço = DESCENDO
                        logger.info(f"[{self.name}] VERMELHO - TENDÊNCIA REAL: DESCENDO ({recent_prices[0]:.2f} -> {recent_prices[-1]:.2f})")
                    elif recent_prices[-1] > recent_prices[0]:  # SUBINDO
                        logger.info(f"[{self.name}] VERDE - TENDÊNCIA REAL: SUBINDO ({recent_prices[0]:.2f} -> {recent_prices[-1]:.2f})")
                    else:
                        logger.info(f"[{self.name}] LATERAL - TENDÊNCIA REAL: LATERAL ({recent_prices[-1]:.2f})")

                return {'recent': recent_prices}
            else:
                logger.warning(f"[{self.name}] Não foi possível obter dados históricos - usando preço atual")
                return {'recent': [current_price]}

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao obter dados de preço: {e}")
            return {'recent': [current_price]}

    def execute_agent_recommendation(self, recommendation):
        """Executa trade usando SISTEMA DE ORDENS INTELIGENTES (BUY+BUY_LIMIT e SELL+SELL_LIMIT)"""
        try:
            if not self.is_connected or len(self.active_positions) >= self.max_positions:
                return False

            if recommendation.decision == TradingDecision.HOLD:
                logger.info(f"[{self.name}] Agentes recomendam AGUARDAR - {recommendation.reasoning}")
                return False

            # VERIFICAR SE MERCADO ESTÁ CONSOLIDADO - NÃO OPERAR
            if "CONSOLIDAT" in recommendation.setup_type.upper() or "SETUP5" in recommendation.setup_type:
                logger.info(f"[{self.name}] MERCADO CONSOLIDADO DETECTADO - NAO OPERANDO")
                logger.info(f"[{self.name}] Setup: {recommendation.setup_type} - AGUARDANDO BREAKOUT")
                return False

            # Obter dados para análise completa do SmartOrderSystem
            current_price = self.get_current_symbol_price()
            mock_calls = self.create_mock_options_data(current_price, option_type='call')
            mock_puts = self.create_mock_options_data(current_price, option_type='put')
            vwap_data = self.simulate_vwap_data(current_price)

            # ANÁLISE COMPLETA DOS 6 SETUPS + GAMMA/DELTA/CHARM
            smart_analysis = self.smart_order_system.analyze_complete_market(
                calls_df=mock_calls,
                puts_df=mock_puts,
                current_price=current_price,
                vwap_data=vwap_data
            )

            logger.info(f"[{self.name}] AGENTES DECIDEM: {recommendation.decision.value} - Setup: {recommendation.setup_type}")
            logger.info(f"[{self.name}] Confianca Multi-Agente: {recommendation.confidence:.1f}%")
            logger.info(f"[{self.name}] SmartOrder Analise: Tendencia={smart_analysis['trend_direction'].value}, Conf={smart_analysis['confidence']:.1f}%")

            # USAR APENAS a confiança dos Multi-Agentes (mais confiável)
            final_confidence = recommendation.confidence  # SÓ Multi-Agentes

            # VERIFICAR CONSOLIDAÇÃO POR BAIXA CONFIANÇA (sinais conflitantes)
            if final_confidence < 40:  # Confiança muito baixa = mercado consolidado
                logger.info(f"[{self.name}] CONFIANÇA BAIXA ({final_confidence:.1f}%) - MERCADO CONSOLIDADO")
                logger.info(f"[{self.name}] Sinais conflitantes detectados - NÃO OPERANDO")
                return False

            if final_confidence >= self.min_confidence_to_trade:
                # EXECUTAR SISTEMA DE ORDENS INTELIGENTES
                logger.info(f"[{self.name}] EXECUTANDO ORDENS INTELIGENTES - Conf. Final: {final_confidence:.1f}%")

                # Mostrar análise detalhada
                for reason in smart_analysis.get('reasoning', []):
                    logger.info(f"[{self.name}] {reason}")

                # EXECUTAR DIRETAMENTE baseado na DECISÃO DOS AGENTES
                # Pular o SmartOrder e executar direto
                if recommendation.decision.value == 'BUY':
                    success = self.place_direct_order('buy', current_price)
                    logger.info(f"[{self.name}] ORDEM EXECUTADA DIRETAMENTE: BUY")
                elif recommendation.decision.value == 'SELL':
                    success = self.place_direct_order('sell', current_price)
                    logger.info(f"[{self.name}] ORDEM EXECUTADA DIRETAMENTE: SELL")
                else:
                    success = False

                if success:
                    # Registrar no histórico
                    self.trade_history.append({
                        'timestamp': datetime.now(),
                        'action': recommendation.decision.value,  # Decisão dos agentes
                        'setup': recommendation.setup_type,
                        'multi_agent_confidence': recommendation.confidence,
                        'smart_order_confidence': smart_analysis['confidence'],
                        'final_confidence': final_confidence,
                        'entry_price': current_price,
                        'setups_active': smart_analysis.get('setups_active', []),
                        'reasoning': smart_analysis.get('reasoning', [])
                    })

                    logger.info(f"[{self.name}] ORDENS EXECUTADAS: {recommendation.decision.value} - Agentes Multi-Agente")
                    return True
                else:
                    logger.warning(f"[{self.name}] AVISO: Ordens inteligentes nao executadas - aguardando melhores sinais")
                    return False
            else:
                logger.info(f"[{self.name}] ⏸️ Confiança final {final_confidence:.1f}% < {self.min_confidence_to_trade}% - aguardando")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar ordens inteligentes: {e}")
            return False

    def execute_trades(self, setups_results):
        """Executa trades baseados nos setups"""
        if not self.is_connected or len(self.active_positions) >= self.max_positions:
            return

        for setup_key, setup_result in setups_results.items():
            if not setup_result.active or setup_result.confidence < self.min_confidence_to_trade:
                continue

            if not setup_result.target_price:
                continue

            # Determinar tipo de ordem baseado no setup
            order_type, action = self.get_order_type_from_setup(setup_result.setup_type)

            if order_type and action:
                success = self.place_market_order(action, self.lot_size)

                if success:
                    logger.info(f"[{self.name}] Trade executado: {setup_key} - {action} - Confiança: {setup_result.confidence:.1f}%")
                    break  # Executa apenas um trade por ciclo

    def get_order_type_from_setup(self, setup_type):
        """Converte tipo de setup em tipo de ordem"""
        order_map = {
            SetupType.BULLISH_BREAKOUT: ("market", "buy"),
            SetupType.BEARISH_BREAKOUT: ("market", "sell"),
            SetupType.PULLBACK_TOP: ("market", "sell"),
            SetupType.PULLBACK_BOTTOM: ("market", "buy"),
            SetupType.CONSOLIDATED_MARKET: (None, None),  # ← NÃO OPERAR em mercado consolidado!
            SetupType.GAMMA_NEGATIVE_PROTECTION: ("market", "buy")
        }

        return order_map.get(setup_type, (None, None))

    def place_agent_order(self, action, volume, recommendation):
        """Coloca ordem baseada na recomendação dos agentes com stops/targets específicos"""
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if not symbol_info:
                logger.error(f"[{self.name}] Símbolo {self.symbol} não encontrado")
                return False

            # Obter preços
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                logger.error(f"[{self.name}] Não foi possível obter preços para {self.symbol}")
                return False

            # Configurar ordem
            order_type = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL
            price = tick.ask if action == "buy" else tick.bid

            # Usar stops/targets recomendados pelos agentes
            sl = recommendation.stop_loss
            tp = recommendation.take_profit

            # Ajustar para máxima lucratividade
            stop_distance = abs(price - sl)
            target_distance = abs(tp - price)

            # Garantir R/R mínimo de 2:1 para máximo lucro
            min_target_distance = stop_distance * self.profit_multiplier

            if action == "buy":
                sl = max(sl, price * 0.985)  # Stop mais apertado (1.5% vs 1% anterior)
                tp = max(tp, price + min_target_distance)  # Target mais ambicioso
                tp = min(tp, price * 1.08)  # Mas não excessivamente distante
            else:
                sl = min(sl, price * 1.015)  # Stop mais apertado para SELL
                tp = min(tp, price - min_target_distance)  # Target mais ambicioso
                tp = max(tp, price * 0.92)  # Mas não excessivamente distante

            # Montar requisição
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"{self.name} - {recommendation.setup_type}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            # Executar ordem com fallback para diferentes modos de preenchimento
            result = mt5.order_send(request)

            # Se falhar com filling mode, tentar outros modos
            if result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                logger.warning(f"[{self.name}] Tentando modo de preenchimento alternativo...")

                # Tentar com ORDER_FILLING_IOC
                request["type_filling"] = mt5.ORDER_FILLING_IOC
                result = mt5.order_send(request)

                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    # Tentar com ORDER_FILLING_RETURN
                    request["type_filling"] = mt5.ORDER_FILLING_RETURN
                    result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] 🎉 ORDEM EXECUTADA: {action.upper()} {volume} {self.symbol} @ {price:.2f}")
                logger.info(f"[{self.name}] Stop Loss: {sl:.2f} | Take Profit: {tp:.2f}")
                return True
            else:
                logger.error(f"[{self.name}] ❌ Falha na ordem dos agentes: {result.retcode} - {result.comment}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar ordem dos agentes: {e}")
            return False

    def place_market_order(self, action, volume):
        """Coloca ordem de mercado"""
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if not symbol_info:
                logger.error(f"[{self.name}] Símbolo {self.symbol} não encontrado")
                return False

            # Obter preços
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                logger.error(f"[{self.name}] Não foi possível obter preços para {self.symbol}")
                return False

            # Configurar ordem
            order_type = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL
            price = tick.ask if action == "buy" else tick.bid

            # Stop Loss fixo de -0.02% e Take Profit de +50%
            sl_distance = price * 0.0002  # 0.02% stop loss FIXO
            tp_distance = price * 0.50     # 50% take profit (limite máximo)

            if action == "buy":
                sl = price - sl_distance
                tp = price + tp_distance  # +50% take profit
            else:
                sl = price + sl_distance
                tp = price - tp_distance  # -50% take profit para SELL

            # Montar requisição com configurações mais compatíveis
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"{self.name} - Auto Trade",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            # Executar ordem com fallback para diferentes modos de preenchimento
            result = mt5.order_send(request)

            # Se falhar com filling mode, tentar outros modos
            if result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                logger.warning(f"[{self.name}] Tentando modo de preenchimento alternativo...")

                # Tentar com ORDER_FILLING_IOC
                request["type_filling"] = mt5.ORDER_FILLING_IOC
                result = mt5.order_send(request)

                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    # Tentar com ORDER_FILLING_RETURN
                    request["type_filling"] = mt5.ORDER_FILLING_RETURN
                    result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] Ordem executada com sucesso: {action} {volume} {self.symbol} @ {price}")
                return True
            else:
                logger.error(f"[{self.name}] Falha na ordem: {result.retcode} - {result.comment}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar ordem: {e}")
            return False

    def place_direct_order(self, action, current_price):
        """Executa ordem diretamente sem SmartOrder - com stops de -0.02% e profit de +50%"""
        try:
            # Obter preços e informações do símbolo
            tick = mt5.symbol_info_tick(self.symbol)
            symbol_info = mt5.symbol_info(self.symbol)
            if not tick or not symbol_info:
                logger.error(f"[{self.name}] Nao foi possivel obter info para {self.symbol}")
                return False

            # Verificar stops mínimos do símbolo
            min_stop_distance = symbol_info.trade_stops_level * symbol_info.point
            if min_stop_distance == 0:
                min_stop_distance = 1.0  # 1 ponto mínimo se não informado

            # Configurar ordem com distâncias mínimas da corretora
            # Usar SEMPRE distâncias seguras
            min_distance = max(5.0, min_stop_distance)  # Mínimo 5.0 pontos para segurança

            if action == "buy":
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = price - min_distance                    # Stop Loss: 5.0 pontos abaixo
                tp = price + (min_distance * 2)              # Take Profit: 10.0 pontos acima (R/R 2:1)
                logger.info(f"[{self.name}] BUY - SL: -{min_distance} | TP: +{min_distance*2}")

            else:  # sell
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = price + min_distance                    # Stop Loss: 5.0 pontos acima
                tp = price - (min_distance * 2)              # Take Profit: 10.0 pontos abaixo (R/R 2:1)
                logger.info(f"[{self.name}] SELL - SL: +{min_distance} | TP: -{min_distance*2}")

            # Volume padrao
            volume = 0.01

            # Determinar filling type baseado nas capacidades do símbolo
            filling_type = mt5.ORDER_FILLING_FOK  # Fill or Kill como padrão
            if symbol_info.filling_mode & 1:  # ORDER_FILLING_FOK
                filling_type = mt5.ORDER_FILLING_FOK
            elif symbol_info.filling_mode & 2:  # ORDER_FILLING_IOC
                filling_type = mt5.ORDER_FILLING_IOC
            elif symbol_info.filling_mode & 4:  # ORDER_FILLING_RETURN
                filling_type = mt5.ORDER_FILLING_RETURN

            # Montar requisicao
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"{self.name} - DIRECT ORDER",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_type,
            }

            # Log detalhado da requisição
            logger.info(f"[{self.name}] EXECUTANDO {action.upper()}: price={price:.2f}, sl={sl:.2f}, tp={tp:.2f}")
            logger.info(f"[{self.name}] Filling type: {filling_type}, Symbol info: {symbol_info.filling_mode}")

            # Executar ordem
            result = mt5.order_send(request)

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] SUCESSO - ORDEM EXECUTADA: {action.upper()} {volume} {self.symbol} @ {price:.2f}")
                logger.info(f"[{self.name}] Stop Loss: {sl:.2f} | Take Profit: {tp:.2f}")
                return True
            else:
                if result:
                    logger.error(f"[{self.name}] ERRO {result.retcode}: {result.comment}")
                    logger.error(f"[{self.name}] Request: {request}")
                    logger.error(f"[{self.name}] Ask: {tick.ask}, Bid: {tick.bid}")
                else:
                    logger.error(f"[{self.name}] ERRO - Result é None - conexão perdida?")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar ordem direta: {e}")
            return False

    def manage_positions(self):
        """Gerencia posições abertas"""
        for position in self.active_positions:
            # Verificar se precisa fechar por stop loss manual ou outros critérios
            if position.profit < -50:  # Stop loss de emergência
                self.close_position(position)

    def close_position(self, position):
        """Fecha uma posição"""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return False

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

            if result is None:
                logger.error(f"[{self.name}] MT5 retornou None ao fechar posição: {position.ticket}")
                return False
            elif result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] Posição fechada: {position.ticket}")
                return True
            else:
                logger.error(f"[{self.name}] Falha ao fechar posição: {result.retcode}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao fechar posição: {e}")
            return False

    def close_all_positions(self):
        """Fecha TODAS as posições abertas - usado no Ctrl+C"""
        try:
            logger.info(f"[{self.name}] ==========================================")
            logger.info(f"[{self.name}] CTRL+C - FECHAMENTO COMPLETO INICIADO")
            logger.info(f"[{self.name}] ==========================================")

            # Buscar TODAS as posições do símbolo (não apenas magic number)
            all_positions = mt5.positions_get(symbol=self.symbol)
            magic_positions = mt5.positions_get(magic=self.magic_number)

            total_positions = []
            if all_positions:
                total_positions.extend(all_positions)
            if magic_positions:
                # Adicionar posições do magic number que não estão na lista
                for pos in magic_positions:
                    if pos not in total_positions:
                        total_positions.append(pos)

            if not total_positions:
                logger.info(f"[{self.name}] ✅ Nenhuma posição aberta em {self.symbol}")
            else:
                logger.info(f"[{self.name}] 📊 Encontradas {len(total_positions)} posições abertas em {self.symbol}")

                closed_count = 0
                for position in total_positions:
                    logger.info(f"[{self.name}] Fechando posição: {position.ticket} | Volume: {position.volume} | Lucro: {position.profit:.2f}")

                    if self.close_position(position):
                        closed_count += 1
                        logger.info(f"[{self.name}] ✅ FECHADA: {position.ticket}")
                    else:
                        logger.error(f"[{self.name}] ❌ ERRO ao fechar: {position.ticket}")

                logger.info(f"[{self.name}] POSIÇÕES: {closed_count}/{len(total_positions)} fechadas com sucesso")

            # Cancelar TODAS as ordens pendentes
            all_orders = mt5.orders_get(symbol=self.symbol)
            magic_orders = mt5.orders_get(magic=self.magic_number)

            total_orders = []
            if all_orders:
                total_orders.extend(all_orders)
            if magic_orders:
                for order in magic_orders:
                    if order not in total_orders:
                        total_orders.append(order)

            if not total_orders:
                logger.info(f"[{self.name}] ✅ Nenhuma ordem pendente em {self.symbol}")
            else:
                logger.info(f"[{self.name}] 📋 Encontradas {len(total_orders)} ordens pendentes em {self.symbol}")

                canceled_count = 0
                for order in total_orders:
                    logger.info(f"[{self.name}] Cancelando ordem: {order.ticket} | Tipo: {order.type} | Volume: {order.volume_initial}")

                    request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": order.ticket,
                    }
                    result = mt5.order_send(request)

                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        canceled_count += 1
                        logger.info(f"[{self.name}] ✅ CANCELADA: {order.ticket}")
                    else:
                        logger.error(f"[{self.name}] ❌ ERRO ao cancelar: {order.ticket}")

                logger.info(f"[{self.name}] ORDENS: {canceled_count}/{len(total_orders)} canceladas com sucesso")

            logger.info(f"[{self.name}] ==========================================")
            logger.info(f"[{self.name}] CTRL+C - FECHAMENTO COMPLETO FINALIZADO")
            logger.info(f"[{self.name}] TODAS AS NEGOCIACOES ENCERRADAS!")
            logger.info(f"[{self.name}] Sistema pronto para nova execução")
            logger.info(f"[{self.name}] ==========================================")

            return True

        except Exception as e:
            logger.error(f"[{self.name}] ERRO CRÍTICO ao fechar posições: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """Loop principal do agente"""
        if not self.is_connected:
            logger.error(f"[{self.name}] Não foi possível conectar ao MT5. Agente não iniciado.")
            return

        logger.info(f"[{self.name}] ==========================================")
        logger.info(f"[{self.name}] SISTEMA INICIADO - AGENTES PRONTOS!")
        logger.info(f"[{self.name}] ==========================================")
        logger.info(f"[{self.name}] OK - Conexão MT5: ATIVA")
        logger.info(f"[{self.name}] OK - Stop Loss: 5.0 pontos (BUY e SELL)")
        logger.info(f"[{self.name}] OK - Take Profit: 10.0 pontos (R/R 2:1)")
        logger.info(f"[{self.name}] OK - Distancias seguras para corretora FBS")
        logger.info(f"[{self.name}] OK - Ctrl+C: Fecha TODAS as negociações")
        logger.info(f"[{self.name}] ==========================================")
        logger.info(f"[{self.name}] AGUARDANDO SINAIS DOS AGENTES...")
        self.running = True

        try:
            while self.running:
                # Atualizar estado da conta
                self.update_account_state()

                # Verificar horário de trading
                if self.is_trading_hours():
                    logger.debug(f"[{self.name}] Mercado aberto - analisando...")

                    # Analisar mercado
                    setups_results = self.analyze_market()

                    # Executar trades se houver oportunidades
                    if setups_results:
                        self.execute_trades(setups_results)

                    # Gerenciar posições existentes
                    self.manage_positions()

                    # Aguardar antes da próxima análise
                    time.sleep(30)  # 30 segundos entre análises

                else:
                    logger.debug(f"[{self.name}] Mercado fechado - aguardando...")
                    time.sleep(300)  # 5 minutos quando mercado fechado

        except KeyboardInterrupt:
            logger.info(f"[{self.name}] === CTRL+C DETECTADO ===")
            logger.info(f"[{self.name}] FECHANDO TODAS AS NEGOCIACOES NO MT5...")
            self.close_all_positions()
        except Exception as e:
            logger.error(f"[{self.name}] Erro no loop principal: {e}")
        finally:
            self.stop()

    def stop(self):
        """Para o agente completamente"""
        logger.info(f"[{self.name}] ==========================================")
        logger.info(f"[{self.name}] PARANDO AGENTE COMPLETO...")
        logger.info(f"[{self.name}] ==========================================")

        self.running = False

        if self.is_connected:
            logger.info(f"[{self.name}] Desconectando do MetaTrader5...")
            mt5.shutdown()
            logger.info(f"[{self.name}] OK - MetaTrader5 desconectado")

        logger.info(f"[{self.name}] OK - AGENTE PARADO COM SUCESSO")
        logger.info(f"[{self.name}] Sistema pronto para nova execução")
        logger.info(f"[{self.name}] ==========================================")

    # Métodos para interface
    def get_status(self):
        """Retorna status atual do agente"""
        return {
            'connected': self.is_connected,
            'running': self.running,
            'balance': self.account_info.balance if self.account_info else 0,
            'equity': self.account_info.equity if self.account_info else 0,
            'positions': len(self.active_positions),
            'pnl': self.total_pnl,
            'setups': self.current_setups
        }

if __name__ == "__main__":
    # Configuração do agente
    config = {
        'name': 'RealAgent-FBS',
        'symbol': 'US100',
        'magic_number': 234001,
        'lot_size': 0.01
    }

    agent = RealAgentSystem(config)
    agent.start()

    try:
        while True:
            time.sleep(60)
            status = agent.get_status()
            print(f"Status: Connected={status['connected']}, Running={status['running']}, "
                  f"Balance=${status['balance']:.2f}, Positions={status['positions']}")
    except KeyboardInterrupt:
        print("\n=== CTRL+C DETECTADO ===")
        print("FECHANDO TODAS AS NEGOCIACOES...")

        # Fechar todas as posições e ordens antes de parar o agente
        agent.close_all_positions()

        print("Parando agente...")
        agent.stop()
        agent.join()

        print("Todas as negociacoes foram encerradas!")
        print("Sistema parado com seguranca.")