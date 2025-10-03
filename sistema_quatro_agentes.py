"""
IMPLEMENTAÇÃO COMPLETA: 4 AGENTES + 6 SETUPS + ORDENS PENDENTES
=================================================================

Este script implementa:

1. 4 Agentes especializados comunicando-se:
   - Anti-Prejuizo (evita perdas)
   - Previsão de Força (prevê direção)
   - 6 Setups (analisa 6 setups tradicionais)
   - Coordenador (consolida decisões)

2. Integração com Gamma, Delta e Charm para análise de força

3. Execução de ordens pendentes:
   - BUY STOP + BUY LIMIT quando prever ALTA
   - SELL STOP + SELL LIMIT quando prever BAIXA

4. Sistema completo plugável para real_agent_system.py
"""

import MetaTrader5 as mt5
import logging
import time
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AgentDecision(Enum):
    BUY = "BUY"
    SELL = "SELL" 
    HOLD = "HOLD"

class SetupType(Enum):
    BULLISH_BREAKOUT = "BULLISH_BREAKOUT"
    BEARISH_BREAKOUT = "BEARISH_BREAKOUT"
    PULLBACK_TOP = "PULLBACK_TOP"
    PULLBACK_BOTTOM = "PULLBACK_BOTTOM"
    CONSOLIDATED_MARKET = "CONSOLIDATED_MARKET"
    GAMMA_NEGATIVE_PROTECTION = "GAMMA_NEGATIVE_PROTECTION"

