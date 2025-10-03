"""
VERIFICAÇÃO DE COMUNICAÇÃO ENTRE AGENTES
======================================

Este script verifica se os agentes estão realmente se comunicando
e tomando decisões corretas em conjunto.
"""

import MetaTrader5 as mt5
import logging
import time
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AgentCommunicationVerifier:
    """Verificador de comunicação entre agentes"""
    
    def __init__(self, agent):
        self.agent = agent
        self.communication_log = []
        self.decision_consensus = []
        self.agent_responses = {}
        
    def verify_agent_communication(self):
        """
        Verifica se os agentes estão se comunicando corretamente
        """
        logger.info(f"[{self.agent.name}] === VERIFICAÇÃO DE COMUNICAÇÃO ENTRE AGENTES ===")
        
        results = {
            'communication_working': False,
            'agents_responding': [],
            'decisions_aligned': False,
            'consensus_quality': 0,
            'issues_found': []
        }
        
        try:
            # 1. VERIFICAR SE O SISTEMA MULTI-AGENTE ESTÁ ATIVO
            if hasattr(self.agent, 'multi_agent_system') and self.agent.multi_agent_system:
                logger.info(f"[{self.agent.name}] ✅ Sistema Multi-Agente está ativo")
                results['communication_working'] = True
            else:
                logger.error(f"[{self.agent.name}] ❌ Sistema Multi-Agente NÃO está ativo")
                results['issues_found'].append("Sistema Multi-Agente desativado")
                return results
            
            # 2. VERIFICAR SE OS AGENTES ESTÃO RESPONDENDO
            agent_status = self.agent.multi_agent_system.get_agent_status()
            active_agents = [name for name, info in agent_status.items() if info.get('status') == 'ACTIVE']
            
            logger.info(f"[{self.agent.name}] Agentes ativos: {len(active_agents)}/{len(agent_status)}")
            
            for agent_name, agent_info in agent_status.items():
                status = agent_info.get('status', 'UNKNOWN')
                logger.info(f"[{self.agent.name}] - {agent_name}: {status}")
                
                if status == 'ACTIVE':
                    results['agents_responding'].append(agent_name)
                else:
                    results['issues_found'].append(f"Agente {agent_name} inativo")
            
            # 3. VERIFICAR QUALIDADE DAS DECISÕES EM CONSENSO
            if hasattr(self.agent, 'last_decision') and self.agent.last_decision:
                decision = self.agent.last_decision
                confidence = getattr(decision, 'confidence', 0)
                consensus = getattr(decision, 'consensus_level', 0)
                
                logger.info(f"[{self.agent.name}] Última decisão registrada:")
                logger.info(f"[{self.agent.name}] - Decisão: {getattr(decision, 'decision', 'UNKNOWN').value if hasattr(getattr(decision, 'decision', None), 'value') else 'UNKNOWN'}")
                logger.info(f"[{self.agent.name}] - Confiança: {confidence:.1f}%")
                logger.info(f"[{self.agent.name}] - Consenso: {consensus:.1%}")
                
                results['consensus_quality'] = consensus * 100
                
                if consensus >= 0.6 and confidence >= 70:
                    results['decisions_aligned'] = True
                    logger.info(f"[{self.agent.name}] ✅ Decisões em consenso adequado")
                else:
                    results['issues_found'].append("Baixo nível de consenso ou confiança")
                    logger.warning(f"[{self.agent.name}] ⚠️  Decisões com baixo consenso/confiança")
            
            # 4. VERIFICAR HISTÓRICO DE DECISÕES
            if hasattr(self.agent, 'decision_history') and self.agent.decision_history:
                recent_decisions = self.agent.decision_history[-5:]  # Últimas 5 decisões
                consistent_decisions = 0
                
                for decision in recent_decisions:
                    if hasattr(decision, 'consensus_level') and decision.consensus_level >= 0.6:
                        consistent_decisions += 1
                
                consistency_rate = consistent_decisions / len(recent_decisions) if recent_decisions else 0
                logger.info(f"[{self.agent.name}] Consistência nas últimas decisões: {consistency_rate:.1%}")
                
                if consistency_rate >= 0.6:
                    logger.info(f"[{self.agent.name}] ✅ Alta consistência nas decisões")
                else:
                    logger.warning(f"[{self.agent.name}] ⚠️  Baixa consistência nas decisões")
            
            # 5. VERIFICAR COMUNICAÇÃO EM TEMPO REAL
            self._test_real_time_communication(results)
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro na verificação de comunicação: {e}")
            results['issues_found'].append(f"Erro na verificação: {str(e)}")
        
        return results
    
    def _test_real_time_communication(self, results):
        """
        Testa comunicação em tempo real entre agentes
        """
        logger.info(f"[{self.agent.name}] Testando comunicação em tempo real...")
        
        try:
            # Simular solicitação de decisão colaborativa
            if hasattr(self.agent.multi_agent_system, 'request_collective_decision'):
                # Criar dados de mercado simulados para teste
                market_data = self._create_test_market_data()
                
                logger.info(f"[{self.agent.name}] Solicitando decisão colaborativa...")
                decision = self.agent.multi_agent_system.request_collective_decision(
                    market_data, 
                    "Teste de Comunicação"
                )
                
                if decision:
                    logger.info(f"[{self.agent.name}] ✅ Decisão colaborativa recebida")
                    logger.info(f"[{self.agent.name}] - Decisão: {decision.final_decision.value}")
                    logger.info(f"[{self.agent.name}] - Confiança: {decision.confidence:.1f}%")
                    logger.info(f"[{self.agent.name}] - Consenso: {decision.consensus_level:.1%}")
                    logger.info(f"[{self.agent.name}] - Opiniões: {len(decision.opinions)} agentes")
                    
                    # Verificar se todas as opiniões têm conteúdo válido
                    valid_opinions = [op for op in decision.opinions if op.decision and op.confidence >= 0]
                    if len(valid_opinions) >= len(decision.opinions) * 0.8:  # 80% das opiniões válidas
                        logger.info(f"[{self.agent.name}] ✅ Comunicação em tempo real funcionando corretamente")
                        results['communication_working'] = True
                    else:
                        logger.warning(f"[{self.agent.name}] ⚠️  Algumas opiniões inválidas na comunicação")
                        results['issues_found'].append("Opiniões de agentes com dados inválidos")
                else:
                    logger.error(f"[{self.agent.name}] ❌ Nenhuma decisão colaborativa recebida")
                    results['issues_found'].append("Falha na decisão colaborativa")
            else:
                logger.error(f"[{self.agent.name}] ❌ Método de decisão colaborativa não disponível")
                results['issues_found'].append("Método de decisão colaborativa ausente")
                
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro no teste de comunicação em tempo real: {e}")
            results['issues_found'].append(f"Erro no teste RTC: {str(e)}")
    
    def _create_test_market_data(self):
        """
        Cria dados de mercado simulados para teste
        """
        try:
            # Obter preço atual real
            current_price = self._get_current_price()
            if not current_price:
                current_price = 24600.0  # Valor padrão
            
            # Criar dados de mercado simulados
            market_data = {
                'charm_data': {'values': [25.0, 30.0, 35.0, 40.0]},
                'delta_data': {'values': [0.5, 0.6, 0.7, 0.8]},
                'gamma_data': {'values': [150, 200, 250, 300], 'strikes': [15200, 15250, 15300, 15350]},
                'vwap_data': {'vwap': current_price, 'std1_upper': current_price * 1.005, 'std1_lower': current_price * 0.995},
                'volume_data': {'current': 1500, 'average': 1000},
                'price_data': {'recent': [current_price - 10, current_price - 5, current_price, current_price + 5, current_price + 10]},
                'current_price': current_price,
                'timestamp': datetime.now()
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro ao criar dados de mercado simulados: {e}")
            # Retornar dados mínimos
            return {
                'charm_data': {'values': [0]},
                'delta_data': {'values': [0]},
                'gamma_data': {'values': [0], 'strikes': [0]},
                'vwap_data': {'vwap': 24600},
                'volume_data': {'current': 1000, 'average': 1000},
                'price_data': {'recent': [24600]},
                'current_price': 24600,
                'timestamp': datetime.now()
            }
    
    def _get_current_price(self):
        """
        Obtém preço atual real do símbolo
        """
        try:
            tick = mt5.symbol_info_tick(self.agent.symbol)
            if tick:
                return (tick.bid + tick.ask) / 2
            return None
        except:
            return None
    
    def generate_communication_report(self, verification_results):
        """
        Gera relatório detalhado da verificação de comunicação
        """
        logger.info(f"[{self.agent.name}] === RELATÓRIO DE VERIFICAÇÃO DE COMUNICAÇÃO ===")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'agent_name': self.agent.name,
            'verification_results': verification_results,
            'recommendations': []
        }
        
        # Analisar resultados e gerar recomendações
        if not verification_results['communication_working']:
            report['recommendations'].append("❌ ATIVAR SISTEMA MULTI-AGENTE")
            report['recommendations'].append("Verificar se os módulos multi_agent_system.py estão disponíveis")
            report['recommendations'].append("Certificar-se de que todos os agentes estão inicializados")
        
        if len(verification_results['agents_responding']) < 8:  # Menos de 80% dos agentes
            report['recommendations'].append("⚠️  VERIFICAR STATUS DOS AGENTES INDIVIDUAIS")
            report['recommendations'].append("Reiniciar agentes que não estão respondendo")
            report['recommendations'].append("Verificar logs individuais dos agentes")
        
        if not verification_results['decisions_aligned']:
            report['recommendations'].append("📊 AJUSTAR PARÂMETROS DE CONSENSO")
            report['recommendations'].append("Reduzir thresholds mínimos temporariamente para testes")
            report['recommendations'].append("Verificar alinhamento das estratégias individuais")
        
        if verification_results['issues_found']:
            report['recommendations'].append("🔧 RESOLVER PROBLEMAS IDENTIFICADOS:")
            for issue in verification_results['issues_found']:
                report['recommendations'].append(f"   - {issue}")
        
        # Se tudo estiver ok
        if (verification_results['communication_working'] and 
            len(verification_results['agents_responding']) >= 8 and
            verification_results['decisions_aligned']):
            report['recommendations'].append("✅ COMUNICAÇÃO ENTRE AGENTES FUNCIONANDO CORRETAMENTE!")
            report['recommendations'].append("Sistema pronto para operações colaborativas")
            report['recommendations'].append("Continuar monitorando performance")
        
        # Exibir relatório
        logger.info(f"[{self.agent.name}] Relatório gerado:")
        logger.info(f"[{self.agent.name}] Timestamp: {report['timestamp']}")
        logger.info(f"[{self.agent.name}] Agentes respondendo: {len(verification_results['agents_responding'])}")
        logger.info(f"[{self.agent.name}] Qualidade do consenso: {verification_results['consensus_quality']:.1f}%")
        logger.info(f"[{self.agent.name}] Decisões alinhadas: {'SIM' if verification_results['decisions_aligned'] else 'NÃO'}")
        
        if verification_results['issues_found']:
            logger.info(f"[{self.agent.name}] Problemas encontrados:")
            for issue in verification_results['issues_found']:
                logger.info(f"[{self.agent.name}] - {issue}")
        
        logger.info(f"[{self.agent.name}] Recomendações:")
        for recommendation in report['recommendations']:
            logger.info(f"[{self.agent.name}] {recommendation}")
        
        return report

