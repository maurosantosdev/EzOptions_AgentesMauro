# -*- coding: utf-8 -*-
"""
Sistema Multi-Agente Inteligente EzOptions
==========================================

10 agentes especializados que conversam entre si para tomar decisões de trading
Cada agente analisa um aspecto específico e contribui para a decisão final.
"""

import logging
import threading
import time
import queue
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np
import pandas as pd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_agent_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradingDecision(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class AgentRole(Enum):
    CHARM_ANALYST = "Analista CHARM"
    DELTA_ANALYST = "Analista DELTA"
    GAMMA_ANALYST = "Analista GAMMA"
    VWAP_ANALYST = "Analista VWAP"
    VOLUME_ANALYST = "Analista Volume"
    PRICE_ACTION_ANALYST = "Analista Price Action"
    RISK_MANAGER = "Gerente de Risco"
    SETUP_COORDINATOR = "Coordenador de Setups"
    STRATEGY_OPTIMIZER = "Otimizador de Estrategia"
    DECISION_MAKER = "Tomador de Decisao Final"

@dataclass
class MarketAnalysis:
    charm_data: Dict
    delta_data: Dict
    gamma_data: Dict
    vwap_data: Dict
    volume_data: Dict
    price_data: Dict
    current_price: float
    timestamp: datetime

@dataclass
class AgentMessage:
    sender: AgentRole
    recipient: AgentRole
    message_type: str
    content: Dict
    confidence: float
    timestamp: datetime

@dataclass
class TradingRecommendation:
    decision: TradingDecision
    confidence: float
    setup_type: str
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    reasoning: str
    consensus_level: float

class IntelligentAgent:
    """Agente inteligente especializado em uma area especifica da analise"""

    def __init__(self, role: AgentRole, agent_id: int):
        self.role = role
        self.agent_id = agent_id
        self.name = f"{role.value}-{agent_id:02d}"
        self.message_queue = queue.Queue()
        self.knowledge_base = {}
        self.confidence_threshold = 0.6  # 60% para operacao
        self.analysis_threshold = 0.9    # 90% para analise profunda
        self.profit_target_multiplier = 2.0  # Target 2x maior que stop para maximizar lucro
        self.max_daily_trades = 8  # Maximo trades/dia para aproveitar todas oportunidades
        self.running = True

    def analyze_market(self, market_data: MarketAnalysis) -> Dict:
        """Analisa o mercado baseado na especialidade do agente"""

        if self.role == AgentRole.CHARM_ANALYST:
            return self._analyze_charm(market_data)
        elif self.role == AgentRole.DELTA_ANALYST:
            return self._analyze_delta(market_data)
        elif self.role == AgentRole.GAMMA_ANALYST:
            return self._analyze_gamma(market_data)
        elif self.role == AgentRole.VWAP_ANALYST:
            return self._analyze_vwap(market_data)
        elif self.role == AgentRole.VOLUME_ANALYST:
            return self._analyze_volume(market_data)
        elif self.role == AgentRole.PRICE_ACTION_ANALYST:
            return self._analyze_price_action(market_data)
        elif self.role == AgentRole.RISK_MANAGER:
            return self._analyze_risk(market_data)
        elif self.role == AgentRole.SETUP_COORDINATOR:
            return self._coordinate_setups(market_data)
        elif self.role == AgentRole.STRATEGY_OPTIMIZER:
            return self._optimize_strategy(market_data)
        elif self.role == AgentRole.DECISION_MAKER:
            return self._make_decision(market_data)

    def _analyze_charm(self, data: MarketAnalysis) -> Dict:
        """Analisa CHARM para detectar força/fraqueza direcional"""
        charm_values = data.charm_data.get('values', [])
        if not charm_values:
            return {'confidence': 0, 'signal': 'NEUTRAL', 'reasoning': 'Dados CHARM insuficientes'}

        current_charm = charm_values[-1] if charm_values else 0
        charm_trend = np.mean(np.diff(charm_values[-5:])) if len(charm_values) >= 5 else 0

        # SETUP 1 e 2: CHARM crescente (bullish) ou decrescente (bearish) - MAIS AGRESSIVO PARA SELL
        if charm_trend > 0.3 and current_charm > 0:  # Menos rigoroso para BUY
            confidence = min(0.85, abs(charm_trend) * 0.1 + 0.6)
            signal = 'BULLISH_BREAKOUT'
            reasoning = f"🟢 CHARM positivo ({current_charm:.2f}) e crescente (trend: {charm_trend:.2f})"
        elif charm_trend < -0.2 and current_charm < 0:  # MAIS AGRESSIVO PARA SELL (era -0.5)
            confidence = min(0.95, abs(charm_trend) * 0.15 + 0.8)  # MAIOR confiança para SELL
            signal = 'BEARISH_BREAKOUT'
            reasoning = f"🔴 CHARM negativo ({current_charm:.2f}) e decrescente (trend: {charm_trend:.2f}) - SELL FORTE!"
        else:
            confidence = 0.4
            signal = 'NEUTRAL'
            reasoning = f"CHARM neutro ou sem tendencia clara"

        return {
            'confidence': confidence,
            'signal': signal,
            'reasoning': reasoning,
            'current_charm': current_charm,
            'charm_trend': charm_trend
        }

    def _analyze_delta(self, data: MarketAnalysis) -> Dict:
        """Analisa DELTA para detectar demanda/oferta"""
        delta_values = data.delta_data.get('values', [])
        if not delta_values:
            return {'confidence': 0, 'signal': 'NEUTRAL', 'reasoning': 'Dados DELTA insuficientes'}

        current_delta = delta_values[-1] if delta_values else 0
        delta_strength = abs(current_delta)

        # DETECTAR SETUPS DE DELTA CORRETAMENTE

        # SETUP 3: DELTA positivo alto = Demanda esgotada = SELL
        if current_delta > 0.7:
            confidence = 0.90
            signal = 'PULLBACK_TOP'
            reasoning = f"SETUP 3: DELTA alto ({current_delta:.2f}) - demanda esgotada, PULLBACK TOP"

        # SETUP 4: DELTA negativo alto = Oferta esgotada = BUY
        elif current_delta < -0.7:
            confidence = 0.90
            signal = 'PULLBACK_BOTTOM'
            reasoning = f"SETUP 4: DELTA negativo alto ({current_delta:.2f}) - oferta esgotada, PULLBACK BOTTOM"

        # DELTA moderado = Consolidação
        elif -0.3 <= current_delta <= 0.3:
            confidence = 0.70
            signal = 'CONSOLIDATED'
            reasoning = f"SETUP 5: DELTA equilibrado ({current_delta:.2f}) - mercado consolidado"

        # DELTA moderadamente positivo = Pressão de compra
        elif 0.3 < current_delta <= 0.7:
            confidence = 0.65
            signal = 'BULLISH_TARGET'
            reasoning = f"DELTA moderadamente positivo ({current_delta:.2f}) - pressão de compra"

        # DELTA moderadamente negativo = Pressão de venda
        else:  # -0.7 < current_delta < -0.3
            confidence = 0.65
            signal = 'BEARISH_TARGET'
            reasoning = f"DELTA moderadamente negativo ({current_delta:.2f}) - pressão de venda"

        return {
            'confidence': confidence,
            'signal': signal,
            'reasoning': reasoning,
            'current_delta': current_delta,
            'delta_strength': delta_strength
        }

    def _analyze_gamma(self, data: MarketAnalysis) -> Dict:
        """Analisa GAMMA para detectar pontos de reversao e barreiras"""
        gamma_values = data.gamma_data.get('values', [])
        strikes = data.gamma_data.get('strikes', [])
        current_price = data.current_price

        if not gamma_values or not strikes:
            return {'confidence': 0, 'signal': 'NEUTRAL', 'reasoning': 'Dados GAMMA insuficientes'}

        # Encontrar maior barra de GAMMA
        max_gamma_idx = np.argmax(np.abs(gamma_values))
        max_gamma_strike = strikes[max_gamma_idx]
        max_gamma_value = gamma_values[max_gamma_idx]

        # Analisar posicao relativa ao preco
        price_position = current_price - max_gamma_strike

        # DETECTAR SETUPS DE GAMMA CORRETAMENTE

        # SETUP 6: GAMMA negativo perigoso = Proteção
        negative_gammas = [g for g in gamma_values if g < -100]
        if len(negative_gammas) > 0:
            confidence = 0.90
            signal = 'BEARISH_DANGER'
            reasoning = f"SETUP 6: GAMMA negativo perigoso detectado - proteção necessaria"

        # SETUP 5: Preço próximo da maior GAMMA = Consolidação
        elif abs(price_position) < 10:
            confidence = 0.75
            signal = 'CONSOLIDATED'
            reasoning = f"SETUP 5: Preco proximo da maior GAMMA ({max_gamma_strike:.2f}) - consolidacao"

        # SETUP 1: Preço abaixo da maior GAMMA = Alvo bullish
        elif price_position < -20:
            confidence = 0.80
            signal = 'BULLISH_TARGET'
            reasoning = f"SETUP 1: GAMMA acima do preco - alvo de alta em {max_gamma_strike:.2f}"

        # SETUP 2: Preço muito acima da GAMMA = Resistência bearish
        elif price_position > 20:
            confidence = 0.80
            signal = 'BEARISH_RESISTANCE'
            reasoning = f"SETUP 2: Preco acima da GAMMA - resistencia em {max_gamma_strike:.2f}"

        # Situação neutra
        else:
            confidence = 0.50
            signal = 'NEUTRAL'
            reasoning = f"GAMMA neutro - sem sinal claro"

        return {
            'confidence': confidence,
            'signal': signal,
            'reasoning': reasoning,
            'max_gamma_strike': max_gamma_strike,
            'max_gamma_value': max_gamma_value,
            'price_position': price_position
        }

    def _analyze_vwap(self, data: MarketAnalysis) -> Dict:
        """Analisa VWAP para confirmacao de breakouts e consolidacao"""
        vwap_data = data.vwap_data
        current_price = data.current_price

        vwap = vwap_data.get('vwap', current_price)
        std1_upper = vwap_data.get('std1_upper', current_price * 1.001)
        std1_lower = vwap_data.get('std1_lower', current_price * 0.999)
        std2_upper = vwap_data.get('std2_upper', current_price * 1.002)
        std2_lower = vwap_data.get('std2_lower', current_price * 0.998)

        # Analise da posicao do preco em relacao a VWAP (MAIS AGRESSIVO PARA SELL)
        if current_price > std1_upper:
            if current_price > std2_upper:
                confidence = 0.75  # REDUZIDA confiança para BUY
                signal = 'STRONG_BULLISH'
                reasoning = f"Preco acima do 2o desvio VWAP - bullish mas cuidado com reversao"
            else:
                confidence = 0.65  # REDUZIDA confiança para BUY
                signal = 'BULLISH_BREAKOUT'
                reasoning = f"🟢 Preço acima do 1º desvio VWAP - breakout bullish moderado"
        elif current_price < std1_lower:
            if current_price < std2_lower:
                confidence = 0.95  # MÁXIMA confiança para SELL
                signal = 'STRONG_BEARISH'
                reasoning = f"🔴 Preço abaixo do 2º desvio VWAP - SELL IMEDIATO - breakout bearish FORTE!"
            else:
                confidence = 0.9   # ALTA confiança para SELL
                signal = 'BEARISH_BREAKOUT'
                reasoning = f"🔴 Preço abaixo do 1º desvio VWAP - SELL AGORA - breakout bearish!"
        else:
            # Dentro dos desvios - consolidacao
            vwap_distance = abs(current_price - vwap) / vwap
            if vwap_distance < 0.001:  # Muito proximo da VWAP
                confidence = 0.85
                signal = 'CONSOLIDATED'
                reasoning = f"Preco proximo a VWAP - mercado consolidado"
            else:
                confidence = 0.6
                signal = 'NEUTRAL'
                reasoning = f"Preco dentro dos desvios VWAP - sem direcao clara"

        return {
            'confidence': confidence,
            'signal': signal,
            'reasoning': reasoning,
            'vwap_position': current_price - vwap,
            'vwap_distance_pct': abs(current_price - vwap) / vwap * 100
        }

    def _analyze_volume(self, data: MarketAnalysis) -> Dict:
        """Analisa volume para confirmar movimentos"""
        volume_data = data.volume_data

        current_volume = volume_data.get('current', 1000)
        avg_volume = volume_data.get('average', 1000)
        volume_profile = volume_data.get('profile', {})

        volume_ratio = current_volume / max(avg_volume, 1)

        if volume_ratio > 1.5:
            confidence = 0.85
            signal = 'HIGH_VOLUME'
            reasoning = f"Volume alto ({volume_ratio:.1f}x media) - confirma movimento"
        elif volume_ratio > 1.2:
            confidence = 0.7
            signal = 'ABOVE_AVERAGE'
            reasoning = f"Volume acima da media ({volume_ratio:.1f}x) - suporte ao movimento"
        elif volume_ratio < 0.8:
            confidence = 0.6
            signal = 'LOW_VOLUME'
            reasoning = f"Volume baixo ({volume_ratio:.1f}x media) - movimento fraco"
        else:
            confidence = 0.5
            signal = 'NEUTRAL'
            reasoning = f"Volume normal ({volume_ratio:.1f}x media)"

        return {
            'confidence': confidence,
            'signal': signal,
            'reasoning': reasoning,
            'volume_ratio': volume_ratio
        }

    def _analyze_price_action(self, data: MarketAnalysis) -> Dict:
        """Analisa price action para confirmar padrões"""
        price_data = data.price_data

        recent_prices = price_data.get('recent', [data.current_price])
        if len(recent_prices) < 3:
            return {'confidence': 0.4, 'signal': 'NEUTRAL', 'reasoning': 'Dados price action insuficientes'}

        # Calcular momentum
        momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        volatility = np.std(recent_prices) / np.mean(recent_prices)

        if momentum > 0.003:  # MAIS rigoroso para BUY (era 0.002)
            confidence = min(0.8, 0.6 + abs(momentum) * 40)  # MENOR confiança para BUY
            signal = 'BULLISH_MOMENTUM'
            reasoning = f"🟢 Momentum bullish ({momentum*100:.2f}%) - price action moderado"
        elif momentum < -0.001:  # MUITO mais agressivo para SELL (era -0.002)
            confidence = min(0.95, 0.8 + abs(momentum) * 60)  # MAIOR confiança para SELL
            signal = 'BEARISH_MOMENTUM'
            reasoning = f"🔴 Momentum bearish ({momentum*100:.2f}%) - SELL IMEDIATO - price action bearish!"
        else:
            confidence = 0.5
            signal = 'NEUTRAL'
            reasoning = f"Price action neutro - sem momentum claro"

        return {
            'confidence': confidence,
            'signal': signal,
            'reasoning': reasoning,
            'momentum': momentum,
            'volatility': volatility
        }

    def _analyze_risk(self, data: MarketAnalysis) -> Dict:
        """Analisa risco e define stops/targets"""
        current_price = data.current_price

        # Calcular ATR simulado
        price_data = data.price_data.get('recent', [current_price])
        if len(price_data) > 1:
            atr = np.mean([abs(price_data[i] - price_data[i-1]) for i in range(1, len(price_data))])
        else:
            atr = current_price * 0.001  # 0.1% como fallback

        # Definir niveis otimizados para MAXIMO LUCRO
        stop_distance = atr * 1.5  # 1.5 ATRs para stop (mais apertado = menor risco)
        target_distance = atr * 3.5  # 3.5 ATRs para target (maior lucro potencial = 1:2.3 R/R)

        risk_reward = target_distance / max(stop_distance, 0.001)

        if risk_reward >= 2.0:  # Excelente para lucro
            confidence = 0.95
            signal = 'EXCELLENT_RR'
            reasoning = f"Risk/Reward excelente ({risk_reward:.1f}:1) - ALTA LUCRATIVIDADE"
        elif risk_reward >= 1.5:  # Bom para lucro
            confidence = 0.85
            signal = 'GOOD_RR'
            reasoning = f"Risk/Reward bom ({risk_reward:.1f}:1) - LUCRATIVO"
        elif risk_reward >= 1.2:  # Aceitavel
            confidence = 0.7
            signal = 'ACCEPTABLE_RR'
            reasoning = f"Risk/Reward aceitavel ({risk_reward:.1f}:1)"
        else:  # Baixo potencial de lucro
            confidence = 0.3
            signal = 'POOR_RR'
            reasoning = f"Risk/Reward baixo ({risk_reward:.1f}:1) - EVITAR"

        return {
            'confidence': confidence,
            'signal': signal,
            'reasoning': reasoning,
            'stop_distance': stop_distance,
            'target_distance': target_distance,
            'risk_reward': risk_reward,
            'atr': atr
        }

    def _coordinate_setups(self, data: MarketAnalysis) -> Dict:
        """Coordena e identifica qual setup esta mais provavel"""
        # Este agente recebe informações de outros agentes e coordena
        return {
            'confidence': 0.8,
            'signal': 'COORDINATING',
            'reasoning': 'Coordenando analises dos outros agentes'
        }

    def _optimize_strategy(self, data: MarketAnalysis) -> Dict:
        """Otimiza a estrategia baseada no historico de performance"""
        # Analisar performance passada e sugerir otimizações
        return {
            'confidence': 0.75,
            'signal': 'OPTIMIZING',
            'reasoning': 'Analisando performance e otimizando estrategia'
        }

    def _make_decision(self, data: MarketAnalysis) -> Dict:
        """Toma a decisao final baseada em todos os inputs"""
        # Este agente recebe todos os inputs e toma a decisao final
        return {
            'confidence': 0.8,
            'signal': 'DECIDING',
            'reasoning': 'Processando todas as analises para decisao final'
        }

    def send_message(self, recipient: AgentRole, message_type: str, content: Dict, confidence: float):
        """Envia mensagem para outro agente"""
        message = AgentMessage(
            sender=self.role,
            recipient=recipient,
            message_type=message_type,
            content=content,
            confidence=confidence,
            timestamp=datetime.now()
        )
        return message

    def receive_message(self, message: AgentMessage):
        """Recebe mensagem de outro agente"""
        self.message_queue.put(message)

    def process_messages(self) -> List[Dict]:
        """Processa mensagens recebidas"""
        messages = []
        while not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                messages.append({
                    'sender': message.sender.value,
                    'content': message.content,
                    'confidence': message.confidence
                })
            except queue.Empty:
                break
        return messages

class MultiAgentTradingSystem:
    """Sistema principal que coordena os 10 agentes"""

    def __init__(self):
        self.agents: List[IntelligentAgent] = []
        self.message_bus = queue.Queue()
        self.consensus_threshold = 0.6  # 60% dos agentes devem concordar
        self.analysis_threshold = 0.9   # 90% confianca para analise detalhada
        self.running = False

        # Criar os 10 agentes especializados
        self._create_agents()

        logger.info("[MultiAgent] Sistema com 10 agentes criado com sucesso")

    def _create_agents(self):
        """Cria os 10 agentes especializados"""
        roles = list(AgentRole)
        for i, role in enumerate(roles):
            agent = IntelligentAgent(role, i + 1)
            self.agents.append(agent)
            logger.info(f"[MultiAgent] Agente criado: {agent.name}")

    def analyze_market_collaborative(self, market_data: MarketAnalysis) -> TradingRecommendation:
        """Analise colaborativa entre todos os agentes"""
        logger.info("[MultiAgent] Iniciando analise colaborativa...")

        # Fase 1: Cada agente faz sua analise individual
        agent_analyses = {}
        for agent in self.agents:
            try:
                analysis = agent.analyze_market(market_data)
                agent_analyses[agent.role] = analysis
                logger.info(f"[{agent.name}] Analise: {analysis['signal']} (Conf: {analysis['confidence']:.1f}%)")
            except Exception as e:
                logger.error(f"[{agent.name}] Erro na analise: {e}")
                agent_analyses[agent.role] = {'confidence': 0, 'signal': 'ERROR', 'reasoning': str(e)}

        # Fase 2: Agentes conversam e trocam informações
        self._facilitate_agent_communication(agent_analyses, market_data)

        # Fase 3: Construir consenso
        recommendation = self._build_consensus(agent_analyses, market_data)

        logger.info(f"[MultiAgent] Decisao final: {recommendation.decision.value} (Conf: {recommendation.confidence:.1f}%)")
        return recommendation

    def _facilitate_agent_communication(self, analyses: Dict, market_data: MarketAnalysis):
        """Facilita a comunicacao entre agentes"""
        logger.info("[MultiAgent] Facilitando comunicacao entre agentes...")

        # Agentes especializados compartilham insights
        charm_analysis = analyses.get(AgentRole.CHARM_ANALYST, {})
        delta_analysis = analyses.get(AgentRole.DELTA_ANALYST, {})
        gamma_analysis = analyses.get(AgentRole.GAMMA_ANALYST, {})

        # Coordenador de setups analisa combinações
        if charm_analysis.get('signal') == 'BULLISH_BREAKOUT' and delta_analysis.get('signal') in ['NEUTRAL', 'BULLISH_TARGET']:
            setup_signal = 'SETUP1_BULLISH_BREAKOUT'
            setup_confidence = (charm_analysis.get('confidence', 0) + delta_analysis.get('confidence', 0)) / 2
        elif charm_analysis.get('signal') == 'BEARISH_BREAKOUT' and delta_analysis.get('signal') in ['NEUTRAL', 'BEARISH_TARGET']:
            setup_signal = 'SETUP2_BEARISH_BREAKOUT'
            setup_confidence = (charm_analysis.get('confidence', 0) + delta_analysis.get('confidence', 0)) / 2
        elif delta_analysis.get('signal') == 'PULLBACK_TOP':
            setup_signal = 'SETUP3_PULLBACK_TOP'
            setup_confidence = delta_analysis.get('confidence', 0)
        elif delta_analysis.get('signal') == 'PULLBACK_BOTTOM':
            setup_signal = 'SETUP4_PULLBACK_BOTTOM'
            setup_confidence = delta_analysis.get('confidence', 0)
        elif gamma_analysis.get('signal') == 'CONSOLIDATED':
            setup_signal = 'SETUP5_CONSOLIDATED'
            setup_confidence = gamma_analysis.get('confidence', 0)
        elif gamma_analysis.get('signal') == 'GAMMA_PROTECTION':
            setup_signal = 'SETUP6_GAMMA_PROTECTION'
            setup_confidence = gamma_analysis.get('confidence', 0)
        else:
            setup_signal = 'NO_CLEAR_SETUP'
            setup_confidence = 0.3

        # Atualizar analise do coordenador
        analyses[AgentRole.SETUP_COORDINATOR] = {
            'confidence': setup_confidence,
            'signal': setup_signal,
            'reasoning': f'Setup identificado baseado na analise colaborativa'
        }

        logger.info(f"[Coordenador] Setup identificado: {setup_signal} (Conf: {setup_confidence:.1f}%)")

    def _build_consensus(self, analyses: Dict, market_data: MarketAnalysis) -> TradingRecommendation:
        """Constroi consenso entre os agentes para decisao final"""

        # Coletar votos dos agentes
        buy_votes = []
        sell_votes = []
        hold_votes = []

        setup_type = analyses.get(AgentRole.SETUP_COORDINATOR, {}).get('signal', 'NO_SETUP')

        # Mapear sinais para decisões de trading (PRIORIZAR SELL PARA PARAR PREJUÍZO)
        for role, analysis in analyses.items():
            signal = analysis.get('signal', 'NEUTRAL')
            confidence = analysis.get('confidence', 0)

            # DETECTAR 6 SETUPS CORRETAMENTE

            # SETUP 1: BULLISH BREAKOUT
            if signal in ['BULLISH_BREAKOUT', 'SETUP1_BULLISH_BREAKOUT', 'BREAKOUT_UP', 'STRONG_BREAKOUT_UP']:
                buy_votes.append((role.value, confidence))
                logger.info(f"[SETUP 1 - BULLISH BREAKOUT] {role.value}: {signal} -> Detectando alta forte")

            # SETUP 2: BEARISH BREAKOUT
            elif signal in ['BEARISH_BREAKOUT', 'SETUP2_BEARISH_BREAKOUT', 'BREAKOUT_DOWN', 'STRONG_BREAKOUT_DOWN']:
                sell_votes.append((role.value, confidence))
                logger.info(f"[SETUP 2 - BEARISH BREAKOUT] {role.value}: {signal} -> Detectando baixa forte")

            # SETUP 3: PULLBACK TOP (demanda esgotada = SELL)
            elif signal in ['PULLBACK_TOP', 'SETUP3_PULLBACK_TOP', 'BEARISH_RESISTANCE']:
                sell_votes.append((role.value, confidence))
                logger.info(f"[SETUP 3 - PULLBACK TOP] {role.value}: {signal} -> Demanda esgotada, SELL")

            # SETUP 4: PULLBACK BOTTOM (oferta esgotada = BUY)
            elif signal in ['PULLBACK_BOTTOM', 'SETUP4_PULLBACK_BOTTOM', 'BULLISH_TARGET']:
                buy_votes.append((role.value, confidence))
                logger.info(f"[SETUP 4 - PULLBACK BOTTOM] {role.value}: {signal} -> Oferta esgotada, BUY")

            # SETUP 5: CONSOLIDACAO (aguardar breakout)
            elif signal in ['CONSOLIDATED', 'SETUP5_CONSOLIDATED', 'SIDEWAYS']:
                hold_votes.append((role.value, confidence))
                logger.info(f"[SETUP 5 - CONSOLIDACAO] {role.value}: {signal} -> Aguardando breakout")

            # SETUP 6: PROTECAO GAMMA (detectar perigo)
            elif signal in ['GAMMA_PROTECTION', 'SETUP6_GAMMA_PROTECTION', 'BEARISH_DANGER', 'BULLISH_PROTECTION']:
                # GAMMA protection pode ser BUY ou SELL dependendo da direção
                if 'BEARISH' in signal or 'DANGER' in signal:
                    sell_votes.append((role.value, confidence))
                    logger.info(f"[SETUP 6 - GAMMA PROTECTION] {role.value}: {signal} -> Proteção bearish, SELL")
                else:
                    buy_votes.append((role.value, confidence))
                    logger.info(f"[SETUP 6 - GAMMA PROTECTION] {role.value}: {signal} -> Proteção bullish, BUY")

            # SINAIS NEUTROS = HOLD
            elif signal in ['NEUTRAL', 'UNCLEAR', 'WEAK_SIGNAL']:
                hold_votes.append((role.value, confidence))
                logger.info(f"[NEUTRO] {role.value}: {signal} -> Aguardando sinal mais claro")

            # OUTROS SINAIS = Classificar baseado no contexto
            else:
                if 'BULLISH' in signal or 'UP' in signal or 'HIGH' in signal:
                    buy_votes.append((role.value, confidence * 0.8))
                    logger.info(f"[BUY CONTEXTO] {role.value}: {signal} -> Sinal bullish")
                elif 'BEARISH' in signal or 'DOWN' in signal or 'LOW' in signal:
                    sell_votes.append((role.value, confidence * 0.8))
                    logger.info(f"[SELL CONTEXTO] {role.value}: {signal} -> Sinal bearish")
                else:
                    hold_votes.append((role.value, confidence * 0.5))
                    logger.info(f"[HOLD CONTEXTO] {role.value}: {signal} -> Sinal indefinido")


        # Calcular consenso
        total_agents = len(analyses)
        buy_strength = sum(conf for _, conf in buy_votes)
        sell_strength = sum(conf for _, conf in sell_votes)
        hold_strength = sum(conf for _, conf in hold_votes)

        # LOGICA NORMAL - DETECTANDO CORRETAMENTE OS 6 SETUPS

        # SELL quando agentes detectam sinais bearish
        if len(sell_votes) >= 2 and sell_strength > buy_strength * 0.8:
            decision = TradingDecision.SELL
            confidence = min(sell_strength / len(sell_votes) * 100, 95)
            consensus_level = len(sell_votes) / total_agents
            logger.info(f"[6 SETUPS] SELL executado - Setup detectado com {len(sell_votes)} votos, Forca: {sell_strength:.1f}")

        # BUY quando agentes detectam sinais bullish claros
        elif len(buy_votes) >= 3 and buy_strength > sell_strength * 1.2:
            decision = TradingDecision.BUY
            confidence = min(buy_strength / len(buy_votes) * 100, 95)
            consensus_level = len(buy_votes) / total_agents
            logger.info(f"[6 SETUPS] BUY executado - Setup detectado com {len(buy_votes)} votos, Forca: {buy_strength:.1f}")

        # HOLD quando não há consenso claro nos setups
        else:
            decision = TradingDecision.HOLD
            confidence = max(hold_strength / max(len(hold_votes), 1) * 50, 20)
            consensus_level = len(hold_votes) / total_agents
            logger.info(f"[6 SETUPS] HOLD - Aguardando setup claro - BUY: {len(buy_votes)}, SELL: {len(sell_votes)}")

        # Definir precos baseado na analise de risco
        risk_analysis = analyses.get(AgentRole.RISK_MANAGER, {})
        current_price = market_data.current_price
        stop_distance = risk_analysis.get('stop_distance', current_price * 0.01)
        target_distance = risk_analysis.get('target_distance', current_price * 0.015)

        if decision == TradingDecision.BUY:
            entry_price = current_price
            stop_loss = current_price - stop_distance
            take_profit = current_price + target_distance
            reasoning = f"Consenso COMPRA: {len(buy_votes)} agentes (força: {buy_strength:.1f})"
        elif decision == TradingDecision.SELL:
            entry_price = current_price
            stop_loss = current_price + stop_distance
            take_profit = current_price - target_distance
            reasoning = f"Consenso VENDA: {len(sell_votes)} agentes (força: {sell_strength:.1f})"
        else:
            entry_price = current_price
            stop_loss = current_price
            take_profit = current_price
            reasoning = f"Consenso AGUARDAR: Sem sinal claro ou confiança insuficiente"

        risk_reward = abs(take_profit - entry_price) / max(abs(stop_loss - entry_price), 0.001)

        recommendation = TradingRecommendation(
            decision=decision,
            confidence=confidence,
            setup_type=setup_type,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward,
            reasoning=reasoning,
            consensus_level=consensus_level
        )

        # Log detalhado da decisao
        logger.info(f"[Consenso] BUY: {len(buy_votes)} votos (força: {buy_strength:.1f})")
        logger.info(f"[Consenso] SELL: {len(sell_votes)} votos (força: {sell_strength:.1f})")
        logger.info(f"[Consenso] HOLD: {len(hold_votes)} votos (força: {hold_strength:.1f})")
        logger.info(f"[Decisao Final] {decision.value} - Setup: {setup_type} - R/R: {risk_reward:.1f}")

        return recommendation

    def get_agent_status(self) -> Dict:
        """Retorna status de todos os agentes"""
        status = {}
        for agent in self.agents:
            status[agent.role.value] = {
                'name': agent.name,
                'running': agent.running,
                'confidence_threshold': agent.confidence_threshold,
                'analysis_threshold': agent.analysis_threshold
            }
        return status

if __name__ == "__main__":
    # Teste do sistema multi-agente
    system = MultiAgentTradingSystem()

    # Criar dados de mercado simulados
    market_data = MarketAnalysis(
        charm_data={'values': [0.5, 0.7, 0.9, 1.2]},
        delta_data={'values': [0.3, 0.4, 0.6, 0.8]},
        gamma_data={'values': [100, 150, 200, 120], 'strikes': [15200, 15250, 15300, 15350]},
        vwap_data={'vwap': 15250, 'std1_upper': 15260, 'std1_lower': 15240},
        volume_data={'current': 1500, 'average': 1000},
        price_data={'recent': [15240, 15245, 15252, 15255]},
        current_price=15255.0,
        timestamp=datetime.now()
    )

    # Analisar colaborativamente
    recommendation = system.analyze_market_collaborative(market_data)

    print(f"\nRecomendacao Final:")
    print(f"Decisao: {recommendation.decision.value}")
    print(f"Confiança: {recommendation.confidence:.1f}%")
    print(f"Setup: {recommendation.setup_type}")
    print(f"Entrada: {recommendation.entry_price:.2f}")
    print(f"Stop: {recommendation.stop_loss:.2f}")
    print(f"Alvo: {recommendation.take_profit:.2f}")
    print(f"R/R: {recommendation.risk_reward:.1f}")
    print(f"Consenso: {recommendation.consensus_level:.1f}%")
    print(f"Reasoning: {recommendation.reasoning}")