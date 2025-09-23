# -*- coding: utf-8 -*-
"""
Sistema de Ordens Inteligentes EzOptions
=======================================

Sistema que executa:
- BUY + BUY LIMIT quando detecta movimento de alta
- SELL + SELL LIMIT quando detecta movimento de baixa
- Cancela ordens opostas automaticamente
- Orders limit com 0.05% de distância
- Análise completa dos 6 setups + GAMMA/DELTA/CHARM
"""

import MetaTrader5 as mt5
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class OrderType(Enum):
    BUY_MARKET = "buy_market"
    BUY_LIMIT = "buy_limit"
    SELL_MARKET = "sell_market"
    SELL_LIMIT = "sell_limit"

class TrendDirection(Enum):
    BULLISH = "BULLISH"    # Vai subir - BUY + BUY LIMIT
    BEARISH = "BEARISH"    # Vai descer - SELL + SELL LIMIT
    NEUTRAL = "NEUTRAL"    # Sem direção clara

class SmartOrderSystem:
    """Sistema de ordens inteligentes que gerencia BUY/SELL + LIMITS automaticamente"""

    def __init__(self, symbol="US100", magic_number=234002, lot_size=0.01):
        self.symbol = symbol
        self.magic_number = magic_number
        self.lot_size = lot_size
        self.limit_distance_pct = 0.002  # 0.2% para orders limit (mais próximo para execução)

        # Rastreamento de ordens ativas
        self.active_buy_orders = []
        self.active_sell_orders = []
        self.last_trend = TrendDirection.NEUTRAL

        # Análise de mercado
        self.current_analysis = {}

    def analyze_complete_market(self, calls_df, puts_df, current_price, vwap_data) -> Dict:
        """Análise COMPLETA dos 6 setups + GAMMA/DELTA/CHARM"""

        analysis = {
            'current_price': current_price,
            'trend_direction': TrendDirection.NEUTRAL,
            'confidence': 0.0,
            'setups_active': [],
            'gamma_analysis': {},
            'delta_analysis': {},
            'charm_analysis': {},
            'should_buy': False,
            'should_sell': False,
            'reasoning': []
        }

        try:
            # 1. ANÁLISE GAMMA
            gamma_analysis = self._analyze_gamma_complete(calls_df, puts_df, current_price)
            analysis['gamma_analysis'] = gamma_analysis

            # 2. ANÁLISE DELTA
            delta_analysis = self._analyze_delta_complete(calls_df, puts_df, current_price)
            analysis['delta_analysis'] = delta_analysis

            # 3. ANÁLISE CHARM
            charm_analysis = self._analyze_charm_complete(calls_df, puts_df, current_price)
            analysis['charm_analysis'] = charm_analysis

            # 4. ANÁLISE VWAP
            vwap_analysis = self._analyze_vwap_complete(current_price, vwap_data)

            # 5. ANÁLISE DOS 6 SETUPS
            setups_analysis = self._analyze_6_setups(gamma_analysis, delta_analysis, charm_analysis, vwap_analysis, current_price)
            analysis['setups_active'] = setups_analysis['active_setups']

            # 6. DECISÃO FINAL INTELIGENTE
            final_decision = self._make_intelligent_decision(gamma_analysis, delta_analysis, charm_analysis, vwap_analysis, setups_analysis)

            analysis['trend_direction'] = final_decision['trend']
            analysis['confidence'] = final_decision['confidence']
            analysis['should_buy'] = final_decision['should_buy']
            analysis['should_sell'] = final_decision['should_sell']
            analysis['reasoning'] = final_decision['reasoning']

            self.current_analysis = analysis
            return analysis

        except Exception as e:
            logger.error(f"[SmartOrder] Erro na análise completa: {e}")
            return analysis

    def _analyze_gamma_complete(self, calls_df, puts_df, current_price) -> Dict:
        """Análise completa do GAMMA"""
        try:
            all_gamma = []
            all_strikes = []

            if not calls_df.empty and 'GAMMA' in calls_df.columns:
                all_gamma.extend(calls_df['GAMMA'].tolist())
                all_strikes.extend(calls_df['strike'].tolist())

            if not puts_df.empty and 'GAMMA' in puts_df.columns:
                all_gamma.extend(puts_df['GAMMA'].tolist())
                all_strikes.extend(puts_df['strike'].tolist())

            if not all_gamma:
                return {'signal': 'NEUTRAL', 'confidence': 0.0, 'reasoning': 'Sem dados GAMMA'}

            # Encontrar maior GAMMA
            max_gamma_idx = np.argmax(np.abs(all_gamma))
            max_gamma_strike = all_strikes[max_gamma_idx]
            max_gamma_value = all_gamma[max_gamma_idx]

            # Analisar posição relativa ao preço
            distance_to_max_gamma = current_price - max_gamma_strike
            distance_pct = abs(distance_to_max_gamma) / current_price

            # Detectar GAMMA negativo perigoso
            negative_gammas = [g for g in all_gamma if g < -100]

            if len(negative_gammas) > 0:
                # SETUP 6: Proteção contra GAMMA Negativo
                if distance_to_max_gamma < 0:  # Preço abaixo do GAMMA positivo
                    return {
                        'signal': 'BULLISH_PROTECTION',
                        'confidence': 0.85,
                        'reasoning': f'GAMMA negativo detectado, preço abaixo do max GAMMA ({max_gamma_strike:.2f}) - COMPRAR para proteção',
                        'max_gamma_strike': max_gamma_strike,
                        'distance_pct': distance_pct
                    }
                else:
                    return {
                        'signal': 'BEARISH_DANGER',
                        'confidence': 0.90,
                        'reasoning': f'GAMMA negativo perigoso, preço acima do max GAMMA - VENDER antes da queda',
                        'max_gamma_strike': max_gamma_strike,
                        'distance_pct': distance_pct
                    }

            # SETUP 5: Mercado Consolidado
            elif distance_pct < 0.002:  # Muito próximo da maior barra GAMMA
                return {
                    'signal': 'CONSOLIDATED',
                    'confidence': 0.75,
                    'reasoning': f'Preço próximo do max GAMMA ({max_gamma_strike:.2f}) - mercado consolidado',
                    'max_gamma_strike': max_gamma_strike,
                    'distance_pct': distance_pct
                }

            # SETUP 1/2: GAMMA como alvo/barreira
            elif distance_to_max_gamma < 0:  # Preço abaixo da maior GAMMA
                return {
                    'signal': 'BULLISH_TARGET',
                    'confidence': 0.80,
                    'reasoning': f'Max GAMMA acima do preço ({max_gamma_strike:.2f}) - alvo de alta, COMPRAR',
                    'max_gamma_strike': max_gamma_strike,
                    'distance_pct': distance_pct
                }
            else:  # Preço acima da maior GAMMA
                return {
                    'signal': 'BEARISH_RESISTANCE',
                    'confidence': 0.80,
                    'reasoning': f'Max GAMMA abaixo do preço ({max_gamma_strike:.2f}) - resistência, VENDER',
                    'max_gamma_strike': max_gamma_strike,
                    'distance_pct': distance_pct
                }

        except Exception as e:
            logger.error(f"[GAMMA Analysis] Erro: {e}")
            return {'signal': 'ERROR', 'confidence': 0.0, 'reasoning': f'Erro na análise GAMMA: {e}'}

    def _analyze_delta_complete(self, calls_df, puts_df, current_price) -> Dict:
        """Análise completa do DELTA"""
        try:
            total_call_delta = calls_df['DELTA'].sum() if not calls_df.empty and 'DELTA' in calls_df.columns else 0
            total_put_delta = puts_df['DELTA'].sum() if not puts_df.empty and 'DELTA' in puts_df.columns else 0
            net_delta = total_call_delta + total_put_delta

            # Analisar força do DELTA
            delta_strength = abs(net_delta)

            # SETUP 3: Pullback no Topo (demanda esgotada)
            if net_delta > 0.6:  # DELTA positivo muito alto
                return {
                    'signal': 'PULLBACK_TOP',
                    'confidence': 0.90,
                    'reasoning': f'DELTA positivo alto ({net_delta:.2f}) - demanda ESGOTADA, VENDER agora!',
                    'net_delta': net_delta,
                    'strength': delta_strength
                }

            # SETUP 4: Pullback no Fundo (oferta esgotada)
            elif net_delta < -0.6:  # DELTA negativo muito alto
                return {
                    'signal': 'PULLBACK_BOTTOM',
                    'confidence': 0.90,
                    'reasoning': f'DELTA negativo alto ({net_delta:.2f}) - oferta ESGOTADA, COMPRAR agora!',
                    'net_delta': net_delta,
                    'strength': delta_strength
                }

            # DELTA equilibrado - consolidação
            elif -0.3 <= net_delta <= 0.3:
                return {
                    'signal': 'BALANCED',
                    'confidence': 0.70,
                    'reasoning': f'DELTA equilibrado ({net_delta:.2f}) - mercado neutro',
                    'net_delta': net_delta,
                    'strength': delta_strength
                }

            # DELTA moderadamente positivo - possível alta
            elif net_delta > 0:
                return {
                    'signal': 'MODERATE_BULLISH',
                    'confidence': 0.60,
                    'reasoning': f'DELTA moderadamente positivo ({net_delta:.2f}) - pressão de compra',
                    'net_delta': net_delta,
                    'strength': delta_strength
                }

            # DELTA moderadamente negativo - possível baixa
            else:
                return {
                    'signal': 'MODERATE_BEARISH',
                    'confidence': 0.60,
                    'reasoning': f'DELTA moderadamente negativo ({net_delta:.2f}) - pressão de venda',
                    'net_delta': net_delta,
                    'strength': delta_strength
                }

        except Exception as e:
            logger.error(f"[DELTA Analysis] Erro: {e}")
            return {'signal': 'ERROR', 'confidence': 0.0, 'reasoning': f'Erro na análise DELTA: {e}'}

    def _analyze_charm_complete(self, calls_df, puts_df, current_price) -> Dict:
        """Análise completa do CHARM"""
        try:
            total_call_charm = calls_df['CHARM'].sum() if not calls_df.empty and 'CHARM' in calls_df.columns else 0
            total_put_charm = puts_df['CHARM'].sum() if not puts_df.empty and 'CHARM' in puts_df.columns else 0
            net_charm = total_call_charm + total_put_charm

            # Simular tendência do CHARM (em produção, usar dados históricos)
            charm_values = [net_charm * (1 + np.random.uniform(-0.1, 0.1)) for _ in range(5)]
            charm_trend = np.mean(np.diff(charm_values)) if len(charm_values) > 1 else 0

            # SETUP 1: Bullish Breakout
            if net_charm > 0.3 and charm_trend > 0.1:
                return {
                    'signal': 'BULLISH_BREAKOUT',
                    'confidence': 0.85,
                    'reasoning': f'CHARM positivo ({net_charm:.2f}) crescente (trend: {charm_trend:.2f}) - BREAKOUT DE ALTA, COMPRAR!',
                    'net_charm': net_charm,
                    'trend': charm_trend
                }

            # SETUP 2: Bearish Breakout
            elif net_charm < -0.3 and charm_trend < -0.1:
                return {
                    'signal': 'BEARISH_BREAKOUT',
                    'confidence': 0.85,
                    'reasoning': f'CHARM negativo ({net_charm:.2f}) decrescente (trend: {charm_trend:.2f}) - BREAKOUT DE BAIXA, VENDER!',
                    'net_charm': net_charm,
                    'trend': charm_trend
                }

            # CHARM neutro mas com tendência
            elif abs(net_charm) <= 0.3:
                if charm_trend > 0.05:
                    return {
                        'signal': 'BUILDING_BULLISH',
                        'confidence': 0.65,
                        'reasoning': f'CHARM neutro ({net_charm:.2f}) mas crescente - força bullish se desenvolvendo',
                        'net_charm': net_charm,
                        'trend': charm_trend
                    }
                elif charm_trend < -0.05:
                    return {
                        'signal': 'BUILDING_BEARISH',
                        'confidence': 0.65,
                        'reasoning': f'CHARM neutro ({net_charm:.2f}) mas decrescente - força bearish se desenvolvendo',
                        'net_charm': net_charm,
                        'trend': charm_trend
                    }
                else:
                    return {
                        'signal': 'NEUTRAL',
                        'confidence': 0.50,
                        'reasoning': f'CHARM neutro ({net_charm:.2f}) sem tendência clara',
                        'net_charm': net_charm,
                        'trend': charm_trend
                    }

            # CHARM forte mas sem tendência clara
            else:
                return {
                    'signal': 'STRONG_BUT_UNCLEAR',
                    'confidence': 0.40,
                    'reasoning': f'CHARM forte ({net_charm:.2f}) mas tendência indefinida',
                    'net_charm': net_charm,
                    'trend': charm_trend
                }

        except Exception as e:
            logger.error(f"[CHARM Analysis] Erro: {e}")
            return {'signal': 'ERROR', 'confidence': 0.0, 'reasoning': f'Erro na análise CHARM: {e}'}

    def _analyze_vwap_complete(self, current_price, vwap_data) -> Dict:
        """Análise completa do VWAP"""
        try:
            vwap = vwap_data.get('vwap', current_price)
            std1_upper = vwap_data.get('std1_upper', current_price * 1.005)
            std1_lower = vwap_data.get('std1_lower', current_price * 0.995)
            std2_upper = vwap_data.get('std2_upper', current_price * 1.01)
            std2_lower = vwap_data.get('std2_lower', current_price * 0.99)

            # Confirmar breakouts e consolidação
            if current_price > std2_upper:
                return {
                    'signal': 'STRONG_BREAKOUT_UP',
                    'confidence': 0.90,
                    'reasoning': f'Preço ({current_price:.2f}) acima do 2º desvio VWAP ({std2_upper:.2f}) - BREAKOUT FORTE DE ALTA',
                    'vwap_position': 'above_std2'
                }
            elif current_price > std1_upper:
                return {
                    'signal': 'BREAKOUT_UP',
                    'confidence': 0.80,
                    'reasoning': f'Preço ({current_price:.2f}) acima do 1º desvio VWAP ({std1_upper:.2f}) - BREAKOUT DE ALTA',
                    'vwap_position': 'above_std1'
                }
            elif current_price < std2_lower:
                return {
                    'signal': 'STRONG_BREAKOUT_DOWN',
                    'confidence': 0.90,
                    'reasoning': f'Preço ({current_price:.2f}) abaixo do 2º desvio VWAP ({std2_lower:.2f}) - BREAKOUT FORTE DE BAIXA',
                    'vwap_position': 'below_std2'
                }
            elif current_price < std1_lower:
                return {
                    'signal': 'BREAKOUT_DOWN',
                    'confidence': 0.80,
                    'reasoning': f'Preço ({current_price:.2f}) abaixo do 1º desvio VWAP ({std1_lower:.2f}) - BREAKOUT DE BAIXA',
                    'vwap_position': 'below_std1'
                }
            else:
                # Dentro dos desvios - consolidação
                distance_from_vwap = abs(current_price - vwap) / vwap
                return {
                    'signal': 'CONSOLIDATED',
                    'confidence': 0.70,
                    'reasoning': f'Preço ({current_price:.2f}) dentro dos desvios VWAP - CONSOLIDAÇÃO',
                    'vwap_position': 'inside_bands',
                    'distance_from_vwap': distance_from_vwap
                }

        except Exception as e:
            logger.error(f"[VWAP Analysis] Erro: {e}")
            return {'signal': 'ERROR', 'confidence': 0.0, 'reasoning': f'Erro na análise VWAP: {e}'}

    def _analyze_6_setups(self, gamma_analysis, delta_analysis, charm_analysis, vwap_analysis, current_price) -> Dict:
        """Identifica quais dos 6 setups estão ativos"""

        active_setups = []

        # SETUP 1: Bullish Breakout
        if (charm_analysis.get('signal') == 'BULLISH_BREAKOUT' and
            vwap_analysis.get('signal') in ['BREAKOUT_UP', 'STRONG_BREAKOUT_UP'] and
            gamma_analysis.get('signal') == 'BULLISH_TARGET'):
            active_setups.append({
                'setup': 'SETUP_1_BULLISH_BREAKOUT',
                'confidence': 0.90,
                'action': 'BUY',
                'reasoning': 'CHARM crescente + VWAP breakout + GAMMA como alvo = COMPRA FORTE'
            })

        # SETUP 2: Bearish Breakout
        elif (charm_analysis.get('signal') == 'BEARISH_BREAKOUT' and
              vwap_analysis.get('signal') in ['BREAKOUT_DOWN', 'STRONG_BREAKOUT_DOWN'] and
              gamma_analysis.get('signal') == 'BEARISH_RESISTANCE'):
            active_setups.append({
                'setup': 'SETUP_2_BEARISH_BREAKOUT',
                'confidence': 0.90,
                'action': 'SELL',
                'reasoning': 'CHARM decrescente + VWAP breakout baixo + GAMMA como resistência = VENDA FORTE'
            })

        # SETUP 3: Pullback no Topo
        elif delta_analysis.get('signal') == 'PULLBACK_TOP':
            active_setups.append({
                'setup': 'SETUP_3_PULLBACK_TOP',
                'confidence': 0.85,
                'action': 'SELL',
                'reasoning': 'DELTA esgotado no topo - demanda acabou, VENDER'
            })

        # SETUP 4: Pullback no Fundo
        elif delta_analysis.get('signal') == 'PULLBACK_BOTTOM':
            active_setups.append({
                'setup': 'SETUP_4_PULLBACK_BOTTOM',
                'confidence': 0.85,
                'action': 'BUY',
                'reasoning': 'DELTA esgotado no fundo - oferta acabou, COMPRAR'
            })

        # SETUP 5: Mercado Consolidado
        elif (gamma_analysis.get('signal') == 'CONSOLIDATED' and
              vwap_analysis.get('signal') == 'CONSOLIDATED' and
              delta_analysis.get('signal') == 'BALANCED'):
            active_setups.append({
                'setup': 'SETUP_5_CONSOLIDATED',
                'confidence': 0.75,
                'action': 'HOLD',
                'reasoning': 'Mercado consolidado - aguardar breakout'
            })

        # SETUP 6: Proteção contra GAMMA Negativo
        elif gamma_analysis.get('signal') in ['BULLISH_PROTECTION', 'BEARISH_DANGER']:
            action = 'BUY' if gamma_analysis.get('signal') == 'BULLISH_PROTECTION' else 'SELL'
            active_setups.append({
                'setup': 'SETUP_6_GAMMA_PROTECTION',
                'confidence': 0.88,
                'action': action,
                'reasoning': gamma_analysis.get('reasoning', 'Proteção contra GAMMA negativo')
            })

        return {'active_setups': active_setups}

    def _make_intelligent_decision(self, gamma_analysis, delta_analysis, charm_analysis, vwap_analysis, setups_analysis) -> Dict:
        """Toma decisão inteligente baseada em todas as análises"""

        reasoning = []
        buy_score = 0.0
        sell_score = 0.0

        # Analisar cada componente
        components = [
            ('GAMMA', gamma_analysis),
            ('DELTA', delta_analysis),
            ('CHARM', charm_analysis),
            ('VWAP', vwap_analysis)
        ]

        for name, analysis in components:
            signal = analysis.get('signal', 'NEUTRAL')
            confidence = analysis.get('confidence', 0.0)

            if signal in ['BULLISH_BREAKOUT', 'BULLISH_TARGET', 'BULLISH_PROTECTION', 'BUILDING_BULLISH',
                         'MODERATE_BULLISH', 'BREAKOUT_UP', 'STRONG_BREAKOUT_UP', 'PULLBACK_BOTTOM']:
                buy_score += confidence
                reasoning.append(f"{name}: {analysis.get('reasoning', signal)}")

            elif signal in ['BEARISH_BREAKOUT', 'BEARISH_RESISTANCE', 'BEARISH_DANGER', 'BUILDING_BEARISH',
                           'MODERATE_BEARISH', 'BREAKOUT_DOWN', 'STRONG_BREAKOUT_DOWN', 'PULLBACK_TOP']:
                sell_score += confidence
                reasoning.append(f"{name}: {analysis.get('reasoning', signal)}")

        # Considerar setups ativos
        for setup_info in setups_analysis.get('active_setups', []):
            if setup_info['action'] == 'BUY':
                buy_score += setup_info['confidence']
                reasoning.append(f"SETUP: {setup_info['reasoning']}")
            elif setup_info['action'] == 'SELL':
                sell_score += setup_info['confidence']
                reasoning.append(f"SETUP: {setup_info['reasoning']}")

        # Decisão final
        if buy_score > sell_score and buy_score > 1.5:  # Threshold para BUY
            return {
                'trend': TrendDirection.BULLISH,
                'confidence': min(buy_score / 4.0, 1.0) * 100,  # Normalizar para %
                'should_buy': True,
                'should_sell': False,
                'reasoning': reasoning
            }
        elif sell_score > buy_score and sell_score > 1.5:  # Threshold para SELL
            return {
                'trend': TrendDirection.BEARISH,
                'confidence': min(sell_score / 4.0, 1.0) * 100,  # Normalizar para %
                'should_buy': False,
                'should_sell': True,
                'reasoning': reasoning
            }
        else:
            return {
                'trend': TrendDirection.NEUTRAL,
                'confidence': 30.0,  # Baixa confiança
                'should_buy': False,
                'should_sell': False,
                'reasoning': ['Sinais conflitantes ou fracos - aguardar']
            }

    def execute_intelligent_orders(self, analysis: Dict) -> bool:
        """Executa ordens inteligentes baseadas na análise"""
        try:
            current_price = analysis['current_price']
            trend = analysis['trend_direction']
            confidence = analysis['confidence']

            # Só operar com confiança >= 60%
            if confidence < 60.0:
                logger.info(f"[SmartOrder] Confiança {confidence:.1f}% < 60% - não operando")
                return False

            # BULLISH: BUY + BUY LIMIT (lógica normal)
            if trend == TrendDirection.BULLISH and analysis['should_buy']:
                logger.info(f"[SmartOrder] BULLISH detectado - EXECUTANDO BUY - Conf: {confidence:.1f}%")

                # 1. Cancelar todas as ordens SELL
                self._cancel_all_sell_orders()

                # 2. Executar BUY Market
                buy_success = self._place_market_order(OrderType.BUY_MARKET, current_price)

                # 3. Colocar BUY LIMIT abaixo
                buy_limit_price = current_price * (1 - self.limit_distance_pct)
                buy_limit_success = self._place_limit_order(OrderType.BUY_LIMIT, buy_limit_price)

                if buy_success or buy_limit_success:
                    logger.info(f"[SmartOrder] ESTRATEGIA BUY executada - Market: {buy_success}, Limit: {buy_limit_success}")
                    return True

            # BEARISH: SELL + SELL LIMIT (lógica normal)
            elif trend == TrendDirection.BEARISH and analysis['should_sell']:
                logger.info(f"[SmartOrder] BEARISH detectado - EXECUTANDO SELL - Conf: {confidence:.1f}%")

                # 1. Cancelar todas as ordens BUY
                self._cancel_all_buy_orders()

                # 2. Executar SELL Market
                sell_success = self._place_market_order(OrderType.SELL_MARKET, current_price)

                # 3. Colocar SELL LIMIT acima
                sell_limit_price = current_price * (1 + self.limit_distance_pct)
                sell_limit_success = self._place_limit_order(OrderType.SELL_LIMIT, sell_limit_price)

                if sell_success or sell_limit_success:
                    logger.info(f"[SmartOrder] ESTRATEGIA SELL executada - Market: {sell_success}, Limit: {sell_limit_success}")
                    return True

            else:
                logger.info(f"[SmartOrder] TENDENCIA NEUTRA - aguardando sinais mais claros")
                return False

        except Exception as e:
            logger.error(f"[SmartOrder] Erro na execução de ordens: {e}")
            return False

    def _cancel_all_buy_orders(self):
        """Cancela todas as ordens BUY ativas"""
        try:
            # Obter ordens ativas
            orders = mt5.orders_get(magic=self.magic_number)
            if not orders:
                return

            buy_orders = [order for order in orders if order.type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT]]

            for order in buy_orders:
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                }
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"[SmartOrder] ❌ Ordem BUY cancelada: {order.ticket}")
                else:
                    logger.warning(f"[SmartOrder] Falha ao cancelar BUY {order.ticket}: {result.comment}")

        except Exception as e:
            logger.error(f"[SmartOrder] Erro ao cancelar ordens BUY: {e}")

    def _cancel_all_sell_orders(self):
        """Cancela todas as ordens SELL ativas"""
        try:
            # Obter ordens ativas
            orders = mt5.orders_get(magic=self.magic_number)
            if not orders:
                return

            sell_orders = [order for order in orders if order.type in [mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL_LIMIT]]

            for order in sell_orders:
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                }
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"[SmartOrder] ❌ Ordem SELL cancelada: {order.ticket}")
                else:
                    logger.warning(f"[SmartOrder] Falha ao cancelar SELL {order.ticket}: {result.comment}")

        except Exception as e:
            logger.error(f"[SmartOrder] Erro ao cancelar ordens SELL: {e}")

    def _place_market_order(self, order_type: OrderType, current_price: float) -> bool:
        """Coloca ordem de mercado"""
        try:
            if order_type == OrderType.BUY_MARKET:
                mt5_order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            else:  # SELL_MARKET
                mt5_order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": mt5_order_type,
                "price": price,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"SmartOrder-{order_type.value}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[SmartOrder] ✅ {order_type.value.upper()} executado: {self.lot_size} @ {price:.2f}")
                return True
            else:
                logger.error(f"[SmartOrder] ❌ Falha {order_type.value}: {result.comment}")
                return False

        except Exception as e:
            logger.error(f"[SmartOrder] Erro na ordem market {order_type.value}: {e}")
            return False

    def _place_limit_order(self, order_type: OrderType, limit_price: float) -> bool:
        """Coloca ordem limite"""
        try:
            if order_type == OrderType.BUY_LIMIT:
                mt5_order_type = mt5.ORDER_TYPE_BUY_LIMIT
            else:  # SELL_LIMIT
                mt5_order_type = mt5.ORDER_TYPE_SELL_LIMIT

            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": mt5_order_type,
                "price": limit_price,
                "magic": self.magic_number,
                "comment": f"SmartOrder-{order_type.value}",
                "type_time": mt5.ORDER_TIME_GTC,
            }

            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[SmartOrder] ✅ {order_type.value.upper()} colocado: {self.lot_size} @ {limit_price:.2f}")
                return True
            else:
                logger.error(f"[SmartOrder] ❌ Falha {order_type.value}: {result.comment}")
                return False

        except Exception as e:
            logger.error(f"[SmartOrder] Erro na ordem limit {order_type.value}: {e}")
            return False

    def get_current_orders_summary(self) -> Dict:
        """Retorna resumo das ordens ativas"""
        try:
            orders = mt5.orders_get(magic=self.magic_number)
            if not orders:
                return {'buy_orders': 0, 'sell_orders': 0, 'total': 0}

            buy_orders = len([o for o in orders if o.type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT]])
            sell_orders = len([o for o in orders if o.type in [mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL_LIMIT]])

            return {
                'buy_orders': buy_orders,
                'sell_orders': sell_orders,
                'total': len(orders),
                'orders': [{'ticket': o.ticket, 'type': o.type, 'price': o.price_open} for o in orders]
            }

        except Exception as e:
            logger.error(f"[SmartOrder] Erro ao obter resumo de ordens: {e}")
            return {'buy_orders': 0, 'sell_orders': 0, 'total': 0}

