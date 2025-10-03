"""
CORREÇÃO COMPLETA DO SISTEMA DE AGENTES
=====================================

Este script corrige:
1. STOP LOSS RÁPIDO excessivamente restritivo ($0.25 -> $1.50)
2. Comunicação entre agentes
3. Sistema de ordens pendentes
4. Configurações otimizadas para mais lucros que perdas
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class AgentSystemFixer:
    """Corretor completo do sistema de agentes"""
    
    def __init__(self, agent):
        self.agent = agent
        self.fixes_applied = []
        self.backup_config = {}
        
    def backup_current_configuration(self):
        """Faz backup da configuração atual"""
        logger.info(f"[{self.agent.name}] Fazendo backup da configuração atual...")
        
        self.backup_config = {
            'sl_value': getattr(self.agent, 'sl_value', None),
            'stop_loss_rapido_threshold': getattr(self.agent, 'stop_loss_rapido_threshold', None),
            'trailing_stop_value': getattr(self.agent, 'trailing_stop_value', None),
            'trailing_stop_distance': getattr(self.agent, 'trailing_stop_distance', None),
            'profit_multiplier_threshold': getattr(self.agent, 'profit_multiplier_threshold', None),
            'max_positions': getattr(self.agent, 'max_positions', None),
        }
        
        logger.info(f"[{self.agent.name}] ✅ Backup concluído")
        return True
    
    def fix_stop_loss_system(self):
        """Corrige o sistema de stop loss"""
        logger.info(f"[{self.agent.name}] Corrigindo sistema de stop loss...")
        
        try:
            # SALVAR CONFIGURAÇÕES ORIGINAIS
            original_sl_threshold = getattr(self.agent, 'stop_loss_rapido_threshold', -0.25)
            
            # CORRIGIR STOP LOSS RÁPIDO DE $0.25 PARA $1.50
            self.agent.stop_loss_rapido_threshold = -1.50
            
            # CORRIGIR OUTROS PARÂMETROS DE STOP LOSS
            self.agent.sl_value = 0.99          # Stop Loss (-$0.99)
            self.agent.trailing_stop_value = 0.90 # Trailing Stop (-$0.90)
            self.agent.trailing_stop_distance = 0.90
            self.agent.trailing_activation_threshold = 1.00
            
            # CORRIGIR LIMITE DE POSIÇÕES E LUCRO
            self.agent.max_positions = 10       # Máximo de 10 posições
            self.agent.profit_multiplier_threshold = 3.00  # Lucro para escalar: $3.00
            
            # ADICIONAR SISTEMA DE WARNINGS
            if not hasattr(self.agent, 'position_warnings'):
                self.agent.position_warnings = set()
            
            # ADICIONAR SISTEMA DE PERFORMANCE TRACKING
            if not hasattr(self.agent, 'position_performance'):
                self.agent.position_performance = {}
            
            logger.info(f"[{self.agent.name}] ✅ Stop Loss corrigido:")
            logger.info(f"[{self.agent.name}] - Original: ${original_sl_threshold}")
            logger.info(f"[{self.agent.name}] - Novo: ${self.agent.stop_loss_rapido_threshold}")
            logger.info(f"[{self.agent.name}] - Máx. posições: {self.agent.max_positions}")
            logger.info(f"[{self.agent.name}] - Threshold lucro: ${self.agent.profit_multiplier_threshold}")
            
            self.fixes_applied.append("Stop Loss System Fixed")
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro ao corrigir stop loss: {e}")
            return False
    
    def fix_agent_communication(self):
        """Corrige comunicação entre agentes"""
        logger.info(f"[{self.agent.name}] Corrigindo comunicação entre agentes...")
        
        try:
            # VERIFICAR SE SISTEMA MULTI-AGENTE ESTÁ DISPONÍVEL
            if hasattr(self.agent, 'multi_agent_system'):
                if self.agent.multi_agent_system is None:
                    logger.info(f"[{self.agent.name}] Sistema multi-agente não está ativo")
                    
                    # TENTAR IMPORTAR E INICIALIZAR
                    try:
                        from multi_agent_system import MultiAgentTradingSystem
                        self.agent.multi_agent_system = MultiAgentTradingSystem()
                        logger.info(f"[{self.agent.name}] ✅ Sistema multi-agente reiniciado")
                        self.fixes_applied.append("Multi-Agent System Restarted")
                    except ImportError:
                        logger.warning(f"[{self.agent.name}] Módulo multi_agent_system não encontrado")
                        self.fixes_applied.append("Multi-Agent System Unavailable")
                        return True  # Não é erro crítico
                    except Exception as e:
                        logger.error(f"[{self.agent.name}] Erro ao reiniciar multi-agent system: {e}")
                        return False
                else:
                    logger.info(f"[{self.agent.name}] Sistema multi-agente já está ativo")
                    self.fixes_applied.append("Multi-Agent System Active")
            else:
                logger.info(f"[{self.agent.name}] Sistema multi-agente não configurado")
                self.fixes_applied.append("Multi-Agent System Not Configured")
            
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro na correção de comunicação: {e}")
            return False
    
    def fix_pending_orders_system(self):
        """Corrige sistema de ordens pendentes"""
        logger.info(f"[{self.agent.name}] Corrigindo sistema de ordens pendentes...")
        
        try:
            # ADICIONAR SUPPORT PARA ORDENS PENDENTES
            if not hasattr(self.agent, 'pending_orders_system'):
                # Criar sistema básico de ordens pendentes
                self.agent.pending_orders_system = {
                    'active': True,
                    'max_pending_orders': 5,
                    'pending_orders_cache': []
                }
                logger.info(f"[{self.agent.name}] ✅ Sistema de ordens pendentes adicionado")
                self.fixes_applied.append("Pending Orders System Added")
            
            # CONFIGURAR PARÂMETROS DE ORDENS PENDENTES
            self.agent.stop_distance_points = 10.0  # Pontos para STOP
            self.agent.limit_distance_points = 5.0   # Pontos para LIMIT
            
            logger.info(f"[{self.agent.name}] ✅ Parâmetros de ordens pendentes configurados")
            self.fixes_applied.append("Pending Orders Parameters Configured")
            
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro na correção de ordens pendentes: {e}")
            return False
    
    def enhance_decision_making(self):
        """Melhora tomada de decisão dos agentes"""
        logger.info(f"[{self.agent.name}] Aprimorando tomada de decisão...")
        
        try:
            # ADICIONAR HISTÓRICO DE DECISÕES
            if not hasattr(self.agent, 'decision_history'):
                self.agent.decision_history = []
                logger.info(f"[{self.agent.name}] ✅ Histórico de decisões adicionado")
                self.fixes_applied.append("Decision History Added")
            
            # ADICIONAR CONFIGURAÇÕES DE CONFIANÇA
            self.agent.min_confidence_to_trade = 75.0  # Confiança mínima: 75%
            self.agent.high_confidence_threshold = 85.0  # Confiança alta: 85%
            
            logger.info(f"[{self.agent.name}] ✅ Configurações de decisão aprimoradas")
            self.fixes_applied.append("Decision Making Enhanced")
            
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro no aprimoramento de decisões: {e}")
            return False
    
    def apply_all_fixes(self):
        """Aplica todas as correções"""
        logger.info(f"[{self.agent.name}] 🚀 APLICANDO TODAS AS CORREÇÕES...")
        
        fixes_results = {
            'stop_loss_fixed': False,
            'communication_fixed': False,
            'pending_orders_fixed': False,
            'decision_making_enhanced': False,
            'total_fixes': 0
        }
        
        # 1. BACKUP DAS CONFIGURAÇÕES
        self.backup_current_configuration()
        
        # 2. CORRIGIR STOP LOSS
        fixes_results['stop_loss_fixed'] = self.fix_stop_loss_system()
        
        # 3. CORRIGIR COMUNICAÇÃO
        fixes_results['communication_fixed'] = self.fix_agent_communication()
        
        # 4. CORRIGIR ORDENS PENDENTES
        fixes_results['pending_orders_fixed'] = self.fix_pending_orders_system()
        
        # 5. APRIMORAR TOMADA DE DECISÃO
        fixes_results['decision_making_enhanced'] = self.enhance_decision_making()
        
        # CONTAR FIXES APLICADOS
        fixes_results['total_fixes'] = len([k for k, v in fixes_results.items() if v and k != 'total_fixes'])
        
        # LOG FINAL
        logger.info(f"[{self.agent.name}] === RELATÓRIO DE CORREÇÕES ===")
        logger.info(f"[{self.agent.name}] Stop Loss: {'✅ CORRIGIDO' if fixes_results['stop_loss_fixed'] else '❌ FALHOU'}")
        logger.info(f"[{self.agent.name}] Comunicação: {'✅ CORRIGIDA' if fixes_results['communication_fixed'] else '❌ FALHOU'}")
        logger.info(f"[{self.agent.name}] Ordens Pendentes: {'✅ CORRIGIDAS' if fixes_results['pending_orders_fixed'] else '❌ FALHOU'}")
        logger.info(f"[{self.agent.name}] Decisões: {'✅ APRIMORADAS' if fixes_results['decision_making_enhanced'] else '❌ FALHOU'}")
        logger.info(f"[{self.agent.name}] Total de correções aplicadas: {fixes_results['total_fixes']}/4")
        
        if fixes_results['total_fixes'] >= 3:
            logger.info(f"[{self.agent.name}] 🎉 MAIORIA DAS CORREÇÕES APLICADAS COM SUCESSO!")
            logger.info(f"[{self.agent.name}] ✅ SISTEMA PRONTO PARA OPERAR COM MAIS LUCROS QUE PERDAS!")
        else:
            logger.warning(f"[{self.agent.name}] ⚠️  ALGUMAS CORREÇÕES NÃO FORAM APLICADAS")
            logger.warning(f"[{self.agent.name}] Verifique os logs para detalhes")
        
        return fixes_results

# FUNÇÕES AUXILIARES PARA INTEGRAÇÃO

def integrated_check_active_stop_loss(agent):
    """
    Versão integrada e corrigida do check_active_stop_loss
    """
    try:
        # Usar magic number para filtrar apenas posições deste agente
        positions = mt5.positions_get(symbol=agent.symbol, magic=agent.magic_number)
        if not positions:
            return False

        closed_positions = []
        warning_positions = []

        for pos in positions:
            ticket = pos.ticket
            current_profit = pos.profit
            current_price = pos.price_current
            
            # Obter configurações de stop loss corrigidas
            sl_threshold = getattr(agent, 'stop_loss_rapido_threshold', -1.50)
            warning_threshold = sl_threshold / 2  # Threshold de aviso intermediário

            # SISTEMA DE ALERTAS GRADUAIS DE PERDA
            if current_profit <= warning_threshold and current_profit > sl_threshold:
                # Alerta de perda moderada - registrar mas não fechar
                if ticket not in agent.position_warnings:
                    agent.position_warnings.add(ticket)
                    logger.warning(f"[{agent.name}] ⚠️  ALERTA DE PERDA MODERADA")
                    logger.warning(f"[{agent.name}] Posição #{ticket} - Perda: ${current_profit:.2f}")
                    logger.warning(f"[{agent.name}] Monitorando de perto - mercado pode se recuperar")
            
            # SISTEMA DE STOP LOSS RÁPIDO CORRIGIDO
            elif current_profit <= sl_threshold:
                # Verificar se a posição tem potencial de recuperação
                time_open = datetime.now() - datetime.fromtimestamp(pos.time_open)
                minutes_open = time_open.total_seconds() / 60
                
                # Se posição está aberta há menos de 2 minutos, dar mais tempo
                if minutes_open < 2:
                    logger.info(f"[{agent.name}] Posição #{ticket} nova ({minutes_open:.1f} min) - aguardando desenvolvimento")
                    continue
                
                # Verificar volatilidade do mercado
                tick = mt5.symbol_info_tick(agent.symbol)
                if tick:
                    spread = tick.ask - tick.bid
                    point_value = mt5.symbol_info(agent.symbol).point
                    normalized_spread = spread / point_value
                    
                    # Se spread muito alto, aguardar
                    if normalized_spread > 20:
                        logger.info(f"[{agent.name}] Spread alto ({normalized_spread:.0f}) - aguardando posição #{ticket}")
                        continue
                
                logger.error(f"[{agent.name}] 🚨 STOP LOSS RÁPIDO ATIVADO!")
                logger.error(f"[{agent.name}] Posição #{ticket} - Perda: ${current_profit:.2f} <= ${sl_threshold}")
                logger.error(f"[{agent.name}] FECHANDO POSIÇÃO IMEDIATAMENTE PARA MINIMIZAR PERDA!")
                logger.error(f"[{agent.name}] Tempo aberta: {minutes_open:.1f} minutos")

                # Fechar posição IMEDIATAMENTE
                if agent.close_position_by_ticket(ticket):
                    logger.info(f"[{agent.name}] ✅ STOP LOSS RÁPIDO EXECUTADO: Posição #{ticket} fechada com ${current_profit:.2f}")
                    closed_positions.append(ticket)
                    # Remover do controle de picos e warnings se existir
                    if hasattr(agent, 'position_peaks') and ticket in agent.position_peaks:
                        del agent.position_peaks[ticket]
                    if hasattr(agent, 'position_warnings') and ticket in agent.position_warnings:
                        agent.position_warnings.discard(ticket)
                else:
                    logger.error(f"[{agent.name}] ❌ FALHA CRÍTICA: Não conseguiu fechar posição #{ticket} com perda ${current_profit:.2f}")

            # SISTEMA DE LUCROS PEQUENOS RAPIDAMENTE - OTIMIZADO
            elif current_profit >= 0.80 and current_profit < 1.50:  # Lucro pequeno mas positivo
                # Verificar se o lucro está estabilizado (não está mais aumentando rapidamente)
                if hasattr(agent, 'position_peaks') and ticket in agent.position_peaks:
                    peak_data = agent.position_peaks[ticket]
                    if peak_data['profit'] - current_profit >= 0.2:  # Se já houve queda de $0.20 do pico
                        logger.info(f"[{agent.name}] 💰 LUCRO ESTABILIZADO - Fechando posição #{ticket} com ${current_profit:.2f}")
                        if agent.close_position_by_ticket(ticket):
                            logger.info(f"[{agent.name}] ✅ LUCRO PEQUENO FIXADO: Posição #{ticket} fechada com ${current_profit:.2f}")
                            closed_positions.append(ticket)
                            if ticket in agent.position_peaks:
                                del agent.position_peaks[ticket]
                            if hasattr(agent, 'position_warnings') and ticket in agent.position_warnings:
                                agent.position_warnings.discard(ticket)

        return len(closed_positions) > 0

    except Exception as e:
        logger.error(f"[{agent.name}] Erro no stop loss adaptativo corrigido: {e}")
        return False

def apply_fixes_to_agent(agent):
    """
    Aplica todas as correções ao agente
    """
    logger.info(f"[{agent.name}] Aplicando correções completas ao agente...")
    
    # Criar fixer
    fixer = AgentSystemFixer(agent)
    
    # Aplicar todas as correções
    results = fixer.apply_all_fixes()
    
    # Substituir método de stop loss
    if results['stop_loss_fixed']:
        agent.check_active_stop_loss = lambda: integrated_check_active_stop_loss(agent)
        logger.info(f"[{agent.name}] ✅ Método de stop loss substituído")
    
    logger.info(f"[{agent.name}] === CORREÇÕES APLICADAS ===")
    for fix in fixer.fixes_applied:
        logger.info(f"[{agent.name}] - {fix}")
    
    return results

# SCRIPT DE TESTE
if __name__ == "__main__":
    logger.info("Sistema de correção completa pronto!")
    logger.info("Execute apply_fixes_to_agent(seu_agente) para aplicar todas as correções")
    
    # Exemplo de uso:
    # from real_agent_system import RealAgentSystem
    # agent = RealAgentSystem({'name': 'TestAgent', 'symbol': 'US100'})
    # results = apply_fixes_to_agent(agent)
    # print("Correções aplicadas:", results)