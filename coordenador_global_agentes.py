"""
COORDENADOR GLOBAL DE AGENTES
Sistema que permite comunicação entre TODOS os agentes para decisões coletivas
"""

import threading
import time
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DecisionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class AgentType(Enum):
    LUCRO_FINAL = "LUCRO_FINAL"
    AGENTES_REAL = "AGENTES_REAL"
    EMERGENCIA = "EMERGENCIA"
    MULTI_AGENT = "MULTI_AGENT"
    SMART_ORDER = "SMART_ORDER"
    PREVISAO = "PREVISAO"

@dataclass
class AgentOpinion:
    """Opinião de um agente sobre uma decisão"""
    agent_type: AgentType
    decision: DecisionType
    confidence: float
    reasoning: str
    timestamp: datetime
    market_data: Dict[str, Any]

@dataclass
class CollectiveDecision:
    """Decisão coletiva de todos os agentes"""
    final_decision: DecisionType
    confidence: float
    consensus_level: float  # Percentual de concordância
    opinions: List[AgentOpinion]
    reasoning: List[str]
    timestamp: datetime

class GlobalCoordinator(threading.Thread):
    """Coordenador global que permite comunicação entre todos os agentes"""

    def __init__(self):
        super().__init__()
        self.name = "GlobalCoordinator"
        self.running = False

        # Registro de agentes ativos
        self.active_agents = {}
        self.agent_opinions = {}

        # Histórico de decisões
        self.decision_history = []

        # Configurações de consenso
        self.min_consensus_threshold = 0.6  # 60% de concordância mínima
        self.min_confidence_threshold = 70.0  # Confiança mínima para decisão

        # Lock para thread safety
        self.lock = threading.Lock()

    def register_agent(self, agent_type: AgentType, agent_instance):
        """Registra um agente no coordenador global"""
        with self.lock:
            self.active_agents[agent_type] = {
                'instance': agent_instance,
                'last_seen': datetime.now(),
                'status': 'ACTIVE'
            }
            logger.info(f"[{self.name}] Agente registrado: {agent_type.value}")

    def unregister_agent(self, agent_type: AgentType):
        """Remove agente do coordenador"""
        with self.lock:
            if agent_type in self.active_agents:
                del self.active_agents[agent_type]
                logger.info(f"[{self.name}] Agente removido: {agent_type.value}")

    def request_opinions(self, market_data: Dict[str, Any], context: str) -> List[AgentOpinion]:
        """Solicita opiniões de todos os agentes sobre uma situação de mercado"""
        logger.info(f"[{self.name}] === SOLICITANDO OPINIÕES COLETIVAS ===")
        logger.info(f"[{self.name}] Contexto: {context}")

        opinions = []

        with self.lock:
            for agent_type, agent_info in self.active_agents.items():
                try:
                    agent = agent_info['instance']

                    # Solicitar opinião baseada no tipo de agente
                    opinion = self._get_agent_opinion(agent, agent_type, market_data, context)

                    if opinion:
                        opinions.append(opinion)
                        logger.info(f"[{self.name}] Opinião {agent_type.value}: {opinion.decision.value} ({opinion.confidence:.1f}%)")

                except Exception as e:
                    logger.error(f"[{self.name}] Erro ao obter opinião de {agent_type.value}: {e}")

        logger.info(f"[{self.name}] Opiniões coletadas: {len(opinions)}/{len(self.active_agents)}")
        return opinions

    def _get_agent_opinion(self, agent, agent_type: AgentType, market_data: Dict[str, Any], context: str) -> AgentOpinion:
        """Obtém opinião específica de cada tipo de agente"""
        try:
            if agent_type == AgentType.LUCRO_FINAL:
                # Sistema de Lucro Final
                analysis = agent.analyze_market_simple()
                if analysis and analysis.get('action') != 'HOLD':
                    return AgentOpinion(
                        agent_type=agent_type,
                        decision=DecisionType.BUY if analysis['action'] == 'BUY' else DecisionType.SELL,
                        confidence=analysis.get('confidence', 0),
                        reasoning=f"Análise: {analysis.get('trend', 'NEUTRAL')}, Volume: {analysis.get('volume_strength', 0):.2f}x",
                        timestamp=datetime.now(),
                        market_data=market_data
                    )

            elif agent_type == AgentType.AGENTES_REAL:
                # Sistema de Agentes Real (Multi-Agente)
                if hasattr(agent, 'multi_agent_system') and agent.multi_agent_system:
                    try:
                        # Criar dados de mercado para análise
                        from multi_agent_system import MarketAnalysis
                        market_data_obj = MarketAnalysis(
                            charm_data=market_data.get('charm_data', {}),
                            delta_data=market_data.get('delta_data', {}),
                            gamma_data=market_data.get('gamma_data', {}),
                            vwap_data=market_data.get('vwap_data', {}),
                            volume_data=market_data.get('volume_data', {}),
                            price_data=market_data.get('price_data', {}),
                            current_price=market_data.get('current_price', 0),
                            timestamp=datetime.now()
                        )

                        recommendation = agent.multi_agent_system.analyze_market_collaborative(market_data_obj)

                        if recommendation and recommendation.confidence >= 30:
                            decision_map = {
                                'BUY': DecisionType.BUY,
                                'SELL': DecisionType.SELL,
                                'HOLD': DecisionType.HOLD
                            }

                            return AgentOpinion(
                                agent_type=agent_type,
                                decision=decision_map.get(recommendation.decision.value, DecisionType.HOLD),
                                confidence=recommendation.confidence,
                                reasoning=f"Multi-Agente: {recommendation.setup_type}",
                                timestamp=datetime.now(),
                                market_data=market_data
                            )
                    except Exception as e:
                        logger.error(f"[{self.name}] Erro na análise multi-agente: {e}")

            elif agent_type == AgentType.EMERGENCIA:
                # Sistema de Emergência
                if hasattr(agent, 'is_market_open') and agent.is_market_open():
                    return AgentOpinion(
                        agent_type=agent_type,
                        decision=DecisionType.HOLD,  # Emergência não decide direção, apenas segurança
                        confidence=90.0,
                        reasoning="Sistema de emergência: Mercado ativo e seguro",
                        timestamp=datetime.now(),
                        market_data=market_data
                    )
                else:
                    return AgentOpinion(
                        agent_type=agent_type,
                        decision=DecisionType.HOLD,
                        confidence=100.0,
                        reasoning="Sistema de emergência: Mercado fechado ou perigoso",
                        timestamp=datetime.now(),
                        market_data=market_data
                    )

            elif agent_type == AgentType.SMART_ORDER:
                # Sistema de Ordens Inteligentes
                if hasattr(agent, 'analyze_complete_market'):
                    try:
                        analysis = agent.analyze_complete_market(
                            calls_df=market_data.get('calls_df'),
                            puts_df=market_data.get('puts_df'),
                            current_price=market_data.get('current_price', 0),
                            vwap_data=market_data.get('vwap_data', {})
                        )

                        if analysis and analysis.get('confidence', 0) >= 40:
                            return AgentOpinion(
                                agent_type=agent_type,
                                decision=DecisionType.BUY if analysis['trend_direction'].value == 'BUY' else DecisionType.SELL,
                                confidence=analysis.get('confidence', 0),
                                reasoning=f"SmartOrder: {analysis['trend_direction'].value}",
                                timestamp=datetime.now(),
                                market_data=market_data
                            )
                    except Exception as e:
                        logger.error(f"[{self.name}] Erro na análise SmartOrder: {e}")

            elif agent_type == AgentType.PREVISAO:
                # Sistema de Previsão
                if hasattr(agent, 'predict_setup_direction'):
                    try:
                        predicted_direction, confidence, reasons = agent.predict_setup_direction(
                            type('MarketData', (), market_data)(),
                            market_data.get('current_price', 0)
                        )

                        if confidence >= 30:
                            decision_map = {'buy': DecisionType.BUY, 'sell': DecisionType.SELL}
                            return AgentOpinion(
                                agent_type=agent_type,
                                decision=decision_map.get(predicted_direction, DecisionType.HOLD),
                                confidence=confidence,
                                reasoning=f"Previsão: {predicted_direction} - {'; '.join(reasons[:2])}",
                                timestamp=datetime.now(),
                                market_data=market_data
                            )
                    except Exception as e:
                        logger.error(f"[{self.name}] Erro na previsão: {e}")

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao obter opinião de {agent_type.value}: {e}")

        return None

    def make_collective_decision(self, opinions: List[AgentOpinion]) -> CollectiveDecision:
        """Toma decisão coletiva baseada nas opiniões de todos os agentes"""
        if not opinions:
            return CollectiveDecision(
                final_decision=DecisionType.HOLD,
                confidence=0.0,
                consensus_level=0.0,
                opinions=[],
                reasoning=["Nenhuma opinião coletada"],
                timestamp=datetime.now()
            )

        # Contar votos por decisão
        decision_votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        total_confidence = {'BUY': 0, 'SELL': 0, 'HOLD': 0}

        for opinion in opinions:
            decision_votes[opinion.decision.value] += 1
            total_confidence[opinion.decision.value] += opinion.confidence

        # Calcular decisão majoritária
        max_votes = max(decision_votes.values())
        total_votes = len(opinions)

        if max_votes == 0:
            final_decision = DecisionType.HOLD
            consensus_level = 0.0
            avg_confidence = 0.0
        else:
            # Encontrar decisão com mais votos
            if decision_votes['BUY'] == max_votes:
                final_decision = DecisionType.BUY
            elif decision_votes['SELL'] == max_votes:
                final_decision = DecisionType.SELL
            else:
                final_decision = DecisionType.HOLD

            consensus_level = max_votes / total_votes
            avg_confidence = total_confidence[final_decision.value] / max_votes if max_votes > 0 else 0

        # Gerar explicação da decisão
        reasoning = []
        for opinion in opinions:
            reasoning.append(f"{opinion.agent_type.value}: {opinion.decision.value} ({opinion.confidence:.1f}%) - {opinion.reasoning}")

        # Aplicar pesos baseados na confiança histórica de cada agente
        final_confidence = self._apply_confidence_weights(avg_confidence, opinions)

        decision = CollectiveDecision(
            final_decision=final_decision,
            confidence=final_confidence,
            consensus_level=consensus_level,
            opinions=opinions,
            reasoning=reasoning,
            timestamp=datetime.now()
        )

        # Log da decisão coletiva
        logger.info(f"[{self.name}] === DECISÃO COLETIVA TOMADA ===")
        logger.info(f"[{self.name}] Decisão Final: {decision.final_decision.value}")
        logger.info(f"[{self.name}] Confiança: {decision.confidence:.1f}%")
        logger.info(f"[{self.name}] Consenso: {decision.consensus_level:.1%}")
        logger.info(f"[{self.name}] Votos - BUY: {decision_votes['BUY']}, SELL: {decision_votes['SELL']}, HOLD: {decision_votes['HOLD']}")

        # Salvar no histórico
        self.decision_history.append(decision)

        return decision

    def _apply_confidence_weights(self, base_confidence: float, opinions: List[AgentOpinion]) -> float:
        """Aplica pesos de confiança baseados no histórico de cada agente"""
        # Por enquanto, retorna a confiança base
        # Futuramente pode usar histórico de acertos/errores de cada agente
        return min(100.0, base_confidence * 1.1)  # Boost de 10% para decisão coletiva

    def should_execute_trade(self, decision: CollectiveDecision) -> bool:
        """Determina se deve executar trade baseado na decisão coletiva"""
        # Verificar consenso mínimo
        if decision.consensus_level < self.min_consensus_threshold:
            logger.warning(f"[{self.name}] Consenso insuficiente: {decision.consensus_level:.1%} < {self.min_consensus_threshold:.1%}")
            return False

        # Verificar confiança mínima
        if decision.confidence < self.min_confidence_threshold:
            logger.warning(f"[{self.name}] Confiança insuficiente: {decision.confidence:.1f}% < {self.min_confidence_threshold}%")
            return False

        # Verificar se há opiniões suficientes
        if len(decision.opinions) < 2:
            logger.warning(f"[{self.name}] Poucas opiniões: {len(decision.opinions)} < 2")
            return False

        return True

    def run(self):
        """Loop principal do coordenador"""
        logger.info(f"[{self.name}] === COORDENADOR GLOBAL INICIADO ===")
        logger.info(f"[{self.name}] Sistema de comunicação entre agentes ATIVO")
        logger.info(f"[{self.name}] Thresholds: Consenso {self.min_consensus_threshold:.1%}, Confiança {self.min_confidence_threshold}%")

        self.running = True

        while self.running:
            try:
                # Manter agentes registrados ativos
                self._update_agent_status()

                # Aguardar solicitações de coordenação
                time.sleep(1)

            except Exception as e:
                logger.error(f"[{self.name}] Erro no loop principal: {e}")
                time.sleep(5)

    def _update_agent_status(self):
        """Atualiza status dos agentes registrados"""
        with self.lock:
            current_time = datetime.now()
            for agent_type, agent_info in self.active_agents.items():
                last_seen = agent_info['last_seen']
                if (current_time - last_seen).seconds > 30:  # 30 segundos de timeout
                    agent_info['status'] = 'TIMEOUT'
                    logger.warning(f"[{self.name}] Agente {agent_type.value} timeout")
                else:
                    agent_info['last_seen'] = current_time

    def stop(self):
        """Para o coordenador"""
        logger.info(f"[{self.name}] === COORDENADOR GLOBAL PARANDO ===")
        self.running = False

        with self.lock:
            logger.info(f"[{self.name}] Agentes ativos no momento da parada:")
            for agent_type in self.active_agents:
                logger.info(f"[{self.name}] - {agent_type.value}")

            logger.info(f"[{self.name}] Total de decisões no histórico: {len(self.decision_history)}")