class FourAgentsPendingOrdersSystem:
    """Sistema completo de 4 agentes com ordens pendentes"""
    
    def __init__(self, agent_reference):
        self.agent = agent_reference
        self.decision_history = []
        self.pending_orders_cache = []
        
        # Configurações otimizadas
        self.min_confidence = 70.0
        self.max_positions = 10
        self.stop_distance_points = 10.0  # Pontos para STOP
        self.limit_distance_points = 5.0  # Pontos para LIMIT
        
        logger.info(f"[{self.agent.name}] Sistema 4 Agentes + Ordens Pendentes inicializado")
    
    def analyze_with_four_agents(self, market_data, setups_analysis):
        """
        Analisa mercado com os 4 agentes especializados
        """
        logger.info(f"[{self.agent.name}] === ANÁLISE MULTIPLO AGENTE ===")
        
        agent_decisions = {}
        
        # 1. AGENTE ANTI-PREJUÍZO
        anti_prejuizo_result = self._agent_anti_prejuizo(market_data)
        agent_decisions['Anti-Prejuizo'] = anti_prejuizo_result
        logger.info(f"[{self.agent.name}] Anti-Prejuizo: {anti_prejuizo_result['decision'].value} ({anti_prejuizo_result['confidence']:.1f}%)")
        
        # 2. AGENTE PREVISÃO DE FORÇA
        previsao_forca_result = self._agent_previsao_forca(market_data)
        agent_decisions['Previsão-Força'] = previsao_forca_result
        logger.info(f"[{self.agent.name}] Previsão-Força: {previsao_forca_result['decision'].value} ({previsao_forca_result['confidence']:.1f}%)")
        
        # 3. AGENTE 6 SETUPS
        seis_setups_result = self._agent_seis_setups(setups_analysis, market_data)
        agent_decisions['6-Setups'] = seis_setups_result
        logger.info(f"[{self.agent.name}] 6-Setups: {seis_setups_result['decision'].value} ({seis_setups_result['confidence']:.1f}%)")
        
        # 4. AGENTE COORDENADOR (decisão final)
        coordenador_result = self._agent_coordenador(agent_decisions)
        agent_decisions['Coordenador'] = coordenador_result
        logger.info(f"[{self.agent.name}] Decisão Final: {coordenador_result['decision'].value} ({coordenador_result['confidence']:.1f}%)")
        
        # Log detalhado das razões
        for agent_name, decision in agent_decisions.items():
            if decision.get('reasons'):
                logger.info(f"[{self.agent.name}] {agent_name} - Razões:")
                for reason in decision['reasons'][:3]:  # Limitar a 3 razões para não lotar o log
                    logger.info(f"   - {reason}")
        
        return coordenador_result
    
    def _agent_anti_prejuizo(self, market_data):
        """
        Agente especializado em evitar prejuízos
        """
        try:
            gamma_values = market_data.get('gamma_data', {}).get('values', [])
            delta_values = market_data.get('delta_data', {}).get('values', [])
            charm_values = market_data.get('charm_data', {}).get('values', [])
            
            if not gamma_values or not delta_values:
                return {
                    'decision': AgentDecision.HOLD,
                    'confidence': 0,
                    'reasons': ['Dados insuficientes para análise']
                }
            
            # Médias recentes (últimos 3 valores)
            avg_gamma = sum(gamma_values[-3:]) / len(gamma_values[-3:]) if len(gamma_values) >= 3 else 0
            avg_delta = sum(delta_values[-3:]) / len(delta_values[-3:]) if len(delta_values) >= 3 else 0
            avg_charm = sum(charm_values[-3:]) / len(charm_values[-3:]) if len(charm_values) >= 3 else 0
            
            reasons = []
            
            # Detectar sinais de reversão ou perigo
            if avg_gamma > 50 and avg_delta < -0.3:  # Volatilidade alta + momentum negativo
                reasons.append(f'Volatilidade alta ({avg_gamma:.1f}) + momentum negativo detectado')
                return {
                    'decision': AgentDecision.SELL,
                    'confidence': min(90, avg_gamma / 2 + abs(avg_delta) * 20),
                    'reasons': reasons
                }
            
            elif avg_gamma > 50 and avg_delta > 0.3:  # Volatilidade alta + momentum positivo
                reasons.append(f'Volatilidade alta ({avg_gamma:.1f}) + momentum positivo detectado')
                return {
                    'decision': AgentDecision.BUY,
                    'confidence': min(90, avg_gamma / 2 + abs(avg_delta) * 20),
                    'reasons': reasons
                }
            
            elif abs(avg_delta) > 0.7:  # Momentum extremo
                if avg_delta > 0:
                    reasons.append(f'Momentum extremo positivo ({avg_delta:.2f}) - possível reversão')
                    return {
                        'decision': AgentDecision.SELL,
                        'confidence': min(85, avg_delta * 15),
                        'reasons': reasons
                    }
                else:
                    reasons.append(f'Momentum extremo negativo ({avg_delta:.2f}) - possível reversão')
                    return {
                        'decision': AgentDecision.BUY,
                        'confidence': min(85, abs(avg_delta) * 15),
                        'reasons': reasons
                    }
            
            # Sem sinais claros de perigo
            reasons.append('Mercado estável - sem sinais de perigo iminente')
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 30,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro no agente Anti-Prejuizo: {e}")
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 0,
                'reasons': [f'Erro na análise: {str(e)}']
            }
    
    def _agent_previsao_forca(self, market_data):
        """
        Agente especializado em prever direção pela força do mercado
        """
        try:
            gamma_values = market_data.get('gamma_data', {}).get('values', [])
            delta_values = market_data.get('delta_data', {}).get('values', [])
            charm_values = market_data.get('charm_data', {}).get('values', [])
            
            if not gamma_values or not delta_values or not charm_values:
                return {
                    'decision': AgentDecision.HOLD,
                    'confidence': 0,
                    'reasons': ['Dados insuficientes para análise de força']
                }
            
            # Análise de força combinada
            recent_gamma = gamma_values[-1] if gamma_values else 0
            recent_delta = delta_values[-1] if delta_values else 0
            recent_charm = charm_values[-1] if charm_values else 0
            
            avg_gamma = sum(gamma_values[-3:]) / len(gamma_values[-3:]) if len(gamma_values) >= 3 else 0
            avg_delta = sum(delta_values[-3:]) / len(delta_values[-3:]) if len(delta_values) >= 3 else 0
            avg_charm = sum(charm_values[-3:]) / len(charm_values[-3:]) if len(charm_values) >= 3 else 0
            
            reasons = []
            
            # Força de alta: delta positivo + gamma controlado + charm positivo
            if avg_delta > 0.4 and avg_gamma < 40 and avg_charm > 10:
                confidence = min(95, avg_delta * 20 + avg_charm / 5)
                reasons.append(f'Força de alta detectada (Delta:{avg_delta:.2f}, Gamma:{avg_gamma:.1f}, Charm:{avg_charm:.1f})')
                return {
                    'decision': AgentDecision.BUY,
                    'confidence': confidence,
                    'reasons': reasons
                }
            
            # Força de baixa: delta negativo + gamma controlado + charm negativo
            elif avg_delta < -0.4 and avg_gamma < 40 and avg_charm < -10:
                confidence = min(95, abs(avg_delta) * 20 + abs(avg_charm) / 5)
                reasons.append(f'Força de baixa detectada (Delta:{avg_delta:.2f}, Gamma:{avg_gamma:.1f}, Charm:{avg_charm:.1f})')
                return {
                    'decision': AgentDecision.SELL,
                    'confidence': confidence,
                    'reasons': reasons
                }
            
            # Tendência mista ou fraca
            reasons.append('Força do mercado neutra ou insuficiente')
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 25,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro no agente Previsão de Força: {e}")
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 0,
                'reasons': [f'Erro na análise: {str(e)}']
            }
    
    def _agent_seis_setups(self, setups_analysis, market_data):
        """
        Agente especializado em analisar os 6 setups tradicionais
        """
        try:
            reasons = []
            setup_signals = []
            
            # Analisar cada setup individualmente
            for setup_key, setup_result in setups_analysis.items():
                if setup_result.get('active', False) and setup_result.get('confidence', 0) >= 60:
                    setup_type = str(setup_result.get('setup_type', 'UNKNOWN'))
                    confidence = setup_result.get('confidence', 0)
                    
                    if 'BULLISH' in setup_type or 'BOTTOM' in setup_type:
                        setup_signals.append(('BUY', confidence, f'{setup_key} - {setup_type}'))
                    elif 'BEARISH' in setup_type or 'TOP' in setup_type:
                        setup_signals.append(('SELL', confidence, f'{setup_key} - {setup_type}'))
            
            # Verificar setups ativos
            if not setup_signals:
                reasons.append('Nenhum setup ativo com confiança suficiente')
                return {
                    'decision': AgentDecision.HOLD,
                    'confidence': 20,
                    'reasons': reasons
                }
            
            # Contar sinais de compra e venda
            buy_signals = [s for s in setup_signals if s[0] == 'BUY']
            sell_signals = [s for s in setup_signals if s[0] == 'SELL']
            
            # Verificar consenso
            if len(buy_signals) > len(sell_signals):
                # Maioria dos setups indica compra
                avg_confidence = sum(s[1] for s in buy_signals) / len(buy_signals)
                reasons.extend([s[2] for s in buy_signals])
                return {
                    'decision': AgentDecision.BUY,
                    'confidence': min(90, avg_confidence),
                    'reasons': reasons
                }
            
            elif len(sell_signals) > len(buy_signals):
                # Maioria dos setups indica venda
                avg_confidence = sum(s[1] for s in sell_signals) / len(sell_signals)
                reasons.extend([s[2] for s in sell_signals])
                return {
                    'decision': AgentDecision.SELL,
                    'confidence': min(90, avg_confidence),
                    'reasons': reasons
                }
            
            else:
                # Empate - verificar força dos greeks
                gamma_values = market_data.get('gamma_data', {}).get('values', [])
                delta_values = market_data.get('delta_data', {}).get('values', [])
                
                if gamma_values and delta_values:
                    avg_gamma = sum(gamma_values[-3:]) / len(gamma_values[-3:]) if len(gamma_values) >= 3 else 0
                    avg_delta = sum(delta_values[-3:]) / len(delta_values[-3:]) if len(delta_values) >= 3 else 0
                    
                    if avg_delta > 0.3:
                        reasons.append(f'Empate nos setups, mas momentum positivo detectado (Delta: {avg_delta:.2f})')
                        return {
                            'decision': AgentDecision.BUY,
                            'confidence': min(75, avg_delta * 25),
                            'reasons': reasons
                        }
                    elif avg_delta < -0.3:
                        reasons.append(f'Empate nos setups, mas momentum negativo detectado (Delta: {avg_delta:.2f})')
                        return {
                            'decision': AgentDecision.SELL,
                            'confidence': min(75, abs(avg_delta) * 25),
                            'reasons': reasons
                        }
            
            # Sem consenso claro
            reasons.append('Empate nos setups sem direção clara')
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 30,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro no agente 6 Setups: {e}")
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 0,
                'reasons': [f'Erro na análise: {str(e)}']
            }
    
    def _agent_coordenador(self, agent_decisions):
        """
        Agente coordenador que consolida decisões dos outros agentes
        """
        try:
            buy_decisions = []
            sell_decisions = []
            hold_decisions = []
            reasons = []
            
            # Separar decisões
            for agent_name, decision in agent_decisions.items():
                if decision['decision'] == AgentDecision.BUY:
                    buy_decisions.append((agent_name, decision))
                elif decision['decision'] == AgentDecision.SELL:
                    sell_decisions.append((agent_name, decision))
                else:
                    hold_decisions.append((agent_name, decision))
                
                # Adicionar razões
                if decision.get('reasons'):
                    for reason in decision['reasons'][:2]:  # Limitar a 2 razões por agente
                        reasons.append(f"{agent_name}: {reason}")
            
            # Tomar decisão baseada no consenso
            if len(buy_decisions) > len(sell_decisions) and len(buy_decisions) >= 2:
                # Consenso de compra (pelo menos 2 agentes concordam)
                total_confidence = sum(d[1]['confidence'] for d in buy_decisions)
                avg_confidence = total_confidence / len(buy_decisions)
                
                reasons.append(f"Consenso de compra: {len(buy_decisions)}/{len(agent_decisions)} agentes")
                return {
                    'decision': AgentDecision.BUY,
                    'confidence': min(95, avg_confidence * 1.1),  # Boost para consenso
                    'reasons': reasons
                }
            
            elif len(sell_decisions) > len(buy_decisions) and len(sell_decisions) >= 2:
                # Consenso de venda (pelo menos 2 agentes concordam)
                total_confidence = sum(d[1]['confidence'] for d in sell_decisions)
                avg_confidence = total_confidence / len(sell_decisions)
                
                reasons.append(f"Consenso de venda: {len(sell_decisions)}/{len(agent_decisions)} agentes")
                return {
                    'decision': AgentDecision.SELL,
                    'confidence': min(95, avg_confidence * 1.1),  # Boost para consenso
                    'reasons': reasons
                }
            
            elif len(buy_decisions) == len(sell_decisions) and len(buy_decisions) > 0:
                # Empate - usar confiança máxima
                all_decisions = buy_decisions + sell_decisions
                max_confidence_decision = max(all_decisions, key=lambda x: x[1]['confidence'])
                agent_name, decision = max_confidence_decision
                
                reasons.append(f"Empate, usando decisão mais confiante: {agent_name}")
                return {
                    'decision': decision['decision'],
                    'confidence': min(85, decision['confidence']),
                    'reasons': reasons
                }
            
            # Sem consenso claro
            reasons.append("Nenhum consenso claro entre agentes")
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 25,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro no agente Coordenador: {e}")
            return {
                'decision': AgentDecision.HOLD,
                'confidence': 0,
                'reasons': [f'Erro na coordenação: {str(e)}']
            }
    
    def execute_pending_orders_strategy(self, decision_result, current_price):
        """
        Executa estratégia de ordens pendentes baseada na decisão
        """
        try:
            decision = decision_result['decision']
            confidence = decision_result['confidence']
            
            if decision == AgentDecision.HOLD or confidence < self.min_confidence:
                logger.info(f"[{self.agent.name}] Sem decisão clara ou confiança insuficiente ({confidence:.1f}%)")
                return False
            
            if not current_price:
                logger.error(f"[{self.agent.name}] Preço atual não disponível")
                return False
            
            logger.info(f"[{self.agent.name}] === EXECUTANDO ESTRATÉGIA DE ORDENS PENDENTES ===")
            logger.info(f"[{self.agent.name}] Decisão: {decision.value} | Confiança: {confidence:.1f}%")
            
            # Obter informações do símbolo
            symbol_info = mt5.symbol_info(self.agent.symbol)
            if not symbol_info:
                logger.error(f"[{self.agent.name}] Não foi possível obter informações do símbolo")
                return False
            
            # Calcular distâncias em pontos do símbolo
            point_value = symbol_info.point
            stop_distance = max(5.0 * point_value, self.stop_distance_points * point_value)
            limit_distance = max(3.0 * point_value, self.limit_distance_points * point_value)
            
            # Obter tick atual
            tick = mt5.symbol_info_tick(self.agent.symbol)
            if not tick:
                logger.error(f"[{self.agent.name}] Não foi possível obter tick atual")
                return False
            
            success = False
            
            if decision == AgentDecision.BUY:
                # BUY STOP: Acima do preço atual para confirmar movimento de alta
                stop_price = tick.ask + stop_distance
                # BUY LIMIT: Abaixo do preço atual para entrada otimizada
                limit_price = tick.bid - limit_distance
                
                logger.info(f"[{self.agent.name}] BUY PENDENTES - STOP: {stop_price:.2f}, LIMIT: {limit_price:.2f}")
                
                # Executar BUY STOP
                stop_success = self._place_pending_order(
                    mt5.ORDER_TYPE_BUY_STOP,
                    stop_price,
                    f"BUY_STOP_{datetime.now().strftime('%H%M%S')}"
                )
                
                # Executar BUY LIMIT
                limit_success = self._place_pending_order(
                    mt5.ORDER_TYPE_BUY_LIMIT,
                    limit_price,
                    f"BUY_LIMIT_{datetime.now().strftime('%H%M%S')}"
                )
                
                success = stop_success or limit_success
                
            elif decision == AgentDecision.SELL:
                # SELL STOP: Abaixo do preço atual para confirmar movimento de baixa  
                stop_price = tick.bid - stop_distance
                # SELL LIMIT: Acima do preço atual para entrada otimizada
                limit_price = tick.ask + limit_distance
                
                logger.info(f"[{self.agent.name}] SELL PENDENTES - STOP: {stop_price:.2f}, LIMIT: {limit_price:.2f}")
                
                # Executar SELL STOP
                stop_success = self._place_pending_order(
                    mt5.ORDER_TYPE_SELL_STOP,
                    stop_price,
                    f"SELL_STOP_{datetime.now().strftime('%H%M%S')}"
                )
                
                # Executar SELL LIMIT
                limit_success = self._place_pending_order(
                    mt5.ORDER_TYPE_SELL_LIMIT,
                    limit_price,
                    f"SELL_LIMIT_{datetime.now().strftime('%H%M%S')}"
                )
                
                success = stop_success or limit_success
            
            if success:
                logger.info(f"[{self.agent.name}] ✅ ESTRATÉGIA DE ORDENS PENDENTES EXECUTADA COM SUCESSO!")
                self.decision_history.append({
                    'timestamp': datetime.now(),
                    'decision': decision.value,
                    'confidence': confidence,
                    'price': current_price,
                    'success': True
                })
            else:
                logger.error(f"[{self.agent.name}] ❌ FALHA NA ESTRATÉGIA DE ORDENS PENDENTES")
                self.decision_history.append({
                    'timestamp': datetime.now(),
                    'decision': decision.value,
                    'confidence': confidence,
                    'price': current_price,
                    'success': False
                })
            
            return success
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro na execução de ordens pendentes: {e}")
            return False
    
    def _place_pending_order(self, order_type, price, comment_suffix):
        """
        Coloca ordem pendente com tratamento de erros
        """
        try:
            # Montar requisição
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.agent.symbol,
                "volume": self.agent.lot_size,
                "type": order_type,
                "price": price,
                "deviation": 20,
                "magic": self.agent.magic_number,
                "comment": f"{self.agent.name}_{comment_suffix}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            
            logger.info(f"[{self.agent.name}] Colocando ordem pendente {order_type} @ {price:.2f}")
            
            # Executar ordem
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[{self.agent.name}] ✅ Ordem pendente executada: Ticket {result.order}")
                self.pending_orders_cache.append(result.order)
                return True
            else:
                error_msg = result.comment if result else "Sem resposta"
                logger.error(f"[{self.agent.name}] ❌ Falha na ordem pendente: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro ao colocar ordem pendente: {e}")
            return False
    
    def cancel_existing_pending_orders(self):
        """
        Cancela ordens pendentes existentes antes de colocar novas
        """
        try:
            # Obter ordens pendentes do agente
            existing_orders = mt5.orders_get(magic=self.agent.magic_number)
            if not existing_orders:
                return True
            
            cancelled_count = 0
            for order in existing_orders:
                # Cancelar ordem
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                }
                
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    cancelled_count += 1
                    logger.info(f"[{self.agent.name}] Ordem {order.ticket} cancelada")
                else:
                    logger.error(f"[{self.agent.name}] Falha ao cancelar ordem {order.ticket}")
            
            if cancelled_count > 0:
                logger.info(f"[{self.agent.name}] {cancelled_count} ordens pendentes canceladas")
            
            # Limpar cache
            self.pending_orders_cache.clear()
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro ao cancelar ordens pendentes: {e}")
            return False
    
    def get_system_status(self):
        """
        Retorna status do sistema
        """
        return {
            'agent_name': self.agent.name,
            'decisions_made': len(self.decision_history),
            'pending_orders': len(self.pending_orders_cache),
            'last_decision': self.decision_history[-1] if self.decision_history else None,
            'min_confidence': self.min_confidence
        }

