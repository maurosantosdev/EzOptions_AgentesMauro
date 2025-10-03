#!/usr/bin/env python3
"""
SISTEMA SEGURO LUCRATIVO - VERSÃO INTEGRADA
Sistema principal + Emergency Stop Loss em um único processo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_completo_14_agentes import SistemaCompletoAgentes
import time
import logging
import threading
import MetaTrader5 as mt5

# Configurar logging sem emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_seguro.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EmergencyStopLoss:
    """Sistema de emergência integrado com trailing stop avançado"""

    def __init__(self):
        self.min_confidence = 50.0
        self.stop_loss_limit = -0.15  # Stop loss mais conservador
        self.max_positions = 2
        self.emergency_active = False

        # Sistema de preço alvo futuro
        self.target_price = 100.0  # Preço alvo de $100
        self.profit_target_pct = 2.0  # 2% de lucro alvo

        # Sistema de trailing stop com 6 setups + greeks
        self.use_greeks_trailing = True
        self.greeks_weights = {'gamma': 0.4, 'delta': 0.35, 'charm': 0.25}

        # Controle de setups
        self.setups_status = {
            'bullish_breakout': {'active': False, 'strength': 0},
            'bearish_breakout': {'active': False, 'strength': 0},
            'pullback_top': {'active': False, 'strength': 0},
            'pullback_bottom': {'active': False, 'strength': 0},
            'consolidated_market': {'active': False, 'strength': 0},
            'gamma_negative_protection': {'active': False, 'strength': 0}
        }

    def check_and_close_positions(self):
        """Verifica e fecha posições com perda excessiva + trailing stop avançado"""
        try:
            positions = mt5.positions_get(symbol="US100", magic=234001)

            if not positions:
                return True

            # Analisar setups e greeks para trailing stop
            greeks_strength = self.analyze_6_setups_greeks()

            for pos in positions:
                current_profit = pos.profit

                # 1. EMERGÊNCIA: Stop loss forçado
                if current_profit <= self.stop_loss_limit:
                    logger.error(f'EMERGENCIA: Fechando posicao {pos.ticket} - Perda: ${current_profit:.2f}')
                    self.close_position_emergency(pos)
                    continue

                # 2. TRAILING STOP AVANÇADO: Baseado nos 6 setups + greeks
                if current_profit > 0.3:  # Só aplicar trailing se estiver lucrando
                    trailing_distance = self.calculate_dynamic_trailing_stop(pos, greeks_strength)

                    if self.should_apply_trailing_stop(pos, trailing_distance):
                        logger.info(f'TRAILING STOP ATIVADO: Fechando posicao {pos.ticket} - Lucro: ${current_profit:.2f}')
                        self.close_position_trailing(pos)
                        continue

                # 3. PREÇO ALVO FUTURO: Fechar se atingir $100
                if self.check_target_price_reached(pos):
                    logger.info(f'ALVO ALCANÇADO: Fechando posicao {pos.ticket} - Preco alvo $100 atingido')
                    self.close_position_target(pos)
                    continue

            return True

        except Exception as e:
            logger.error(f'Erro no sistema de emergencia: {e}')
            return False

    def close_position_emergency(self, position):
        """Fecha posição por emergência"""
        try:
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick("US100").bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick("US100").ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "US100",
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": 20,
                "magic": 234001,
                "comment": "Emergency Stop Loss",
                "type_time": mt5.ORDER_TIME_GTC,
            }

            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f'Posicao {position.ticket} fechada por emergencia')
                return True
            else:
                logger.error(f'Falha ao fechar posicao {position.ticket} por emergencia')
                return False
        except Exception as e:
            logger.error(f'Erro ao fechar posicao de emergencia {position.ticket}: {e}')
            return False

    def close_position_trailing(self, position):
        """Fecha posição por trailing stop"""
        try:
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick("US100").bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick("US100").ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "US100",
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": 20,
                "magic": 234001,
                "comment": "Trailing Stop (6 Setups + Greeks)",
                "type_time": mt5.ORDER_TIME_GTC,
            }

            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f'Posicao {position.ticket} fechada por trailing stop - Lucro: ${position.profit:.2f}')
                return True
            else:
                logger.error(f'Falha ao fechar posicao {position.ticket} por trailing')
                return False
        except Exception as e:
            logger.error(f'Erro ao fechar posicao por trailing {position.ticket}: {e}')
            return False

    def close_position_target(self, position):
        """Fecha posição por atingir preço alvo"""
        try:
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick("US100").bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick("US100").ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": "US100",
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": 20,
                "magic": 234001,
                "comment": "Target Price $100 Reached",
                "type_time": mt5.ORDER_TIME_GTC,
            }

            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f'Posicao {position.ticket} fechada por atingir alvo $100 - Lucro: ${position.profit:.2f}')
                return True
            else:
                logger.error(f'Falha ao fechar posicao {position.ticket} por alvo')
                return False
        except Exception as e:
            logger.error(f'Erro ao fechar posicao por alvo {position.ticket}: {e}')
            return False

    def calculate_dynamic_trailing_stop(self, position, greeks_strength):
        """Calcula trailing stop baseado nos 6 setups + greeks"""
        try:
            current_price = mt5.symbol_info_tick("US100").ask if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick("US100").bid
            entry_price = position.price_open
            current_profit = position.profit

            # Base trailing distance
            base_distance = 30  # 30 pontos base

            # Ajustar baseado no lucro atual
            if current_profit > 2.0:  # Lucro > $2
                base_distance = 80
            elif current_profit > 1.0:  # Lucro > $1
                base_distance = 50
            elif current_profit > 0.5:  # Lucro > $0.5
                base_distance = 35

            # Ajustar baseado na força dos greeks e setups
            if greeks_strength > 0.6:  # Greeks muito favoráveis
                base_distance *= 1.3  # Aumentar trailing (mais agressivo)
            elif greeks_strength < 0.3:  # Greeks desfavoráveis
                base_distance *= 0.7  # Diminuir trailing (mais conservador)

            # Ajustar baseado nos setups ativos
            active_setups = sum(1 for setup in self.setups_status.values() if setup['active'])
            if active_setups >= 3:  # Múltiplos setups ativos
                base_distance *= 1.2  # Mais agressivo
            elif active_setups == 0:  # Nenhum setup
                base_distance *= 0.8  # Mais conservador

            return int(base_distance)

        except Exception as e:
            logger.error(f'Erro no calculo do trailing dinamico: {e}')
            return 30  # Valor padrão

    def should_apply_trailing_stop(self, position, trailing_distance):
        """Verifica se deve aplicar trailing stop"""
        try:
            current_price = mt5.symbol_info_tick("US100").ask if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick("US100").bid
            entry_price = position.price_open

            # Calcular distância do preço atual para o preço de entrada
            price_distance = abs(current_price - entry_price) * 10  # Converter para pontos

            # Aplicar trailing se o preço se moveu favoravelmente
            if position.type == mt5.POSITION_TYPE_BUY:
                # Para BUY: se preço subiu mais que a distância do trailing
                return (current_price - entry_price) * 10 > trailing_distance
            else:
                # Para SELL: se preço caiu mais que a distância do trailing
                return (entry_price - current_price) * 10 > trailing_distance

        except Exception as e:
            logger.error(f'Erro na verificacao do trailing: {e}')
            return False

    def check_target_price_reached(self, position):
        """Verifica se preço alvo de $100 foi atingido"""
        try:
            current_price = mt5.symbol_info_tick("US100").ask if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick("US100").bid

            # Para BUY: fechar se preço >= $100
            if position.type == mt5.POSITION_TYPE_BUY:
                return current_price >= self.target_price
            # Para SELL: fechar se preço <= $100 (se short)
            else:
                return current_price <= self.target_price

        except Exception as e:
            logger.error(f'Erro na verificacao do alvo: {e}')
            return False

    def analyze_6_setups_greeks(self):
        """Analisa os 6 setups + gamma, delta e charm para trailing stop"""
        try:
            # Buscar dados de mercado
            symbol_info = mt5.symbol_info("US100")
            if not symbol_info:
                return 0

            current_price = symbol_info.ask
            tick = mt5.symbol_info_tick("US100")

            if not tick:
                return 0

            # Calcular Greeks (simplificado)
            delta = self.calculate_delta(current_price)
            gamma = self.calculate_gamma(current_price)
            charm = self.calculate_charm(current_price)

            # Analisar 6 setups
            setups_strength = self.analyze_6_setups(current_price, tick)

            # Calcular força combinada
            greeks_strength = (gamma * 0.4 + delta * 0.35 + charm * 0.25)
            total_strength = (setups_strength + greeks_strength) / 2

            return total_strength

        except Exception as e:
            logger.error(f'Erro na analise de setups e greeks: {e}')
            return 0

    def calculate_delta(self, price):
        """Calcula Delta (sensibilidade ao preço)"""
        try:
            # Delta simplificado baseado na tendência
            positions = mt5.positions_get(symbol="US100", magic=234001)
            if positions:
                pos = positions[0]
                if pos.type == mt5.POSITION_TYPE_BUY:
                    return min(1.0, (price - pos.price_open) / pos.price_open * 10)
                else:
                    return max(-1.0, (pos.price_open - price) / pos.price_open * 10)
            return 0
        except:
            return 0

    def calculate_gamma(self, price):
        """Calcula Gamma (aceleração do delta)"""
        try:
            # Gamma baseado na volatilidade recente
            rates = mt5.copy_rates_from_pos("US100", mt5.TIMEFRAME_M1, 0, 20)
            if rates is not None and len(rates) >= 10:
                volatility = np.std([rate['close'] for rate in rates[-10:]])
                return min(1.0, volatility / 50)  # Normalizar
            return 0.3  # Valor padrão
        except:
            return 0.3

    def calculate_charm(self, price):
        """Calcula Charm (decaimento do delta no tempo)"""
        try:
            # Charm baseado no tempo de vida da posição
            positions = mt5.positions_get(symbol="US100", magic=234001)
            if positions:
                pos = positions[0]
                position_age = time.time() - pos.time
                # Charm diminui com o tempo (decaimento)
                return max(0.1, 1.0 - (position_age / 3600) * 0.2)  # Decaimento em 1h
            return 0.5
        except:
            return 0.5

    def analyze_6_setups(self, current_price, tick):
        """Analisa os 6 setups para trailing stop"""
        try:
            # Buscar dados históricos para análise
            rates = mt5.copy_rates_from_pos("US100", mt5.TIMEFRAME_M1, 0, 50)
            if rates is None or len(rates) < 20:
                return 0.5

            prices = [rate['close'] for rate in rates]
            volumes = [rate['tick_volume'] for rate in rates]

            strength = 0

            # 1. Bullish Breakout
            if self.setups_status['bullish_breakout']['active']:
                recent_high = max(prices[-10:])
                if current_price > recent_high * 1.001:
                    strength += 0.2

            # 2. Bearish Breakout
            if self.setups_status['bearish_breakout']['active']:
                recent_low = min(prices[-10:])
                if current_price < recent_low * 0.999:
                    strength -= 0.2

            # 3. Pullback Top
            if self.setups_status['pullback_top']['active']:
                ma20 = np.mean(prices[-20:])
                if current_price > ma20 and prices[-1] < prices[-2]:
                    strength += 0.15

            # 4. Pullback Bottom
            if self.setups_status['pullback_bottom']['active']:
                ma20 = np.mean(prices[-20:])
                if current_price < ma20 and prices[-1] > prices[-2]:
                    strength -= 0.15

            # 5. Consolidated Market
            if self.setups_status['consolidated_market']['active']:
                volatility = np.std(prices[-20:])
                avg_volatility = np.mean([np.std(prices[i:i+10]) for i in range(0, len(prices)-10, 5)])
                if volatility < avg_volatility * 0.7:
                    strength += 0.1  # Consolidado é bom para trailing

            # 6. Gamma Negative Protection
            if self.setups_status['gamma_negative_protection']['active']:
                # Proteção quando gamma está negativo (movimento contra)
                gamma = self.calculate_gamma(current_price)
                if gamma < 0.3:  # Gamma baixo indica movimento contra
                    strength -= 0.1

            return max(-1.0, min(1.0, strength))

        except Exception as e:
            logger.error(f'Erro na analise dos 6 setups: {e}')
            return 0

    def calculate_dynamic_trailing_stop(self, position, greeks_strength):
        """Calcula trailing stop baseado nos 6 setups + greeks"""
        try:
            current_price = mt5.symbol_info_tick("US100").ask if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick("US100").bid
            entry_price = position.price_open
            current_profit = position.profit

            # Base trailing distance
            base_distance = 30  # 30 pontos base

            # Ajustar baseado no lucro atual
            if current_profit > 2.0:  # Lucro > $2
                base_distance = 80
            elif current_profit > 1.0:  # Lucro > $1
                base_distance = 50
            elif current_profit > 0.5:  # Lucro > $0.5
                base_distance = 35

            # Ajustar baseado na força dos greeks e setups
            if greeks_strength > 0.6:  # Greeks muito favoráveis
                base_distance *= 1.3  # Aumentar trailing (mais agressivo)
            elif greeks_strength < 0.3:  # Greeks desfavoráveis
                base_distance *= 0.7  # Diminuir trailing (mais conservador)

            # Ajustar baseado nos setups ativos
            active_setups = sum(1 for setup in self.setups_status.values() if setup['active'])
            if active_setups >= 3:  # Múltiplos setups ativos
                base_distance *= 1.2  # Mais agressivo
            elif active_setups == 0:  # Nenhum setup
                base_distance *= 0.8  # Mais conservador

            return int(base_distance)

        except Exception as e:
            logger.error(f'Erro no calculo do trailing dinamico: {e}')
            return 30  # Valor padrão

def emergency_monitor():
    """Monitor de emergência rodando em paralelo"""
    emergency = EmergencyStopLoss()

    while True:
        try:
            emergency.check_and_close_positions()
            time.sleep(2)  # Verificar a cada 2 segundos
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f'Erro no monitor de emergencia: {e}')
            time.sleep(5)

def main():
    """Sistema principal com monitor de emergência integrado"""
    print("=" * 60)
    print("SISTEMA SEGURO LUCRATIVO - 10 AGENTES + EMERGENCIA")
    print("=" * 60)
    print()
    print("Sistema INTELIGENTE - 10 Agentes + 6 Setups + Greeks:")
    print("  - 10 agentes para maxima qualidade")
    print("  - Configuracoes ultra-conservadoras")
    print("  - Sistema de emergencia integrado")
    print("  - Stop loss automatico")
    print("  - Protecao contra perdas excessivas")
    print("  - 6 Setups analisados em tempo real")
    print("  - Greeks (Gamma, Delta, Charm) calculados")
    print("  - Preco alvo $100 configurado")
    print("  - Trailing stop inteligente")
    print()

    # Configuração ultra-conservadora
    config = {
        'name': 'SistemaSeguroLucrativo',
        'symbol': 'US100',
        'magic_number': 234001,
        'lot_size': 0.02  # Lote ainda menor
    }

    # Criar sistema principal
    sistema = SistemaCompletoAgentes(config)

    # Iniciar monitor de emergência em paralelo
    emergency_thread = threading.Thread(target=emergency_monitor, daemon=True)
    emergency_thread.start()

    try:
        logger.info("Iniciando sistema seguro...")
        sistema.start()

        print("Sistema iniciado com sucesso!")
        print("Monitor de emergencia rodando em paralelo")
        print("Monitore o arquivo 'sistema_seguro.log'")
        print()

        # Manter o programa rodando
        while sistema.is_alive():
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupcao detectada")
        print("\nEncerrando sistema...")
    except Exception as e:
        logger.error(f"Erro critico: {e}")
        print(f"\nErro critico: {e}")
    finally:
        sistema.stop()
        sistema.join()
        print("Sistema encerrado")

if __name__ == '__main__':
    main()