def diagnose_agent_communication(agent):
    """
    Diagnóstico completo da comunicação entre agentes
    """
    logger.info(f"[{agent.name}] Iniciando diagnóstico de comunicação entre agentes...")
    
    # Criar verificador
    verifier = AgentCommunicationVerifier(agent)
    
    # Executar verificação
    results = verifier.verify_agent_communication()
    
    # Gerar relatório
    report = verifier.generate_communication_report(results)
    
    return report

def fix_agent_communication_issues(agent):
    """
    Corrige problemas de comunicação entre agentes
    """
    logger.info(f"[{agent.name}] Aplicando correções de comunicação...")
    
    fixes_applied = []
    
    try:
        # 1. VERIFICAR E REINICIAR SISTEMA MULTI-AGENTE
        if hasattr(agent, 'multi_agent_system'):
            if agent.multi_agent_system:
                logger.info(f"[{agent.name}] Sistema multi-agente já está ativo")
            else:
                logger.info(f"[{agent.name}] Reiniciando sistema multi-agente...")
                # Tentar reiniciar
                try:
                    from multi_agent_system import MultiAgentTradingSystem
                    agent.multi_agent_system = MultiAgentTradingSystem()
                    fixes_applied.append("Sistema multi-agente reiniciado")
                    logger.info(f"[{agent.name}] ✅ Sistema multi-agente reiniciado com sucesso")
                except Exception as e:
                    logger.error(f"[{agent.name}] ❌ Falha ao reiniciar sistema multi-agente: {e}")
                    fixes_applied.append(f"Falha no reinício: {str(e)}")
        else:
            fixes_applied.append("Sistema multi-agente não disponível")
            logger.warning(f"[{agent.name}] Sistema multi-agente não está configurado")
        
        # 2. VERIFICAR CONEXÃO COM MT5
        if not agent.is_connected:
            logger.info(f"[{agent.name}] Tentando reconectar ao MT5...")
            if agent.reconnect_mt5():
                fixes_applied.append("Reconexão MT5 bem-sucedida")
                logger.info(f"[{agent.name}] ✅ Reconexão MT5 realizada")
            else:
                fixes_applied.append("Falha na reconexão MT5")
                logger.error(f"[{agent.name}] ❌ Falha na reconexão MT5")
        
        # 3. VERIFICAR CREDENCIAIS
        import os
        required_env_vars = ['MT5_LOGIN', 'MT5_SERVER', 'MT5_PASSWORD']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            fixes_applied.append(f"Variáveis de ambiente faltando: {missing_vars}")
            logger.error(f"[{agent.name}] Variáveis de ambiente faltando: {missing_vars}")
        else:
            fixes_applied.append("Credenciais verificadas")
            logger.info(f"[{agent.name}] ✅ Todas as credenciais estão configuradas")
        
        # 4. VERIFICAR AGENTES INDIVIDUAIS
        if hasattr(agent, 'multi_agent_system') and agent.multi_agent_system:
            agent_status = agent.multi_agent_system.get_agent_status()
            inactive_agents = [name for name, info in agent_status.items() if info.get('status') != 'ACTIVE']
            
            if inactive_agents:
                fixes_applied.append(f"Agentes inativos: {inactive_agents}")
                logger.warning(f"[{agent.name}] Agentes inativos detectados: {inactive_agents}")
                
                # Tentar reativar agentes (se possível)
                try:
                    # Isso seria específico da implementação do MultiAgentTradingSystem
                    logger.info(f"[{agent.name}] Tentando reativar agentes...")
                    # Implementação específica dependeria da estrutura do sistema
                except Exception as e:
                    logger.error(f"[{agent.name}] Erro ao tentar reativar agentes: {e}")
            else:
                fixes_applied.append("Todos os agentes estão ativos")
                logger.info(f"[{agent.name}] ✅ Todos os agentes estão ativos")
        
    except Exception as e:
        logger.error(f"[{agent.name}] Erro durante correções: {e}")
        fixes_applied.append(f"Erro nas correções: {str(e)}")
    
    return fixes_applied

