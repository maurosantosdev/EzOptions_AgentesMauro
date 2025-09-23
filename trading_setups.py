import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class SetupType(Enum):
    BULLISH_BREAKOUT = "bullish_breakout"
    BEARISH_BREAKOUT = "bearish_breakout"
    PULLBACK_TOP = "pullback_top"
    PULLBACK_BOTTOM = "pullback_bottom"
    CONSOLIDATED_MARKET = "consolidated_market"
    GAMMA_NEGATIVE_PROTECTION = "gamma_negative_protection"


@dataclass
class SetupResult:
    setup_type: SetupType
    active: bool
    confidence: float
    details: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    entry_conditions: Dict = None
    risk_level: str = "LOW"


class ConfidenceSystem:
    def __init__(self):
        self.analysis_threshold = 90.0
        self.operation_threshold = 60.0

    def calculate_confidence(self, indicators: Dict) -> float:
        weights = {
            'charm_strength': 0.25,
            'delta_alignment': 0.25,
            'gamma_position': 0.20,
            'price_action_confirmation': 0.15,
            'volume_confirmation': 0.10,
            'vwap_alignment': 0.05
        }

        confidence = 0.0
        for indicator, value in indicators.items():
            if indicator in weights:
                confidence += weights[indicator] * value

        return min(100.0, max(0.0, confidence))

    def can_analyze(self, confidence: float) -> bool:
        return confidence >= self.analysis_threshold

    def can_operate(self, confidence: float) -> bool:
        return confidence >= self.operation_threshold