# Função de integração para real_agent_system.py
def integrate_four_agents_system(real_agent):
    """
    Integra o sistema de 4 agentes ao RealAgentSystem
    """
    logger.info(f"[{real_agent.name}] Integrando sistema de 4 agentes...")
    
    # Criar instância do sistema de 4 agentes
    four_agents_system = FourAgentsPendingOrdersSystem(real_agent)
    
    # Adicionar ao agente principal
    real_agent.four_agents_system = four_agents_system
    
    logger.info(f"[{real_agent.name}] Sistema de 4 agentes integrado com sucesso!")
    
    return four_agents_system

# Exemplo de uso no método analyze_market do RealAgentSystem:
"""
# Após obter setups_results e market_data no método analyze_market:

# ANALISAR COM OS 4 AGENTES ESPECIALIZADOS
if hasattr(self, 'four_agents_system'):
    # Preparar dados de mercado para análise
    market_analysis_data = {
        'gamma_data': gamma_data,
        'delta_data': delta_data,
        'charm_data': charm_data,
        'vwap_data': vwap_data,
        'price_data': self.get_recent_price_data(current_price),
        'volume_data': self.get_real_volume_data()
    }
    
    # Analisar com os 4 agentes
    decision_result = self.four_agents_system.analyze_with_four_agents(
        market_analysis_data, 
        setups_results
    )
    
    # Se decisão for clara e confiante, executar estratégia de ordens pendentes
    if decision_result['decision'] != AgentDecision.HOLD and decision_result['confidence'] >= 75:
        logger.info(f"[{self.name}] DECISÃO CLARA DETECTADA - EXECUTANDO ESTRATÉGIA DE ORDENS PENDENTES")
        
        # Cancelar ordens pendentes existentes
        self.four_agents_system.cancel_existing_pending_orders()
        
        # Executar estratégia de ordens pendentes
        success = self.four_agents_system.execute_pending_orders_strategy(
            decision_result, 
            current_price
        )
        
        if success:
            logger.info(f"[{self.name}] ✅ ESTRATÉGIA DE ORDENS PENDENTES EXECUTADA!")
        else:
            logger.error(f"[{self.name}] ❌ FALHA NA ESTRATÉGIA DE ORDENS PENDENTES")
"""

if __name__ == "__main__":
    logger.info("Sistema de 4 agentes com ordens pendentes pronto para integração!")
    logger.info("Adicione ao real_agent_system.py conforme instruções acima.")