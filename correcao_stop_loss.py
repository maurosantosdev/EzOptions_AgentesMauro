"""
CORREÇÃO CRÍTICA PARA O SISTEMA DE STOP LOSS RÁPIDO
==================================================

Problema identificado:
- STOP LOSS RÁPIDO estava ativando com perda de apenas $0.25
- Isso estava causando fechamento prematuro de posições boas
- O sistema não estava dando tempo suficiente para as posições se recuperarem

Solução implementada:
- Aumentar o limite de STOP LOSS RÁPIDO para $1.50 (mais realista)
- Permitir flutuações normais do mercado
- Manter proteção contra grandes perdas
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def fix_stop_loss_rapido(agent):
    """
    Corrige o problema do STOP LOSS RÁPIDO muito restritivo
    """
    logger.info(f"[{agent.name}] Aplicando correção do STOP LOSS RÁPIDO...")
    
    # AUMENTAR LIMITE DE STOP LOSS RÁPIDO DE $0.25 PARA $1.50
    # Isso permite flutuações normais do mercado
    agent.stop_loss_rapido_threshold = -1.50  # Aumentado de -$0.25 para -$1.50
    
    logger.info(f"[{agent.name}] Novo limite STOP LOSS RÁPIDO: ${agent.stop_loss_rapido_threshold}")
    
    return agent

def enhanced_stop_loss_system(agent):
    """
    Sistema aprimorado de stop loss com múltiplos níveis
    """
    # Configurações otimizadas de stop loss
    agent.stop_loss_config = {
        'rapido_threshold': -1.50,      # Stop loss rápido mais tolerante
        'warning_threshold': -0.75,    # Alerta de perda
        'trailing_distance': 0.90,     # Distância do trailing stop
        'activation_threshold': 1.00,   # Ativação do trailing stop
        'max_loss_per_position': -5.0, # Perda máxima por posição
        'protection_level': 3.0        # Nível de proteção avançada
    }
    
    logger.info(f"[{agent.name}] Sistema de stop loss aprimorado configurado")
    logger.info(f"[{agent.name}] Configurações: {agent.stop_loss_config}")
    
    return agent

def improved_check_active_stop_loss(self):
    """
    Versão aprimorada do método check_active_stop_loss
    """
    try:
        # Usar magic number para filtrar apenas posições deste agente
        positions = mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
        if not positions:
            return False

        closed_positions = []
        warning_positions = []

        for pos in positions:
            ticket = pos.ticket
            current_profit = pos.profit
            current_price = pos.price_current
            
            # Obter configurações de stop loss
            sl_config = getattr(self, 'stop_loss_config', {
                'rapido_threshold': -1.50,
                'warning_threshold': -0.75,
                'trailing_distance': 0.90,
                'activation_threshold': 1.00,
                'max_loss_per_position': -5.0,
                'protection_level': 3.0
            })

            # SISTEMA DE ALERTAS GRADUAIS DE PERDA
            if current_profit <= sl_config['warning_threshold'] and current_profit > sl_config['rapido_threshold']:
                # Alerta de perda moderada - registrar mas não fechar
                if ticket not in self.position_warnings:
                    self.position_warnings.add(ticket)
                    logger.warning(f"[{self.name}] ⚠️  ALERTA DE PERDA MODERADA")
                    logger.warning(f"[{self.name}] Posição #{ticket} - Perda: ${current_profit:.2f}")
                    logger.warning(f"[{self.name}] Monitorando de perto - mercado pode se recuperar")
            
            # SISTEMA DE STOP LOSS RÁPIDO APRIMORADO
            elif current_profit <= sl_config['rapido_threshold']:
                # Verificar se a posição tem potencial de recuperação
                time_open = datetime.now() - datetime.fromtimestamp(pos.time_open)
                minutes_open = time_open.total_seconds() / 60
                
                # Se posição está aberta há menos de 2 minutos, dar mais tempo
                if minutes_open < 2:
                    logger.info(f"[{self.name}] Posição #{ticket} nova ({minutes_open:.1f} min) - aguardando desenvolvimento")
                    continue
                
                # Se posição está com perda mas tem histórico positivo recente, dar mais tempo
                if hasattr(self, 'position_performance') and ticket in self.position_performance:
                    perf_history = self.position_performance[ticket][-5:]  # Últimos 5 registros
                    if perf_history and any(p > 0 for p in perf_history[-3:]):  # Últimos 3 positivos
                        logger.info(f"[{self.name}] Posição #{ticket} com histórico positivo - dando mais tempo")
                        continue
                
                logger.error(f"[{self.name}] 🚨 STOP LOSS RÁPIDO ATIVADO!")
                logger.error(f"[{self.name}] Posição #{ticket} - Perda: ${current_profit:.2f} <= ${sl_config['rapido_threshold']}")
                logger.error(f"[{self.name}] FECHANDO POSIÇÃO IMEDIATAMENTE PARA MINIMIZAR PERDA!")
                logger.error(f"[{self.name}] Tempo aberta: {minutes_open:.1f} minutos")

                # Fechar posição IMEDIATAMENTE
                if self.close_position_by_ticket(ticket):  # Usar ticket diretamente em vez do objeto
                    logger.info(f"[{self.name}] ✅ STOP LOSS RÁPIDO EXECUTADO: Posição #{ticket} fechada com ${current_profit:.2f}")
                    closed_positions.append(ticket)
                    # Remover do controle de picos e warnings se existir
                    if ticket in self.position_peaks:
                        del self.position_peaks[ticket]
                    if ticket in self.position_warnings:
                        self.position_warnings.remove(ticket)
                    if hasattr(self, 'position_performance') and ticket in self.position_performance:
                        del self.position_performance[ticket]
                else:
                    logger.error(f"[{self.name}] ❌ FALHA CRÍTICA: Não conseguiu fechar posição #{ticket} com perda ${current_profit:.2f}")

            # SISTEMA DE LUCROS PEQUENOS RAPIDAMENTE - OTIMIZADO
            elif current_profit >= 0.80 and current_profit < 1.50:  # Lucro pequeno mas positivo
                # Verificar se o lucro está estabilizado (não está mais aumentando rapidamente)
                if ticket in self.position_peaks:
                    peak_data = self.position_peaks[ticket]
                    if peak_data['profit'] - current_profit >= 0.2:  # Se já houve queda de $0.20 do pico
                        logger.info(f"[{self.name}] 💰 LUCRO ESTABILIZADO - Fechando posição #{ticket} com ${current_profit:.2f}")
                        if self.close_position_by_ticket(ticket):
                            logger.info(f"[{self.name}] ✅ LUCRO PEQUENO FIXADO: Posição #{ticket} fechada com ${current_profit:.2f}")
                            closed_positions.append(ticket)
                            if ticket in self.position_peaks:
                                del self.position_peaks[ticket]
                            if ticket in self.position_warnings:
                                self.position_warnings.remove(ticket)

        return len(closed_positions) > 0

    except Exception as e:
        logger.error(f"[{self.name}] Erro no stop loss adaptativo aprimorado: {e}")
        return False

def add_position_performance_tracking(agent):
    """
    Adiciona sistema de rastreamento de performance das posições
    """
    agent.position_performance = {}  # Dicionário para rastrear performance histórica
    agent.position_warnings = set()  # Conjunto para rastrear posições com alertas
    
    logger.info(f"[{agent.name}] Sistema de rastreamento de performance adicionado")
    
    return agent

def integrate_improved_stop_loss_system(agent):
    """
    Integra o sistema de stop loss aprimorado ao agente
    """
    logger.info(f"[{agent.name}] Iniciando integração do sistema de stop loss aprimorado...")
    
    # Aplicar correções
    agent = fix_stop_loss_rapido(agent)
    agent = enhanced_stop_loss_system(agent)
    agent = add_position_performance_tracking(agent)
    
    # Substituir método original
    agent.original_check_active_stop_loss = agent.check_active_stop_loss
    agent.check_active_stop_loss = lambda: improved_check_active_stop_loss(agent)
    
    logger.info(f"[{agent.name}] ✅ Sistema de stop loss aprimorado integrado com sucesso!")
    
    return agent

# Função para aplicar correções diretamente ao real_agent_system.py
def apply_stop_loss_fixes(real_agent_system):
    """
    Aplica todas as correções de stop loss ao sistema real
    """
    logger.info(f"[{real_agent_system.name}] Aplicando correções críticas de stop loss...")
    
    # Corrigir limite de stop loss rápido
    real_agent_system.stop_loss_rapido_threshold = -1.50
    
    # Adicionar sistema de tracking
    real_agent_system.position_performance = {}
    real_agent_system.position_warnings = set()
    
    # Atualizar método de verificação
    real_agent_system.check_active_stop_loss = lambda: improved_check_active_stop_loss(real_agent_system)
    
    logger.info(f"[{real_agent_system.name}] ✅ Correções de stop loss aplicadas com sucesso!")
    logger.info(f"[{real_agent_system.name}] Novo limite: ${real_agent_system.stop_loss_rapido_threshold}")
    
    return real_agent_system

if __name__ == "__main__":
    logger.info("Sistema de correção de stop loss pronto para integração!")
    logger.info("Execute apply_stop_loss_fixes() no seu RealAgentSystem")