class TradingSetupAnalyzer:
    def __init__(self):
        self.confidence_system = ConfidenceSystem()

    def analyze_all_setups(self, calls: pd.DataFrame, puts: pd.DataFrame,
                          current_price: float, vwap_data: Dict = None) -> Dict[str, SetupResult]:
        setups = {}

        # Calcular indicadores base
        indicators = self._calculate_base_indicators(calls, puts, current_price, vwap_data)

        # Analisar cada setup
        setups[SetupType.BULLISH_BREAKOUT.value] = self._analyze_bullish_breakout(
            calls, puts, current_price, indicators)
        setups[SetupType.BEARISH_BREAKOUT.value] = self._analyze_bearish_breakout(
            calls, puts, current_price, indicators)
        setups[SetupType.PULLBACK_TOP.value] = self._analyze_pullback_top(
            calls, puts, current_price, indicators)
        setups[SetupType.PULLBACK_BOTTOM.value] = self._analyze_pullback_bottom(
            calls, puts, current_price, indicators)
        setups[SetupType.CONSOLIDATED_MARKET.value] = self._analyze_consolidated_market(
            calls, puts, current_price, indicators)
        setups[SetupType.GAMMA_NEGATIVE_PROTECTION.value] = self._analyze_gamma_protection(
            calls, puts, current_price, indicators)

        return setups

    def _calculate_base_indicators(self, calls: pd.DataFrame, puts: pd.DataFrame,
                                 current_price: float, vwap_data: Dict = None) -> Dict:
        indicators = {}

        # CHARM analysis
        all_options = pd.concat([calls, puts])
        if 'CHARM' in all_options.columns:
            charm_above_mask = all_options['strike'] > current_price
            charm_below_mask = all_options['strike'] < current_price

            charm_above = all_options[charm_above_mask]['CHARM'].sum()
            charm_below = all_options[charm_below_mask]['CHARM'].sum()
            indicators['charm_above'] = float(charm_above) if not pd.isna(charm_above) else 0.0
            indicators['charm_below'] = float(charm_below) if not pd.isna(charm_below) else 0.0
            indicators['charm_net'] = indicators['charm_above'] + indicators['charm_below']
            indicators['charm_direction'] = 1 if indicators['charm_above'] > abs(indicators['charm_below']) else -1

        # DELTA analysis
        if 'DELTA' in all_options.columns:
            delta_above_mask = all_options['strike'] > current_price
            delta_below_mask = all_options['strike'] < current_price

            delta_above = all_options[delta_above_mask]['DELTA'].sum()
            delta_below = all_options[delta_below_mask]['DELTA'].sum()
            indicators['delta_above'] = float(delta_above) if not pd.isna(delta_above) else 0.0
            indicators['delta_below'] = float(delta_below) if not pd.isna(delta_below) else 0.0
            indicators['delta_net'] = indicators['delta_above'] + indicators['delta_below']

        # GAMMA analysis
        if 'GAMMA' in all_options.columns:
            gamma_above_mask = all_options['strike'] > current_price
            gamma_below_mask = all_options['strike'] < current_price

            gamma_above = all_options[gamma_above_mask]['GAMMA'].sum()
            gamma_below = all_options[gamma_below_mask]['GAMMA'].sum()
            indicators['gamma_above'] = float(gamma_above) if not pd.isna(gamma_above) else 0.0
            indicators['gamma_below'] = float(gamma_below) if not pd.isna(gamma_below) else 0.0
            indicators['gamma_net'] = indicators['gamma_above'] + indicators['gamma_below']

            # Find max gamma strikes (with error handling)
            try:
                if len(all_options) > 0:
                    max_gamma_idx = all_options['GAMMA'].idxmax()
                    min_gamma_idx = all_options['GAMMA'].idxmin()

                    # Garantir que temos um índice válido
                    if pd.notna(max_gamma_idx) and max_gamma_idx in all_options.index:
                        max_strike_value = all_options.loc[max_gamma_idx, 'strike']
                        if isinstance(max_strike_value, pd.Series):
                            max_strike_value = max_strike_value.iloc[0]
                        indicators['max_gamma_strike'] = float(max_strike_value)
                    else:
                        indicators['max_gamma_strike'] = current_price * 1.01

                    if pd.notna(min_gamma_idx) and min_gamma_idx in all_options.index:
                        min_strike_value = all_options.loc[min_gamma_idx, 'strike']
                        if isinstance(min_strike_value, pd.Series):
                            min_strike_value = min_strike_value.iloc[0]
                        indicators['min_gamma_strike'] = float(min_strike_value)
                    else:
                        indicators['min_gamma_strike'] = current_price * 0.99
                else:
                    indicators['max_gamma_strike'] = current_price * 1.01
                    indicators['min_gamma_strike'] = current_price * 0.99
            except (ValueError, KeyError, TypeError) as e:
                indicators['max_gamma_strike'] = current_price * 1.01
                indicators['min_gamma_strike'] = current_price * 0.99

        # VWAP analysis
        if vwap_data:
            indicators['vwap'] = vwap_data.get('vwap', current_price)
            indicators['vwap_std1_upper'] = vwap_data.get('std1_upper', current_price)
            indicators['vwap_std1_lower'] = vwap_data.get('std1_lower', current_price)
            indicators['price_vs_vwap'] = (current_price - indicators['vwap']) / indicators['vwap']

        return indicators

    def _analyze_bullish_breakout(self, calls: pd.DataFrame, puts: pd.DataFrame,
                                current_price: float, indicators: Dict) -> SetupResult:
        confidence_factors = {
            'charm_strength': 0,
            'delta_alignment': 0,
            'gamma_position': 0,
            'price_action_confirmation': 0,
            'volume_confirmation': 0,
            'vwap_alignment': 0
        }

        # SETUP 1 - Bullish Breakout: Acima do alvo
        target_strike = indicators.get('max_gamma_strike', current_price * 1.02)

        # Preço operando em CHARM positivo CHARM crescente até o alvo
        if indicators.get('charm_above', 0) > 0 and indicators.get('charm_direction', 0) > 0:
            confidence_factors['charm_strength'] = 85

        # Barra de DELTA positivo até o alvo
        if indicators.get('delta_above', 0) > 0:
            confidence_factors['delta_alignment'] = 80

        # Maior barra de GAMMA acima do preço (preferencialmente no alvo)
        if target_strike > current_price and indicators.get('gamma_above', 0) > 0:
            confidence_factors['gamma_position'] = 90

        # Sem barreiras de GAMMA abaixo do preço
        if indicators.get('gamma_below', 0) <= 0:
            confidence_factors['gamma_position'] += 10

        # Confirmação com Price Action - Rompimento do primeiro desvio da VWAP para cima
        if current_price > indicators.get('vwap_std1_upper', current_price):
            confidence_factors['price_action_confirmation'] = 75

        # VWAP alignment
        if indicators.get('price_vs_vwap', 0) > 0:
            confidence_factors['vwap_alignment'] = 70

        confidence = self.confidence_system.calculate_confidence(confidence_factors)
        active = confidence >= self.confidence_system.operation_threshold

        # Stop Loss - Ativado se o preço voltar abaixo do ponto de virada a estrutura de CHARM
        stop_loss = current_price * 0.995 if active else None

        details = f"Target: {target_strike:.2f}, Confidence: {confidence:.1f}%"
        if confidence >= self.confidence_system.analysis_threshold:
            details += " [ANÁLISE AUTORIZADA]"
        if active:
            details += " [OPERAÇÃO AUTORIZADA]"

        return SetupResult(
            setup_type=SetupType.BULLISH_BREAKOUT,
            active=active,
            confidence=confidence,
            details=details,
            target_price=target_strike if active else None,
            stop_loss=stop_loss,
            entry_conditions=confidence_factors,
            risk_level="MEDIUM" if confidence > 80 else "HIGH"
        )

    def _analyze_bearish_breakout(self, calls: pd.DataFrame, puts: pd.DataFrame,
                                current_price: float, indicators: Dict) -> SetupResult:
        confidence_factors = {
            'charm_strength': 0,
            'delta_alignment': 0,
            'gamma_position': 0,
            'price_action_confirmation': 0,
            'volume_confirmation': 0,
            'vwap_alignment': 0
        }

        # SETUP 2 - Bearish Breakout: Alvo abaixo
        target_strike = indicators.get('min_gamma_strike', current_price * 0.98)

        # Preço operando em CHARM negativo. CHARM decrescente até o alvo
        if indicators.get('charm_below', 0) < 0 and indicators.get('charm_direction', 0) < 0:
            confidence_factors['charm_strength'] = 85

        # Barras de DELTA negativo até o alvo
        if indicators.get('delta_below', 0) < 0:
            confidence_factors['delta_alignment'] = 80

        # Maior barra de GAMMA abaixo do preço (preferencialmente no alvo)
        if target_strike < current_price and indicators.get('gamma_below', 0) < 0:
            confidence_factors['gamma_position'] = 90

        # Sem barreiras do GAMMA acima do preço
        if indicators.get('gamma_above', 0) <= 0:
            confidence_factors['gamma_position'] += 10

        # Confirmação com Price Action - Rompimento do primeiro desvio da VWAP para baixo
        if current_price < indicators.get('vwap_std1_lower', current_price):
            confidence_factors['price_action_confirmation'] = 75

        # VWAP alignment
        if indicators.get('price_vs_vwap', 0) < 0:
            confidence_factors['vwap_alignment'] = 70

        confidence = self.confidence_system.calculate_confidence(confidence_factors)
        active = confidence >= self.confidence_system.operation_threshold

        # Stop Loss - Ativado se o preço voltar acima do ponto de virada ou perder a estrutura de CHARM
        stop_loss = current_price * 1.005 if active else None

        details = f"Target: {target_strike:.2f}, Confidence: {confidence:.1f}%"
        if confidence >= self.confidence_system.analysis_threshold:
            details += " [ANÁLISE AUTORIZADA]"
        if active:
            details += " [OPERAÇÃO AUTORIZADA]"

        return SetupResult(
            setup_type=SetupType.BEARISH_BREAKOUT,
            active=active,
            confidence=confidence,
            details=details,
            target_price=target_strike if active else None,
            stop_loss=stop_loss,
            entry_conditions=confidence_factors,
            risk_level="MEDIUM" if confidence > 80 else "HIGH"
        )

    def _analyze_pullback_top(self, calls: pd.DataFrame, puts: pd.DataFrame,
                            current_price: float, indicators: Dict) -> SetupResult:
        confidence_factors = {
            'charm_strength': 0,
            'delta_alignment': 0,
            'gamma_position': 0,
            'price_action_confirmation': 0,
            'volume_confirmation': 0,
            'vwap_alignment': 0
        }

        # SETUP 3 - Pullback no Topo: Reversão para baixo
        max_gamma_strike = indicators.get('max_gamma_strike', current_price)

        # Preço na maior barra de GAMMA positiva ou área de GAMMA Flip
        gamma_flip_zone = abs(current_price - max_gamma_strike) / current_price < 0.005
        if gamma_flip_zone and indicators.get('gamma_above', 0) > 0:
            confidence_factors['gamma_position'] = 85

        # Maior barra de CHARM positivo antes de barra menor (indica perda de força)
        if indicators.get('charm_above', 0) > 0 and indicators.get('charm_direction', 0) > 0:
            confidence_factors['charm_strength'] = 75

        # Última barra de DELTA positivo atingida (indica esgotamento de demanda)
        if indicators.get('delta_above', 0) > 0:
            confidence_factors['delta_alignment'] = 80

        # Próximo à VWAP superior
        if current_price > indicators.get('vwap', current_price):
            confidence_factors['price_action_confirmation'] = 70

        confidence = self.confidence_system.calculate_confidence(confidence_factors)
        active = confidence >= self.confidence_system.operation_threshold

        # Stop Loss - Ativado se DELTA e CHARM continuarem crescendo acima do nível de entrada
        stop_loss = current_price * 1.01 if active else None

        details = f"Reversal Zone: {max_gamma_strike:.2f}, Confidence: {confidence:.1f}%"
        if confidence >= self.confidence_system.analysis_threshold:
            details += " [ANÁLISE AUTORIZADA]"
        if active:
            details += " [OPERAÇÃO AUTORIZADA]"

        return SetupResult(
            setup_type=SetupType.PULLBACK_TOP,
            active=active,
            confidence=confidence,
            details=details,
            target_price=max_gamma_strike * 0.98 if active else None,
            stop_loss=stop_loss,
            entry_conditions=confidence_factors,
            risk_level="LOW" if confidence > 85 else "MEDIUM"
        )

    def _analyze_pullback_bottom(self, calls: pd.DataFrame, puts: pd.DataFrame,
                               current_price: float, indicators: Dict) -> SetupResult:
        confidence_factors = {
            'charm_strength': 0,
            'delta_alignment': 0,
            'gamma_position': 0,
            'price_action_confirmation': 0,
            'volume_confirmation': 0,
            'vwap_alignment': 0
        }

        # SETUP 4 - Pullback no Fundo: Reversão para cima
        min_gamma_strike = indicators.get('min_gamma_strike', current_price)

        # Preço na maior barra de GAMMA negativo ou área de GAMMA Flip
        gamma_flip_zone = abs(current_price - min_gamma_strike) / current_price < 0.005
        if gamma_flip_zone and indicators.get('gamma_below', 0) < 0:
            confidence_factors['gamma_position'] = 85

        # Maior barra de CHARM negativo antes de barra menor (indica perda de força vendedora)
        if indicators.get('charm_below', 0) < 0 and indicators.get('charm_direction', 0) < 0:
            confidence_factors['charm_strength'] = 75

        # Última barra de DELTA negativo atingida (indica exaustão de oferta)
        if indicators.get('delta_below', 0) < 0:
            confidence_factors['delta_alignment'] = 80

        # Próximo à VWAP inferior
        if current_price < indicators.get('vwap', current_price):
            confidence_factors['price_action_confirmation'] = 70

        confidence = self.confidence_system.calculate_confidence(confidence_factors)
        active = confidence >= self.confidence_system.operation_threshold

        # Stop Loss - Ativado se DELTA e CHARM continuarem crescendo abaixo do nível de entrada
        stop_loss = current_price * 0.99 if active else None

        details = f"Reversal Zone: {min_gamma_strike:.2f}, Confidence: {confidence:.1f}%"
        if confidence >= self.confidence_system.analysis_threshold:
            details += " [ANÁLISE AUTORIZADA]"
        if active:
            details += " [OPERAÇÃO AUTORIZADA]"

        return SetupResult(
            setup_type=SetupType.PULLBACK_BOTTOM,
            active=active,
            confidence=confidence,
            details=details,
            target_price=min_gamma_strike * 1.02 if active else None,
            stop_loss=stop_loss,
            entry_conditions=confidence_factors,
            risk_level="LOW" if confidence > 85 else "MEDIUM"
        )

    def _analyze_consolidated_market(self, calls: pd.DataFrame, puts: pd.DataFrame,
                                  current_price: float, indicators: Dict) -> SetupResult:
        confidence_factors = {
            'charm_strength': 0,
            'delta_alignment': 0,
            'gamma_position': 0,
            'price_action_confirmation': 0,
            'volume_confirmation': 0,
            'vwap_alignment': 0
        }

        # SETUP 5 - Mercado Consolidado (VWAP): Consolidado
        vwap = indicators.get('vwap', current_price)

        # Maior barra de GAMMA posicionada no centro do range (normalmente na VWAP)
        gamma_center_zone = abs(current_price - vwap) / current_price < 0.002
        if gamma_center_zone:
            confidence_factors['gamma_position'] = 80

        # CHARM neutro ou em Flip, sem direção clara
        charm_neutral = abs(indicators.get('charm_net', 0)) < 100
        if charm_neutral:
            confidence_factors['charm_strength'] = 75

        # VWAP e seus desvios formando linhas retas, indicando equilíbrio
        price_vs_vwap = abs(indicators.get('price_vs_vwap', 0))
        if price_vs_vwap < 0.005:
            confidence_factors['price_action_confirmation'] = 85
            confidence_factors['vwap_alignment'] = 90

        # Maior barra de DELTA no centro do range
        if abs(indicators.get('delta_net', 0)) < 50:
            confidence_factors['delta_alignment'] = 70

        confidence = self.confidence_system.calculate_confidence(confidence_factors)
        active = confidence >= self.confidence_system.operation_threshold

        # Stop Loss - Ativado caso haja rompimento claro do range com confirmação do CHARM
        upper_range = vwap * 1.01
        lower_range = vwap * 0.99

        details = f"Range: {lower_range:.2f} - {upper_range:.2f}, Confidence: {confidence:.1f}%"
        if confidence >= self.confidence_system.analysis_threshold:
            details += " [ANÁLISE AUTORIZADA]"
        if active:
            details += " [OPERAÇÃO AUTORIZADA]"

        return SetupResult(
            setup_type=SetupType.CONSOLIDATED_MARKET,
            active=active,
            confidence=confidence,
            details=details,
            target_price=vwap if active else None,
            stop_loss=None,  # Range trading - sem stop loss fixo
            entry_conditions=confidence_factors,
            risk_level="LOW"
        )

    def _analyze_gamma_protection(self, calls: pd.DataFrame, puts: pd.DataFrame,
                                current_price: float, indicators: Dict) -> SetupResult:
        confidence_factors = {
            'charm_strength': 0,
            'delta_alignment': 0,
            'gamma_position': 0,
            'price_action_confirmation': 0,
            'volume_confirmation': 0,
            'vwap_alignment': 0
        }

        # SETUP 6 - Proteção contra GAMMA Negativo
        # Preço operando em GAMMA e DELTA positivo
        current_gamma_positive = indicators.get('gamma_net', 0) > 0
        current_delta_positive = indicators.get('delta_net', 0) > 0

        if current_gamma_positive and current_delta_positive:
            confidence_factors['gamma_position'] = 70
            confidence_factors['delta_alignment'] = 70

        # Maior barra de GAMMA Positivo acima do preço
        if indicators.get('gamma_above', 0) > 0:
            confidence_factors['gamma_position'] += 15

        # Grande barra de GAMMA e DELTA Negativo abaixo do preço (perigo iminente)
        gamma_negative_below = indicators.get('gamma_below', 0) < -1000
        delta_negative_below = indicators.get('delta_below', 0) < -100

        if gamma_negative_below and delta_negative_below:
            confidence_factors['charm_strength'] = 90  # Alto risco = alta necessidade de proteção

        # Proximidade com zona de perigo
        danger_zone_distance = abs(current_price - indicators.get('min_gamma_strike', current_price))
        if danger_zone_distance / current_price < 0.02:  # Muito próximo da zona negativa
            confidence_factors['price_action_confirmation'] = 85

        confidence = self.confidence_system.calculate_confidence(confidence_factors)
        active = confidence >= self.confidence_system.operation_threshold

        # Stop Loss - Ativado caso o preço entre em GAMMA Negativo sem defesa
        danger_level = indicators.get('min_gamma_strike', current_price * 0.98)
        stop_loss = danger_level * 1.005 if active else None

        details = f"Danger Zone: {danger_level:.2f}, Confidence: {confidence:.1f}%"
        if confidence >= self.confidence_system.analysis_threshold:
            details += " [ANÁLISE AUTORIZADA]"
        if active:
            details += " [PROTEÇÃO NECESSÁRIA]"

        return SetupResult(
            setup_type=SetupType.GAMMA_NEGATIVE_PROTECTION,
            active=active,
            confidence=confidence,
            details=details,
            target_price=current_price * 1.005 if active else None,  # Proteção defensiva
            stop_loss=stop_loss,
            entry_conditions=confidence_factors,
            risk_level="HIGH"
        )