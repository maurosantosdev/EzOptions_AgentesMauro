"""
SISTEMA DE COORDENAÇÃO DE AGENTES
Implementa comunicação entre TODOS os agentes para decisões coletivas
"""

import threading
import time
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass

# Importar o coordenador global
from coordenador_global_agentes import (
    get_coordinator, register_agent_in_coordinator,
    unregister_agent_from_coordinator, request_collective_decision,
    AgentType, DecisionType, AgentOpinion, CollectiveDecision
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CoordinatedTradingSystem(threading.Thread):
    """Sistema de trading que coordena TODOS os agentes"""

    def __init__(self, config):
        super().__init__()
        self.name = config.get('name', 'CoordinatedTradingSystem')
        self.symbol = config.get('symbol', 'US100')
        self.running = False

        # Estado do sistema
        self.market_data = {}
        self.last_decision = None
        self.coordinator = get_coordinator()

        # Registros de performance
        self.decision_history = []
        self.performance_metrics = {
            'total_decisions': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'accuracy_rate': 0.0
        }

        logger.info(f"[{self.name}] Sistema de Coordenação de Agentes Iniciado")
        logger.info(f"[{self.name}] Coordenador Global: {len(self.coordinator.active_agents)} agentes registrados")

    def run(self):
        """Loop principal do sistema coordenado"""
        logger.info(f"[{self.name}] === SISTEMA COORDENADO INICIADO ===")
        logger.info(f"[{self.name}] 🤖 14 Agentes trabalhando em conjunto")
        logger.info(f"[{self.name}] 📡 Sistema de comunicação ATIVO")
        logger.info(f"[{self.name}] 🎯 Decisões por consenso implementado")

        self.running = True

        while self.running:
            try:
                # Coletar dados de mercado
                self._update_market_data()

                # Solicitar decisão coletiva de TODOS os agentes
                decision = self._request_collective_decision()

                if decision:
                    self._process_collective_decision(decision)

                # Aguardar próximo ciclo
                time.sleep(30)  # 30 segundos entre análises

            except Exception as e:
                logger.error(f"[{self.name}] Erro no loop principal: {e}")
                time.sleep(60)  # Aguardar mais tempo em caso de erro

    def _update_market_data(self):
        """Atualiza dados de mercado de todas as fontes"""
        try:
            # Simular coleta de dados de mercado
            # Em um sistema real, isso viria de diferentes fontes
            self.market_data = {
                'current_price': 24625.00,
                'timestamp': datetime.now(),
                'volume': 1000,
                'spread': 0.25,
                'source': 'COORDINATED_SYSTEM'
            }

            logger.debug(f"[{self.name}] Dados de mercado atualizados: {self.market_data['current_price']}")

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao atualizar dados de mercado: {e}")

    def _request_collective_decision(self) -> CollectiveDecision:
        """Solicita decisão coletiva de todos os agentes"""
        try:
            logger.info(f"[{self.name}] 📡 Solicitando decisão coletiva de {len(self.coordinator.active_agents)} agentes")

            # Preparar dados para os agentes
            market_context = {
                'current_price': self.market_data.get('current_price', 0),
                'volume': self.market_data.get('volume', 0),
                'spread': self.market_data.get('spread', 0),
                'timestamp': self.market_data.get('timestamp'),
                'context': 'COORDINATED_MARKET_ANALYSIS'
            }

            # Solicitar decisão coletiva
            decision = request_collective_decision(market_context, "Coordinated Market Analysis")

            if decision:
                logger.info(f"[{self.name}] 🎯 Decisão coletiva recebida: {decision.final_decision.value}")
                logger.info(f"[{self.name}] 📊 Confiança: {decision.confidence:.1f}% | Consenso: {decision.consensus_level:.1%}")
                logger.info(f"[{self.name}] 👥 Opiniões: {len(decision.opinions)} agentes participaram")

                # Log detalhado das opiniões
                for opinion in decision.opinions:
                    logger.info(f"[{self.name}]   - {opinion.agent_type.value}: {opinion.decision.value} ({opinion.confidence:.1f}%)")

                return decision
            else:
                logger.warning(f"[{self.name}] Nenhuma decisão coletiva obtida")
                return None

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao solicitar decisão coletiva: {e}")
            return None

    def _process_collective_decision(self, decision: CollectiveDecision):
        """Processa decisão coletiva e executa ações"""
        try:
            # Verificar se deve executar trade
            if self._should_execute_trade(decision):
                logger.info(f"[{self.name}] ✅ EXECUTANDO DECISÃO COLETIVA")
                logger.info(f"[{self.name}] 🎯 Ação: {decision.final_decision.value}")
                logger.info(f"[{self.name}] 📊 Confiança: {decision.confidence:.1f}%")

                # Executar trade baseado na decisão coletiva
                success = self._execute_collective_trade(decision)

                if success:
                    self._record_successful_decision(decision)
                    logger.info(f"[{self.name}] ✅ Trade coletivo executado com sucesso")
                else:
                    self._record_failed_decision(decision)
                    logger.error(f"[{self.name}] ❌ Falha na execução do trade coletivo")

                self.last_decision = decision
            else:
                logger.info(f"[{self.name}] ⏸️  Aguardando melhores condições para decisão coletiva")
                logger.info(f"[{self.name}] 📊 Confiança atual: {decision.confidence:.1f}% (mínimo: 70.0%)")

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao processar decisão coletiva: {e}")

    def _should_execute_trade(self, decision: CollectiveDecision) -> bool:
        """Determina se deve executar trade baseado na decisão coletiva"""
        try:
            # Verificar consenso mínimo (60%)
            if decision.consensus_level < 0.6:
                logger.warning(f"[{self.name}] Consenso insuficiente: {decision.consensus_level:.1%}")
                return False

            # Verificar confiança mínima (70%)
            if decision.confidence < 70.0:
                logger.warning(f"[{self.name}] Confiança insuficiente: {decision.confidence:.1f}%")
                return False

            # Verificar se há opiniões suficientes (pelo menos 3 agentes)
            if len(decision.opinions) < 3:
                logger.warning(f"[{self.name}] Poucas opiniões: {len(decision.opinions)} < 3")
                return False

            # Verificar se não é HOLD
            if decision.final_decision == DecisionType.HOLD:
                logger.info(f"[{self.name}] Decisão coletiva: AGUARDAR")
                return False

            return True

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao verificar se deve executar trade: {e}")
            return False

    def _execute_collective_trade(self, decision: CollectiveDecision) -> bool:
        """Executa trade baseado na decisão coletiva"""
        try:
            logger.info(f"[{self.name}] 🚀 EXECUTANDO TRADE COLETIVO")
            logger.info(f"[{self.name}] 📈 Direção: {decision.final_decision.value}")
            logger.info(f"[{self.name}] 🎯 Preço: {self.market_data.get('current_price', 0)}")

            # Simular execução de trade
            # Em um sistema real, isso executaria a ordem no MT5

            # Calcular parâmetros baseados na decisão coletiva
            entry_price = self.market_data.get('current_price', 0)
            confidence = decision.confidence

            # Ajustar volume baseado na confiança coletiva
            base_volume = 0.02
            if confidence >= 90:
                volume = base_volume * 1.5  # 150% do volume para alta confiança
            elif confidence >= 80:
                volume = base_volume  # Volume normal
            else:
                volume = base_volume * 0.5  # 50% do volume para confiança média

            logger.info(f"[{self.name}] 📊 Volume ajustado: {volume} (baseado em confiança {confidence:.1f}%)")

            # Simular execução bem-sucedida
            # Em produção, isso seria:
            # success = self.execute_order(decision.final_decision.value, volume, entry_price)

            success = True  # Simulação

            if success:
                logger.info(f"[{self.name}] ✅ ORDEM COLETIVA EXECUTADA COM SUCESSO")
                logger.info(f"[{self.name}] 🎯 {decision.final_decision.value} {volume} @ {entry_price}")

            return success

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao executar trade coletivo: {e}")
            return False

    def _record_successful_decision(self, decision: CollectiveDecision):
        """Registra decisão bem-sucedida"""
        self.performance_metrics['total_decisions'] += 1
        self.performance_metrics['successful_trades'] += 1

        # Recalcular taxa de acerto
        total = self.performance_metrics['total_decisions']
        successful = self.performance_metrics['successful_trades']
        self.performance_metrics['accuracy_rate'] = (successful / total) * 100 if total > 0 else 0

        logger.info(f"[{self.name}] 📈 Performance: {self.performance_metrics['accuracy_rate']:.1f}% acurácia")

    def _record_failed_decision(self, decision: CollectiveDecision):
        """Registra decisão falhada"""
        self.performance_metrics['total_decisions'] += 1
        self.performance_metrics['failed_trades'] += 1

        # Recalcular taxa de acerto
        total = self.performance_metrics['total_decisions']
        successful = self.performance_metrics['successful_trades']
        self.performance_metrics['accuracy_rate'] = (successful / total) * 100 if total > 0 else 0

        logger.warning(f"[{self.name}] 📉 Performance: {self.performance_metrics['accuracy_rate']:.1f}% acurácia")

    def get_status(self):
        """Retorna status atual do sistema coordenado"""
        return {
            'running': self.running,
            'active_agents': len(self.coordinator.active_agents),
            'last_decision': self.last_decision.final_decision.value if self.last_decision else 'NONE',
            'performance': self.performance_metrics,
            'market_data': self.market_data
        }

    def stop(self):
        """Para o sistema coordenado"""
        logger.info(f"[{self.name}] === SISTEMA COORDENADO PARANDO ===")
        self.running = False

        # Log final de performance
        perf = self.performance_metrics
        logger.info(f"[{self.name}] 📊 Performance Final:")
        logger.info(f"[{self.name}]   Total de decisões: {perf['total_decisions']}")
        logger.info(f"[{self.name}]   Trades bem-sucedidos: {perf['successful_trades']}")
        logger.info(f"[{self.name}]   Trades falhados: {perf['failed_trades']}")
        logger.info(f"[{self.name}]   Taxa de acerto: {perf['accuracy_rate']:.1f}%")

def main():
    """Função principal para teste do sistema coordenado"""
    logger.info("🚀 SISTEMA DE COORDENAÇÃO DE AGENTES")
    logger.info("🤖 14 Agentes trabalhando em conjunto")
    logger.info("📡 Comunicação entre agentes ATIVA")

    # Criar sistema coordenado
    config = {
        'name': 'CoordinatedTradingSystem',
        'symbol': 'US100'
    }

    coordinated_system = CoordinatedTradingSystem(config)

    try:
        # Iniciar sistema
        coordinated_system.start()

        # Manter rodando
        while True:
            time.sleep(60)

            # Mostrar status a cada minuto
            status = coordinated_system.get_status()
            logger.info(f"Status: {status['active_agents']} agentes ativos | "
                       f"Última decisão: {status['last_decision']} | "
                       f"Acurácia: {status['performance']['accuracy_rate']:.1f}%")

    except KeyboardInterrupt:
        logger.info("🛑 Interrupção detectada pelo usuário")
    except Exception as e:
        logger.error(f"💥 Erro crítico: {e}")
    finally:
        coordinated_system.stop()
        coordinated_system.join()
        logger.info("👋 Sistema coordenado finalizado")

if __name__ == "__main__":
    main()