if __name__ == "__main__":
    # Teste do sistema de ordens inteligentes
    smart_system = SmartOrderSystem()

    # Simular análise
    import pandas as pd

    # Dados simulados
    calls_df = pd.DataFrame({
        'strike': [15200, 15220, 15240, 15260],
        'GAMMA': [150, 200, 180, 120],
        'DELTA': [0.7, 0.5, 0.3, 0.1],
        'CHARM': [0.5, 0.3, 0.1, -0.1]
    })

    puts_df = pd.DataFrame({
        'strike': [15200, 15220, 15240, 15260],
        'GAMMA': [100, 140, 160, 90],
        'DELTA': [-0.3, -0.5, -0.7, -0.9],
        'CHARM': [-0.2, -0.4, -0.6, -0.8]
    })

    vwap_data = {
        'vwap': 15225,
        'std1_upper': 15235,
        'std1_lower': 15215,
        'std2_upper': 15245,
        'std2_lower': 15205
    }

    # Testar análise
    analysis = smart_system.analyze_complete_market(calls_df, puts_df, 15230, vwap_data)

    print(f"Tendência: {analysis['trend_direction'].value}")
    print(f"Confiança: {analysis['confidence']:.1f}%")
    print(f"Deve Comprar: {analysis['should_buy']}")
    print(f"Deve Vender: {analysis['should_sell']}")
    print(f"Setups Ativos: {len(analysis['setups_active'])}")

    for reason in analysis['reasoning']:
        print(f"- {reason}")