"""
Sistema de Agentes para LUCRO - Focado nos 4 agentes específicos
Criado para gerar lucros em vez de perdas
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
import yfinance as yf
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lucro_agentes.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LucroAgente(threading.Thread):
    """Agente base otimizado para LUCRO"""

    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.name = config.get('name', 'LucroAgente')
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 999999)
        self.lot_size = config.get('lot_size', 0.01)  # REDUZIDO para segurança

        # CONFIGURAÇÕES OTIMIZADAS PARA LUCRO
        self.min_confidence = 75.0  # AUMENTADO - apenas sinais de alta confiança
        self.max_positions = 3      # REDUZIDO - menos posições simultâneas
        self.stop_loss_pct = 0.5   # Stop loss de 0.5% (mais apertado)
        self.take_profit_pct = 2.0  # Take profit de 2% (otimizado para lucro)
        self.trailing_stop_pct = 1.0  # Trailing stop de 1%

        # Estado
        self.is_connected = False
        self.running = False
        self.positions = []
        self.setup_analyzer = TradingSetupAnalyzer()

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
            logger.info(f"[{self.name}] Conectado ao MT5 com sucesso!")
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

    def analyze_market(self):
        """Análise de mercado otimizada para LUCRO"""
        try:
            current_price = self.get_current_price()
            if not current_price:
                return {}

            # Criar dados simulados de opções
            calls_df = self.create_options_data(current_price, 'call')
            puts_df = self.create_options_data(current_price, 'put')

            # VWAP simulado
            vwap_data = {
                'vwap': current_price * 0.999,
                'std1_upper': current_price * 1.01,
                'std1_lower': current_price * 0.99
            }

            # Analisar apenas os 4 setups específicos
            setups_results = {}
            setups_results[SetupType.BUY_STOP_STRONG_MARKET.value] = self.analyze_buy_stop_strong(calls_df, puts_df, current_price)
            setups_results[SetupType.BUY_LIMIT_STRONG_MARKET.value] = self.analyze_buy_limit_strong(calls_df, puts_df, current_price)
            setups_results[SetupType.SELL_STOP_STRONG_MARKET.value] = self.analyze_sell_stop_strong(calls_df, puts_df, current_price)
            setups_results[SetupType.SELL_LIMIT_STRONG_MARKET.value] = self.analyze_sell_limit_strong(calls_df, puts_df, current_price)

            return setups_results

        except Exception as e:
            logger.error(f"[{self.name}] Erro na análise: {e}")
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

    def analyze_buy_stop_strong(self, calls_df, puts_df, current_price):
        """Análise específica para BUY STOP - OTIMIZADA PARA LUCRO"""
        try:
            # Verificar se há força compradora
            calls_gamma = calls_df[calls_df['strike'] > current_price]['GAMMA'].sum()
            calls_delta = calls_df[calls_df['strike'] > current_price]['DELTA'].sum()

            confidence = 0

            # Condições para BUY STOP FORTE
            if calls_gamma > 500:  # Gamma alto = volatilidade compradora
                confidence += 40
            if calls_delta > 0.5:  # Delta positivo = momentum comprador
                confidence += 35
            if current_price > calls_df['strike'].mean():  # Preço acima da média
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
            return type('SetupResult', (), {
                'setup_type': SetupType.BUY_STOP_STRONG_MARKET,
                'active': False,
                'confidence': 0,
                'target_price': None,
                'stop_loss': None,
                'risk_level': 'HIGH'
            })()

    def analyze_buy_limit_strong(self, calls_df, puts_df, current_price):
        """Análise específica para BUY LIMIT - OTIMIZADA PARA LUCRO"""
        try:
            # Verificar força compradora mas preço caindo
            calls_gamma = calls_df['GAMMA'].sum()
            puts_delta = puts_df['DELTA'].sum()

            confidence = 0

            # Condições para BUY LIMIT (compra na queda)
            if calls_gamma > 300:  # Gamma moderado
                confidence += 30
            if puts_delta < -0.3:  # Puts caras = mercado caindo
                confidence += 40
            if current_price < calls_df['strike'].mean():  # Preço abaixo da média
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
            return type('SetupResult', (), {
                'setup_type': SetupType.BUY_LIMIT_STRONG_MARKET,
                'active': False,
                'confidence': 0,
                'target_price': None,
                'stop_loss': None,
                'risk_level': 'HIGH'
            })()

    def analyze_sell_stop_strong(self, calls_df, puts_df, current_price):
        """Análise específica para SELL STOP - OTIMIZADA PARA LUCRO"""
        try:
            # Verificar força vendedora
            puts_gamma = puts_df[puts_df['strike'] < current_price]['GAMMA'].sum()
            puts_delta = puts_df[puts_df['strike'] < current_price]['DELTA'].sum()

            confidence = 0

            # Condições para SELL STOP FORTE
            if puts_gamma > 500:  # Gamma alto = volatilidade vendedora
                confidence += 40
            if puts_delta < -0.5:  # Delta negativo = momentum vendedor
                confidence += 35
            if current_price > puts_df['strike'].mean():  # Preço acima da média
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
            return type('SetupResult', (), {
                'setup_type': SetupType.SELL_STOP_STRONG_MARKET,
                'active': False,
                'confidence': 0,
                'target_price': None,
                'stop_loss': None,
                'risk_level': 'HIGH'
            })()

    def analyze_sell_limit_strong(self, calls_df, puts_df, current_price):
        """Análise específica para SELL LIMIT - OTIMIZADA PARA LUCRO"""
        try:
            # Verificar força vendedora mas preço subindo
            puts_gamma = puts_df['GAMMA'].sum()
            calls_delta = calls_df['DELTA'].sum()

            confidence = 0

            # Condições para SELL LIMIT (venda na alta)
            if puts_gamma > 300:  # Gamma moderado
                confidence += 30
            if calls_delta > 0.3:  # Calls caras = mercado subindo
                confidence += 40
            if current_price > puts_df['strike'].mean():  # Preço acima da média
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
            return type('SetupResult', (), {
                'setup_type': SetupType.SELL_LIMIT_STRONG_MARKET,
                'active': False,
                'confidence': 0,
                'target_price': None,
                'stop_loss': None,
                'risk_level': 'HIGH'
            })()

    def execute_trade(self, setup_result):
        """Executa trade com configurações otimizadas para LUCRO"""
        try:
            if not setup_result.active or not setup_result.target_price:
                return False

            current_price = self.get_current_price()
            if not current_price:
                return False

            # Configurar ordem
            if setup_result.setup_type == SetupType.BUY_STOP_STRONG_MARKET:
                action = "BUY"
                order_type = "BUY_STOP"
                price = current_price * 1.001
            elif setup_result.setup_type == SetupType.BUY_LIMIT_STRONG_MARKET:
                action = "BUY"
                order_type = "BUY_LIMIT"
                price = current_price * 0.999
            elif setup_result.setup_type == SetupType.SELL_STOP_STRONG_MARKET:
                action = "SELL"
                order_type = "SELL_STOP"
                price = current_price * 0.999
            elif setup_result.setup_type == SetupType.SELL_LIMIT_STRONG_MARKET:
                action = "SELL"
                order_type = "SELL_LIMIT"
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
                "type": self.get_order_type(order_type),
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
                logger.info(f"[{self.name}] ✅ ORDEM EXECUTADA: {action} {self.lot_size} @ {price:.2f} (SL: {sl:.2f}, TP: {tp:.2f})")
                return True
            else:
                logger.error(f"[{self.name}] ❌ Falha na ordem: {result.retcode if result else 'None'}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro na execução: {e}")
            return False

    def get_order_type(self, order_kind):
        """Converte tipo de ordem"""
        order_types = {
            "BUY_LIMIT": mt5.ORDER_TYPE_BUY_LIMIT,
            "SELL_LIMIT": mt5.ORDER_TYPE_SELL_LIMIT,
            "BUY_STOP": mt5.ORDER_TYPE_BUY_STOP,
            "SELL_STOP": mt5.ORDER_TYPE_SELL_STOP
        }
        return order_types.get(order_kind)

    def run(self):
        """Loop principal otimizado para LUCRO"""
        if not self.is_connected:
            logger.error(f"[{self.name}] MT5 não conectado")
            return

        logger.info(f"[{self.name}] 🚀 INICIADO - Sistema Otimizado para LUCRO!")
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

                # Analisar mercado
                setups = self.analyze_market()

                # Verificar posições atuais
                positions = mt5.positions_get(magic=self.magic_number)
                current_positions = len(positions) if positions else 0

                logger.info(f"[{self.name}] 📊 Posições atuais: {current_positions}/{self.max_positions}")

                # Executar apenas 1 trade por ciclo se houver oportunidade
                trade_executed = False
                for setup_name, setup_result in setups.items():
                    if (setup_result.active and
                        setup_result.confidence >= self.min_confidence and
                        current_positions < self.max_positions and
                        not trade_executed):

                        logger.info(f"[{self.name}] 🎯 SINAL DETECTADO: {setup_name} (Conf: {setup_result.confidence:.1f}%)")
                        if self.execute_trade(setup_result):
                            trade_executed = True
                            logger.info(f"[{self.name}] ✅ Trade executado com sucesso!")
                        break

                # Aguardar antes da próxima análise
                time.sleep(30)  # Análise a cada 30 segundos

        except KeyboardInterrupt:
            logger.info(f"[{self.name}] ⏹️ Interrupção detectada")
        except Exception as e:
            logger.error(f"[{self.name}] Erro no loop: {e}")
        finally:
            self.stop()

    def stop(self):
        """Para o agente"""
        logger.info(f"[{self.name}] 🛑 Parando agente...")
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

class SistemaLucroAgentes:
    """Sistema principal que gerencia os 4 agentes específicos"""

    def __init__(self):
        self.config = {
            'symbol': 'US100',
            'lot_size': 0.01
        }

        self.agentes = {
            'buy_stop': LucroAgente({**self.config, 'name': 'BuyStopLucro', 'magic_number': 111111}),
            'buy_limit': LucroAgente({**self.config, 'name': 'BuyLimitLucro', 'magic_number': 222222}),
            'sell_stop': LucroAgente({**self.config, 'name': 'SellStopLucro', 'magic_number': 333333}),
            'sell_limit': LucroAgente({**self.config, 'name': 'SellLimitLucro', 'magic_number': 444444})
        }

        self.running = False

    def iniciar_todos(self):
        """Inicia todos os 4 agentes"""
        logger.info("🚀 INICIANDO SISTEMA DE LUCRO COM 4 AGENTES ESPECÍFICOS")
        logger.info("🎯 Buy Stop - Compra quando mercado compra forte")
        logger.info("💰 Buy Limit - Compra quando mercado cai mas está forte")
        logger.info("📉 Sell Stop - Vende quando mercado vende forte")
        logger.info("🎯 Sell Limit - Vende quando mercado sobe mas está fraco")

        for nome, agente in self.agentes.items():
            agente.start()
            logger.info(f"✅ Agente {nome} iniciado")

        self.running = True
        logger.info("🎉 TODOS OS 4 AGENTES ATIVOS E FUNCIONANDO!")

    def parar_todos(self):
        """Para todos os agentes"""
        logger.info("🛑 PARANDO TODOS OS AGENTES...")
        self.running = False

        for nome, agente in self.agentes.items():
            agente.stop()
            agente.join()
            logger.info(f"✅ Agente {nome} parado")

        logger.info("🎉 SISTEMA COMPLETAMENTE PARADO!")

if __name__ == "__main__":
    # Criar e iniciar o sistema
    sistema = SistemaLucroAgentes()

    try:
        sistema.iniciar_todos()

        # Manter sistema rodando
        while sistema.running:
            time.sleep(60)

            # Verificar status dos agentes
            status_info = []
            for nome, agente in sistema.agentes.items():
                positions = 0
                try:
                    if agente.is_connected:
                        positions = len(mt5.positions_get(magic=agente.magic_number) or [])
                except:
                    pass
                status_info.append(f"{nome}: {positions} pos")

            logger.info(f"📊 Status: {' | '.join(status_info)}")

    except KeyboardInterrupt:
        logger.info("⏹️ Interrupção detectada pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro no sistema: {e}")
    finally:
        sistema.parar_todos()
        logger.info("🎯 SISTEMA FINALIZADO")