# Instância global do coordenador
global_coordinator = GlobalCoordinator()

def get_coordinator():
    """Retorna instância do coordenador global"""
    return global_coordinator

def register_agent_in_coordinator(agent_type: AgentType, agent_instance):
    """Registra agente no coordenador global"""
    global_coordinator.register_agent(agent_type, agent_instance)

def unregister_agent_from_coordinator(agent_type: AgentType):
    """Remove agente do coordenador global"""
    global_coordinator.unregister_agent(agent_type)

def request_collective_decision(market_data: Dict[str, Any], context: str = "General Market Analysis"):
    """Solicita decisão coletiva de todos os agentes"""
    opinions = global_coordinator.request_opinions(market_data, context)
    decision = global_coordinator.make_collective_decision(opinions)
    return decision

if __name__ == "__main__":
    # Teste do coordenador
    global_coordinator.start()

    try:
        # Simular alguns dados de mercado
        test_market_data = {
            'current_price': 24625.00,
            'charm_data': {'values': [25.0, 30.0, 35.0]},
            'delta_data': {'values': [0.5, 0.6, 0.7]},
            'gamma_data': {'values': [150.0, 160.0, 170.0]},
            'vwap_data': {'vwap': 24620.00},
            'volume_data': {'current': 1000, 'average': 800},
            'price_data': {'recent': [24620.00, 24625.00, 24630.00]}
        }

        # Solicitar decisão coletiva
        decision = request_collective_decision(test_market_data, "Teste de Coordenação")

        logger.info(f"Decisão coletiva: {decision.final_decision.value} ({decision.confidence:.1f}%)")

    except KeyboardInterrupt:
        logger.info("Interrupção detectada")
    finally:
        global_coordinator.stop()
        global_coordinator.join()