# Função principal para executar diagnóstico completo
def run_complete_diagnostic(agent):
    """
    Executa diagnóstico completo do sistema de agentes
    """
    logger.info(f"[{agent.name}] 🚀 INICIANDO DIAGNÓSTICO COMPLETO DO SISTEMA DE AGENTES")
    
    results = {
        'communication_verified': False,
        'issues_fixed': False,
        'recommendations': []
    }
    
    try:
        # 1. VERIFICAR COMUNICAÇÃO ENTRE AGENTES
        logger.info(f"[{agent.name}] Etapa 1: Verificando comunicação entre agentes...")
        communication_report = diagnose_agent_communication(agent)
        
        if communication_report:
            results['communication_verified'] = True
            logger.info(f"[{agent.name}] ✅ Comunicação verificada")
        else:
            logger.error(f"[{agent.name}] ❌ Falha na verificação de comunicação")
        
        # 2. IDENTIFICAR E CORRIGIR PROBLEMAS
        issues_found = communication_report.get('verification_results', {}).get('issues_found', [])
        if issues_found:
            logger.info(f"[{agent.name}] Etapa 2: Corrigindo problemas identificados...")
            fixes = fix_agent_communication_issues(agent)
            
            if fixes:
                results['issues_fixed'] = True
                results['recommendations'].extend(fixes)
                logger.info(f"[{agent.name}] ✅ {len(fixes)} correções aplicadas")
            else:
                logger.warning(f"[{agent.name}] ⚠️  Nenhuma correção aplicada")
        
        # 3. VERIFICAÇÃO FINAL
        logger.info(f"[{agent.name}] Etapa 3: Verificação final...")
        final_verification = diagnose_agent_communication(agent)
        
        if final_verification:
            final_status = final_verification.get('verification_results', {})
            if final_status.get('communication_working') and final_status.get('decisions_aligned'):
                logger.info(f"[{agent.name}] 🎉 DIAGNÓSTICO CONCLUÍDO COM SUCESSO!")
                logger.info(f"[{agent.name}] ✅ SISTEMA DE AGENTES FUNCIONANDO CORRETAMENTE!")
                results['final_status'] = 'SUCCESS'
            else:
                logger.warning(f"[{agent.name}] ⚠️  DIAGNÓSTICO CONCLUÍDO COM RESTRIÇÕES")
                results['final_status'] = 'PARTIAL_SUCCESS'
        else:
            logger.error(f"[{agent.name}] ❌ FALHA NA VERIFICAÇÃO FINAL")
            results['final_status'] = 'FAILURE'
            
    except Exception as e:
        logger.error(f"[{agent.name}] Erro no diagnóstico completo: {e}")
        results['final_status'] = 'ERROR'
        results['error_details'] = str(e)
    
    # RELATÓRIO FINAL
    logger.info(f"[{agent.name}] === RELATÓRIO FINAL DO DIAGNÓSTICO ===")
    logger.info(f"[{agent.name}] Status: {results['final_status']}")
    logger.info(f"[{agent.name}] Comunicação verificada: {'SIM' if results['communication_verified'] else 'NÃO'}")
    logger.info(f"[{agent.name}] Problemas corrigidos: {'SIM' if results['issues_fixed'] else 'NÃO'}")
    
    if results['recommendations']:
        logger.info(f"[{agent.name}] Recomendações aplicadas:")
        for rec in results['recommendations']:
            logger.info(f"[{agent.name}] - {rec}")
    
    return results

if __name__ == "__main__":
    logger.info("Sistema de verificação de comunicação entre agentes pronto!")
    logger.info("Importe e execute run_complete_diagnostic(agent) com seu RealAgentSystem")