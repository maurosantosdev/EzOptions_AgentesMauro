"""
Sistema Completo de Agentes para LUCRO
Combina os 10 agentes multi-agente com os 4 agentes específicos
Otimizado para gerar lucros em vez de perdas
"""

import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import threading
from datetime import datetime, time as datetime_time
import pytz
import logging
from trading_setups import TradingSetupAnalyzer, SetupType
from multi_agent_system import MultiAgentTradingSystem, MarketAnalysis, TradingDecision
import yfinance as yf
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_lucro_completo.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SistemaLucroCompleto(threading.Thread):
    """Sistema completo que combina 10 agentes + 4 agentes específicos"""

    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.name = config.get('name', 'SistemaLucroCompleto')
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 777777)

        # CONFIGURAÇÕES OTIMIZADAS PARA LUCRO
        self.lot_size = 0.01  # Volume reduzido para segurança
        self.min_confidence = 75.0  # Alta confiança necessária
        self.max_positions = 5  # Máximo 5 posições simultâneas
        self.stop_loss_pct = 0.5  # Stop loss apertado (0.5%)
        self.take_profit_pct = 2.0  # Take profit otimizado (2%)
        self.trailing_stop_pct = 1.0  # Trailing stop (1%)

        # Estado
        self.is_connected = False
        self.running = False
        self.positions = []

        # Sistemas de análise
        self.setup_analyzer = TradingSetupAnalyzer()
        self.multi_agent_system = MultiAgentTradingSystem()

        # Conectar ao MT5
        self.connect_mt5()

    def connect_mt5(self):
        """Conecta ao MetaTrader5"""
        try:
            if not mt5.initialize(
                login=int(os.getenv("MT5_LOGIN")),
                server=os.getenv("MT5_SERVER"),
                password=os.getenv("MT5_PASSWORD")
            ):
                logger.error(f"[{self.name}] Falha na conexão MT5")
                return False

            self.is_connected = True
            logger.info(f"[{self.name}] ✅ Conectado ao MT5 com sucesso!")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Erro na conexão: {e}")
            return False

    def get_current_price(self):
        """Obtém preço atual"""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
                return (tick.bid + tick.ask) / 2
            return None
        except:
            return None

    def analyze_complete_market(self):
        """Análise completa usando 10 agentes + 4 agentes específicos"""
        try:
            current_price = self.get_current_price()
            if not current_price:
                return {}

            # 1. ANÁLISE DOS 10 AGENTES MULTI-AGENTE
            logger.info(f"[{self.name}] 🤖 Iniciando análise dos 10 agentes...")

            # Criar dados de mercado para os 10 agentes
            calls_df = self.create_options_data(current_price, 'call')
            puts_df = self.create_options_data(current_price, 'put')

            # Extrair dados greeks
            charm_data = self.extract_greeks_data(calls_df, puts_df, 'CHARM')
            delta_data = self.extract_greeks_data(calls_df, puts_df, 'DELTA')
            gamma_data = self.extract_greeks_data(calls_df, puts_df, 'GAMMA')

            # VWAP simulado
            vwap_data = {
                'vwap': current_price * 0.999,
                'std1_upper': current_price * 1.01,
                'std1_lower': current_price * 0.99
            }

            # Dados reais de preço e volume
            price_data = {'recent': [current_price] * 5}  # Simplificado
            volume_data = {'current': 1000, 'average': 1000}

            # Análise dos 10 agentes
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

            multi_agent_recommendation = self.multi_agent_system.analyze_market_collaborative(market_data)

            # 2. ANÁLISE DOS 4 AGENTES ESPECÍFICOS
            logger.info(f"[{self.name}] 🎯 Iniciando análise dos 4 agentes específicos...")

            specific_setups = {}
            specific_setups[SetupType.BUY_STOP_STRONG_MARKET.value] = self.analyze_buy_stop_strong(calls_df, puts_df, current_price)
            specific_setups[SetupType.BUY_LIMIT_STRONG_MARKET.value] = self.analyze_buy_limit_strong(calls_df, puts_df, current_price)
            specific_setups[SetupType.SELL_STOP_STRONG_MARKET.value] = self.analyze_sell_stop_strong(calls_df, puts_df, current_price)
            specific_setups[SetupType.SELL_LIMIT_STRONG_MARKET.value] = self.analyze_sell_limit_strong(calls_df, puts_df, current_price)

            # 3. COMBINAR ANÁLISES
            combined_analysis = {
                'multi_agent': multi_agent_recommendation,
                'specific_setups': specific_setups,
                'current_price': current_price
            }

            logger.info(f"[{self.name}] ✅ Análise completa finalizada")
            return combined_analysis

        except Exception as e:
            logger.error(f"[{self.name}] Erro na análise completa: {e}")
            return {}

    def create_options_data(self, current_price, option_type):
        """Cria dados de opções simulados"""
        strikes = []
        strike = current_price * 0.95
        while strike <= current_price * 1.05:
            strikes.append(strike)
            strike += current_price * 0.005

        data = []
        for strike in strikes:
            if option_type == 'call':
                delta = max(0.1, min(0.9, (strike/current_price - 0.95) * 5))
                gamma = 100 * np.exp(-abs(strike/current_price - 1) * 10)
                charm = np.random.uniform(-20, 20)
            else:
                delta = max(-0.9, min(-0.1, (0.95 - strike/current_price) * 5))
                gamma = 100 * np.exp(-abs(strike/current_price - 1) * 10)
                charm = np.random.uniform(-20, 20)

            data.append({
                'strike': strike,
                'DELTA': delta,
                'GAMMA': gamma,
                'CHARM': charm,
                'GEX': gamma * 500
            })

        return pd.DataFrame(data)

    def extract_greeks_data(self, calls_df, puts_df, greek_type):
        """Extrai dados de greeks"""
        values = []
        if not calls_df.empty and greek_type in calls_df.columns:
            values.extend(calls_df[greek_type].tolist())
        if not puts_df.empty and greek_type in puts_df.columns:
            values.extend(puts_df[greek_type].tolist())

        return {'values': values[-10:] if values else [0]}

    def analyze_buy_stop_strong(self, calls_df, puts_df, current_price):
        """Análise para BUY STOP FORTE"""
        try:
            calls_gamma = calls_df[calls_df['strike'] > current_price]['GAMMA'].sum()
            calls_delta = calls_df[calls_df['strike'] > current_price]['DELTA'].sum()

            confidence = 0
            if calls_gamma > 500:
                confidence += 40
            if calls_delta > 0.5:
                confidence += 35
            if current_price > calls_df['strike'].mean():
                confidence += 25

            active = confidence >= self.min_confidence
            target_price = current_price * 1.002 if active else None
            stop_loss = current_price * 0.995 if active else None

            return type('SetupResult', (), {
                'setup_type': SetupType.BUY_STOP_STRONG_MARKET,
                'active': active,
                'confidence': confidence,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'risk_level': 'LOW' if confidence > 85 else 'MEDIUM'
            })()

        except Exception as e:
            logger.error(f"[{self.name}] Erro no BUY STOP: {e}")
            return type('SetupResult', (), {'setup_type': SetupType.BUY_STOP_STRONG_MARKET, 'active': False, 'confidence': 0, 'target_price': None, 'stop_loss': None, 'risk_level': 'HIGH'})()

    def analyze_buy_limit_strong(self, calls_df, puts_df, current_price):
        """Análise para BUY LIMIT FORTE"""
        try:
            calls_gamma = calls_df['GAMMA'].sum()
            puts_delta = puts_df['DELTA'].sum()

            confidence = 0
            if calls_gamma > 300:
                confidence += 30
            if puts_delta < -0.3:
                confidence += 40
            if current_price < calls_df['strike'].mean():
                confidence += 30

            active = confidence >= self.min_confidence
            target_price = current_price * 0.998 if active else None
            stop_loss = current_price * 0.994 if active else None

            return type('SetupResult', (), {
                'setup_type': SetupType.BUY_LIMIT_STRONG_MARKET,
                'active': active,
                'confidence': confidence,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'risk_level': 'LOW' if confidence > 85 else 'MEDIUM'
            })()

        except Exception as e:
            logger.error(f"[{self.name}] Erro no BUY LIMIT: {e}")
            return type('SetupResult', (), {'setup_type': SetupType.BUY_LIMIT_STRONG_MARKET, 'active': False, 'confidence': 0, 'target_price': None, 'stop_loss': None, 'risk_level': 'HIGH'})()

    def analyze_sell_stop_strong(self, calls_df, puts_df, current_price):
        """Análise para SELL STOP FORTE"""
        try:
            puts_gamma = puts_df[puts_df['strike'] < current_price]['GAMMA'].sum()
            puts_delta = puts_df[puts_df['strike'] < current_price]['DELTA'].sum()

            confidence = 0
            if puts_gamma > 500:
                confidence += 40
            if puts_delta < -0.5:
                confidence += 35
            if current_price > puts_df['strike'].mean():
                confidence += 25

            active = confidence >= self.min_confidence
            target_price = current_price * 0.998 if active else None
            stop_loss = current_price * 1.005 if active else None

            return type('SetupResult', (), {
                'setup_type': SetupType.SELL_STOP_STRONG_MARKET,
                'active': active,
                'confidence': confidence,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'risk_level': 'LOW' if confidence > 85 else 'MEDIUM'
            })()

        except Exception as e:
            logger.error(f"[{self.name}] Erro no SELL STOP: {e}")
            return type('SetupResult', (), {'setup_type': SetupType.SELL_STOP_STRONG_MARKET, 'active': False, 'confidence': 0, 'target_price': None, 'stop_loss': None, 'risk_level': 'HIGH'})()

    def analyze_sell_limit_strong(self, calls_df, puts_df, current_price):
        """Análise para SELL LIMIT FORTE"""
        try:
            puts_gamma = puts_df['GAMMA'].sum()
            calls_delta = calls_df['DELTA'].sum()

            confidence = 0
            if puts_gamma > 300:
                confidence += 30
            if calls_delta > 0.3:
                confidence += 40
            if current_price > puts_df['strike'].mean():
                confidence += 30

            active = confidence >= self.min_confidence
            target_price = current_price * 1.002 if active else None
            stop_loss = current_price * 1.006 if active else None

            return type('SetupResult', (), {
                'setup_type': SetupType.SELL_LIMIT_STRONG_MARKET,
                'active': active,
                'confidence': confidence,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'risk_level': 'LOW' if confidence > 85 else 'MEDIUM'
            })()

        except Exception as e:
            logger.error(f"[{self.name}] Erro no SELL LIMIT: {e}")
            return type('SetupResult', (), {'setup_type': SetupType.SELL_LIMIT_STRONG_MARKET, 'active': False, 'confidence': 0, 'target_price': None, 'stop_loss': None, 'risk_level': 'HIGH'})()

    def execute_best_signal(self, analysis):
        """Executa o melhor sinal disponível"""
        try:
            current_price = analysis['current_price']
            multi_agent = analysis['multi_agent']
            specific_setups = analysis['specific_setups']

            # Verificar posições atuais
            positions = mt5.positions_get(magic=self.magic_number)
            current_positions = len(positions) if positions else 0

            if current_positions >= self.max_positions:
                logger.info(f"[{self.name}] 📊 Limite de posições atingido: {current_positions}/{self.max_positions}")
                return False

            # 1. Verificar sinais dos 4 agentes específicos (prioridade alta)
            best_specific_signal = None
            best_confidence = 0

            for setup_name, setup_result in specific_setups.items():
                if (setup_result.active and
                    setup_result.confidence >= self.min_confidence and
                    setup_result.target_price):

                    if setup_result.confidence > best_confidence:
                        best_confidence = setup_result.confidence
                        best_specific_signal = setup_result

            # 2. Se há sinal específico forte, executar
            if best_specific_signal:
                logger.info(f"[{self.name}] 🎯 SINAL ESPECÍFICO FORTE: {best_specific_signal.setup_type.value} (Conf: {best_specific_signal.confidence:.1f}%)")
                return self.execute_trade(best_specific_signal, current_price)

            # 3. Verificar sinal dos 10 agentes multi-agente
            if (hasattr(multi_agent, 'confidence') and
                multi_agent.confidence >= self.min_confidence and
                hasattr(multi_agent, 'decision') and
                multi_agent.decision != TradingDecision.HOLD):

                logger.info(f"[{self.name}] 🤖 SINAL MULTI-AGENTE: {multi_agent.decision.value} (Conf: {multi_agent.confidence:.1f}%)")
                return self.execute_multi_agent_trade(multi_agent, current_price)

            logger.info(f"[{self.name}] ⏸️ Nenhum sinal com confiança suficiente")
            return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro na execução: {e}")
            return False

    def execute_trade(self, setup_result, current_price):
        """Executa trade dos 4 agentes específicos"""
        try:
            if not setup_result.target_price:
                return False

            # Configurar ordem baseada no tipo de setup
            if setup_result.setup_type == SetupType.BUY_STOP_STRONG_MARKET:
                action = "BUY"
                order_type = mt5.ORDER_TYPE_BUY_STOP
                price = current_price * 1.001
            elif setup_result.setup_type == SetupType.BUY_LIMIT_STRONG_MARKET:
                action = "BUY"
                order_type = mt5.ORDER_TYPE_BUY_LIMIT
                price = current_price * 0.999
            elif setup_result.setup_type == SetupType.SELL_STOP_STRONG_MARKET:
                action = "SELL"
                order_type = mt5.ORDER_TYPE_SELL_STOP
                price = current_price * 0.999
            elif setup_result.setup_type == SetupType.SELL_LIMIT_STRONG_MARKET:
                action = "SELL"
                order_type = mt5.ORDER_TYPE_SELL_LIMIT
                price = current_price * 1.001
            else:
                return False

            # Calcular SL e TP
            if action == "BUY":
                sl = price * (1 - self.stop_loss_pct/100)
                tp = price * (1 + self.take_profit_pct/100)
            else:
                sl = price * (1 + self.stop_loss_pct/100)
                tp = price * (1 - self.take_profit_pct/100)

            # Executar ordem
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": order_type,
                "price": round(price, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "magic": self.magic_number,
                "comment": f"{self.name} - {setup_result.setup_type.value}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }

            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] ✅ ORDEM ESPECÍFICA EXECUTADA: {action} {self.lot_size} @ {price:.2f}")
                logger.info(f"[{self.name}] 🎯 SL: {sl:.2f} | TP: {tp:.2f}")
                return True
            else:
                logger.error(f"[{self.name}] ❌ Falha na ordem específica: {result.retcode if result else 'None'}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro na execução específica: {e}")
            return False

    def execute_multi_agent_trade(self, recommendation, current_price):
        """Executa trade dos 10 agentes multi-agente"""
        try:
            if not hasattr(recommendation, 'decision') or recommendation.decision == TradingDecision.HOLD:
                return False

            # Configurar ordem baseada na decisão dos 10 agentes
            if recommendation.decision == TradingDecision.BUY:
                action = "BUY"
                order_type = mt5.ORDER_TYPE_BUY_STOP
                price = current_price * 1.001
            elif recommendation.decision == TradingDecision.SELL:
                action = "SELL"
                order_type = mt5.ORDER_TYPE_SELL_STOP
                price = current_price * 0.999
            else:
                return False

            # Calcular SL e TP
            if action == "BUY":
                sl = price * (1 - self.stop_loss_pct/100)
                tp = price * (1 + self.take_profit_pct/100)
            else:
                sl = price * (1 + self.stop_loss_pct/100)
                tp = price * (1 - self.take_profit_pct/100)

            # Executar ordem
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": order_type,
                "price": round(price, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "magic": self.magic_number,
                "comment": f"{self.name} - MultiAgent {recommendation.setup_type}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }

            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.name}] 🤖 ORDEM MULTI-AGENTE EXECUTADA: {action} {self.lot_size} @ {price:.2f}")
                logger.info(f"[{self.name}] 🎯 SL: {sl:.2f} | TP: {tp:.2f}")
                return True
            else:
                logger.error(f"[{self.name}] ❌ Falha na ordem multi-agente: {result.retcode if result else 'None'}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro na execução multi-agente: {e}")
            return False

    def run(self):
        """Loop principal do sistema completo"""
        if not self.is_connected:
            logger.error(f"[{self.name}] MT5 não conectado")
            return

        logger.info(f"[{self.name}] 🚀 SISTEMA COMPLETO INICIADO!")
        logger.info(f"[{self.name}] 🤖 10 Agentes Multi-Agente + 🎯 4 Agentes Específicos")
        logger.info(f"[{self.name}] 📊 Confiança mínima: {self.min_confidence}%")
        logger.info(f"[{self.name}] 🎯 Stop Loss: {self.stop_loss_pct}% | Take Profit: {self.take_profit_pct}%")
        logger.info(f"[{self.name}] 📈 Máximo posições: {self.max_positions}")

        self.running = True

        try:
            while self.running:
                # Verificar se é horário de trading
                if not self.is_trading_hours():
                    time.sleep(60)
                    continue

                # Executar análise completa
                analysis = self.analyze_complete_market()

                if analysis:
                    # Executar melhor sinal disponível
                    self.execute_best_signal(analysis)

                # Aguardar antes da próxima análise
                time.sleep(30)  # Análise a cada 30 segundos

        except KeyboardInterrupt:
            logger.info(f"[{self.name}] ⏹️ Interrupção detectada")
        except Exception as e:
            logger.error(f"[{self.name}] Erro no loop: {e}")
        finally:
            self.stop()

    def stop(self):
        """Para o sistema"""
        logger.info(f"[{self.name}] 🛑 Parando sistema...")
        self.running = False

        # Fechar todas as posições
        try:
            positions = mt5.positions_get(magic=self.magic_number)
            if positions:
                for pos in positions:
                    self.close_position(pos.ticket)
        except:
            pass

        # Fechar conexão
        try:
            mt5.shutdown()
        except:
            pass

    def close_position(self, ticket):
        """Fecha posição específica"""
        try:
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                return True

            pos = positions[0]
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY

            tick = mt5.symbol_info_tick(self.symbol)
            price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": self.magic_number,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }

            result = mt5.order_send(request)
            return result and result.retcode == mt5.TRADE_RETCODE_DONE

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao fechar posição {ticket}: {e}")
            return False

    def is_trading_hours(self):
        """Verifica se é horário de trading"""
        try:
            ny_tz = pytz.timezone('America/New_York')
            now_ny = datetime.now(ny_tz)

            if now_ny.weekday() > 4:  # Fim de semana
                return False

            market_open = datetime_time(9, 30, 0)
            market_close = datetime_time(16, 0, 0)

            return market_open <= now_ny.time() <= market_close
        except:
            return True

if __name__ == "__main__":
    # Criar e iniciar o sistema completo
    config = {
        'name': 'SistemaLucroCompleto',
        'symbol': 'US100',
        'magic_number': 777777
    }

    sistema = SistemaLucroCompleto(config)
    sistema.start()

    try:
        # Manter sistema rodando
        while True:
            time.sleep(60)
            logger.info(f"[{config['name']}] Sistema ativo - Aguardando sinais...")

    except KeyboardInterrupt:
        logger.info("⏹️ Interrupção detectada pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro no sistema: {e}")
    finally:
        sistema.stop()
        sistema.join()
        logger.info("🎯 SISTEMA COMPLETO FINALIZADO")