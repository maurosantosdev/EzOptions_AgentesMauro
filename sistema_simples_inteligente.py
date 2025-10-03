#!/usr/bin/env python3
"""
SISTEMA SIMPLES INTELIGENTE - 6 SETUPS + GREEKS + 10 AGENTES
Versão simplificada que funciona sem MT5 para análise
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import logging
import numpy as np
from datetime import datetime

# Configurar logging sem emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_simples.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SistemaSimplesInteligente:
    """Sistema inteligente simplificado baseado na estratégia do usuário"""

    def __init__(self):
        # Configurações CONSERVADORAS - confiança ≥ 40%
        self.min_confidence = 40.0
        self.max_positions = 2
        self.lot_size = 0.01

        # Sistema de 6 setups + greeks
        self.setups_config = {
            'bullish_breakout': {'active': False, 'strength': 0},
            'bearish_breakout': {'active': False, 'strength': 0},
            'pullback_top': {'active': False, 'strength': 0},
            'pullback_bottom': {'active': False, 'strength': 0},
            'consolidated_market': {'active': False, 'strength': 0},
            'gamma_protection': {'active': False, 'strength': 0}
        }

        self.greeks_values = {'gamma': 0, 'delta': 0, 'charm': 0}

    def analyze_6_setups_greeks(self):
        """Análise completa dos 6 setups + greeks"""
        # Simular dados de mercado
        current_price = 24900 + np.random.normal(0, 50)

        # Criar dados simulados
        prices = [current_price + np.random.normal(0, 20) for _ in range(50)]
        volumes = [np.random.randint(100, 1000) for _ in range(50)]
        highs = [p + abs(np.random.normal(0, 15)) for p in prices]
        lows = [p - abs(np.random.normal(0, 15)) for p in prices]

        market_data = {
            'current_price': current_price,
            'historical_rates': {
                'close': prices,
                'high': highs,
                'low': lows,
                'tick_volume': volumes
            }
        }

        # Análise dos 6 setups
        setups_results = self.analyze_6_setups(market_data)

        # Cálculo dos greeks
        greeks_results = self.calculate_greeks(market_data)

        # Combinar resultados
        return {
            'setups': setups_results,
            'greeks': greeks_results,
            'current_price': current_price,
            'recommendation': self.generate_recommendation(setups_results, greeks_results)
        }

    def analyze_6_setups(self, market_data):
        """Análise dos 6 setups"""
        results = {}

        try:
            prices = market_data['historical_rates']['close']
            volumes = market_data['historical_rates']['tick_volume']
            highs = market_data['historical_rates']['high']
            lows = market_data['historical_rates']['low']
            current_price = market_data['current_price']

            # 1. Bullish Breakout
            avg_volume = np.mean(volumes[-10:])
            if volumes[-1] > avg_volume * 1.5:
                recent_high = max(highs[-5:])
                if current_price > recent_high * 1.002:
                    results['bullish_breakout'] = {'active': True, 'strength': 0.8}

            # 2. Bearish Breakout
            if volumes[-1] > avg_volume * 1.5:
                recent_low = min(lows[-5:])
                if current_price < recent_low * 0.998:
                    results['bearish_breakout'] = {'active': True, 'strength': 0.8}

            # 3. Pullback Top
            ema20 = np.mean(prices[-20:])
            if current_price < ema20:
                recent_high = max(highs[-10:])
                pullback_pct = (recent_high - current_price) / recent_high * 100
                if 0.3 <= pullback_pct <= 0.7:
                    results['pullback_top'] = {'active': True, 'strength': 0.6}

            # 4. Pullback Bottom
            if current_price > ema20:
                recent_low = min(lows[-10:])
                pullback_pct = (current_price - recent_low) / recent_low * 100
                if 0.3 <= pullback_pct <= 0.7:
                    results['pullback_bottom'] = {'active': True, 'strength': 0.6}

            # 5. Consolidated Market
            volatility = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
            if volatility < 0.15:
                results['consolidated_market'] = {'active': True, 'strength': 0.5}

            # 6. Gamma Protection
            returns = np.diff(prices[-10:]) / prices[-10:-1] * 100
            gamma = np.std(returns)
            if gamma > 0.5:
                results['gamma_protection'] = {'active': True, 'strength': 0.7}

        except Exception as e:
            logger.error(f'Erro na análise dos setups: {e}')

        return results

    def calculate_greeks(self, market_data):
        """Cálculo dos greeks"""
        try:
            prices = market_data['historical_rates']['close']
            current_price = market_data['current_price']

            # Gamma - Volatilidade
            returns = np.diff(prices[-10:]) / prices[-10:-1] * 100
            gamma = np.std(returns)
            gamma = max(-1, min(1, gamma * 10))  # Normalizar

            # Delta - Tendência
            trend = (current_price - prices[-10]) / prices[-10] * 100
            delta = np.tanh(trend / 10)

            # Charm - Tempo
            current_hour = datetime.now().hour
            charm = max(0.1, 1 - (current_hour - 9) / 7)

            return {
                'gamma': gamma,
                'delta': delta,
                'charm': charm
            }

        except Exception as e:
            return {'gamma': 0, 'delta': 0, 'charm': 0}

    def generate_recommendation(self, setups, greeks):
        """Gera recomendação baseada nos setups e greeks"""
        buy_signals = 0
        sell_signals = 0

        # Contar sinais dos setups
        for setup, result in setups.items():
            if result['active']:
                if setup in ['bullish_breakout', 'pullback_bottom', 'consolidated_market']:
                    buy_signals += result['strength']
                elif setup in ['bearish_breakout', 'pullback_top', 'gamma_protection']:
                    sell_signals += result['strength']

        # Considerar greeks
        if greeks['delta'] > 0.6:
            buy_signals += 0.5
        elif greeks['delta'] < -0.6:
            sell_signals += 0.5

        if greeks['gamma'] > 0.7:
            sell_signals += 0.3  # Alta volatilidade = cautela
        elif greeks['gamma'] < -0.7:
            buy_signals += 0.3  # Gamma negativo = oportunidade

        # Decisão final
        if buy_signals > sell_signals * 1.3 and buy_signals >= 1.5:
            return 'BUY'
        elif sell_signals > buy_signals * 1.3 and sell_signals >= 1.5:
            return 'SELL'
        else:
            return 'HOLD'

    def run(self):
        """Loop principal do sistema"""
        logger.info("Sistema Inteligente Iniciado - 6 Setups + Greeks + 10 Agentes")

        while True:
            try:
                # Análise completa
                analysis = self.analyze_6_setups_greeks()

                # Log detalhado
                logger.info("=" * 60)
                logger.info("ANÁLISE INTELIGENTE - 6 SETUPS + GREEKS")
                logger.info("=" * 60)

                # Setups ativos
                active_setups = []
                for setup, result in analysis['setups'].items():
                    if result['active']:
                        active_setups.append(f"{setup}({result['strength']:.2f})")

                logger.info(f"Setups Ativos: {', '.join(active_setups) if active_setups else 'Nenhum'}")
                logger.info(f"Greeks: Gamma={analysis['greeks']['gamma']:.3f}, Delta={analysis['greeks']['delta']:.3f}, Charm={analysis['greeks']['charm']:.3f}")
                logger.info(f"Preço Atual: ${analysis['current_price']:.2f}")
                logger.info(f"Recomendação: {analysis['recommendation']}")

                # Simular operações dos 10 agentes
                self.simulate_10_agents(analysis)

                time.sleep(30)  # Análise a cada 30 segundos

            except KeyboardInterrupt:
                logger.info("Sistema interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no sistema: {e}")
                time.sleep(60)

    def simulate_10_agents(self, analysis):
        """Simula análise de 10 agentes"""
        try:
            # Simular votos dos 10 agentes
            buy_votes = np.random.randint(3, 8)
            sell_votes = np.random.randint(1, 5)
            hold_votes = 10 - buy_votes - sell_votes

            # Ajustar baseado na análise dos setups + greeks
            if analysis['recommendation'] == 'BUY':
                buy_votes += 2
                hold_votes = max(0, hold_votes - 2)
            elif analysis['recommendation'] == 'SELL':
                sell_votes += 2
                hold_votes = max(0, hold_votes - 2)

            # Calcular confiança
            total_votes = buy_votes + sell_votes + hold_votes
            if total_votes > 0:
                confidence = (max(buy_votes, sell_votes) / total_votes) * 100
            else:
                confidence = 0

            logger.info("ANÁLISE DOS 10 AGENTES:")
            logger.info(f"  BUY: {buy_votes} votos")
            logger.info(f"  SELL: {sell_votes} votos")
            logger.info(f"  HOLD: {hold_votes} votos")
            logger.info(f"  Confiança: {confidence:.1f}%")

            # Decisão final
            if confidence >= self.min_confidence:
                if buy_votes > sell_votes:
                    logger.info("DECISÃO FINAL: BUY com alta confiança!")
                elif sell_votes > buy_votes:
                    logger.info("DECISÃO FINAL: SELL com alta confiança!")
            else:
                logger.info("DECISÃO FINAL: HOLD - Confiança insuficiente")

        except Exception as e:
            logger.error(f"Erro na simulação dos agentes: {e}")

def main():
    """Função principal"""
    print("=" * 70)
    print("SISTEMA SIMPLES INTELIGENTE - 6 SETUPS + GREEKS + 10 AGENTES")
    print("=" * 70)
    print()
    print("Funcionalidades:")
    print("  - 6 setups analisados em tempo real")
    print("  - Greeks (Gamma, Delta, Charm) calculados")
    print("  - 10 agentes simulando analise")
    print("  - Sistema de decisao inteligente")
    print("  - Funciona sem MT5")
    print("  - Analise a cada 30 segundos")
    print()

    sistema = SistemaSimplesInteligente()
    sistema.run()

if __name__ == '__main__':
    main()