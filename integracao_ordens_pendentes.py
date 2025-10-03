"""
INTEGRACAO DE ORDENS PENDENTES AO SISTEMA REAL_AGENT_SYSTEM
Esta é uma implementação direta que pode ser adicionada ao real_agent_system.py
para habilitar ordens pendentes (BUY STOP/LIMIT e SELL STOP/LIMIT)
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PendingOrdersSystem:
    """Sistema de ordens pendentes integrado ao RealAgentSystem"""
    
    def __init__(self, agent):
        self.agent = agent  # Referência ao agente principal
        self.pending_orders = []  # Controle interno de ordens pendentes
        self.setup_types = {
            'BULLISH_BREAKOUT': 'ALTA',
            'BEARISH_BREAKOUT': 'BAIXA', 
            'PULLBACK_TOP': 'BAIXA',
            'PULLBACK_BOTTOM': 'ALTA',
            'CONSOLIDATED_MARKET': 'AGUARDAR',
            'GAMMA_NEGATIVE_PROTECTION': 'ALTA'
        }
        
    def analyze_pending_opportunity(self, setups_results, market_analysis):
        """
        Analisa oportunidade para ordens pendentes baseado em:
        - 6 setups com greeks (Gamma, Delta, Charm)
        - Força do mercado
        - Tendência preditiva
        """
        try:
            logger.info(f"[{self.agent.name}] === ANÁLISE DE ORDENS PENDENTES ===")
            
            # Contar setups ativos e suas direções
            buy_setups = []
            sell_setups = []
            consolidation_setups = []
            
            for setup_key, setup_result in setups_results.items():
                if setup_result.active and setup_result.confidence >= 60.0:
                    setup_type_str = str(setup_result.setup_type)
                    
                    if 'BULLISH' in setup_type_str or 'BOTTOM' in setup_type_str:
                        buy_setups.append((setup_key, setup_result))
                    elif 'BEARISH' in setup_type_str or 'TOP' in setup_type_str:
                        sell_setups.append((setup_key, setup_result))
                    elif 'CONSOLIDATED' in setup_type_str:
                        consolidation_setups.append((setup_key, setup_result))
            
            # Verificar se mercado está consolidado
            if len(consolidation_setups) > 0:
                logger.info(f"[{self.agent.name}] MERCADO CONSOLIDADO DETECTADO - AGUARDANDO BREAKOUT")
                return None, 0, "MERCADO_CONSOLIDADO"
            
            # Determinar ação baseada na maioria dos setups
            if len(buy_setups) > len(sell_setups) and len(buy_setups) >= 1:
                # Sinais de alta predominantes
                strongest_buy = max(buy_setups, key=lambda x: x[1].confidence)
                avg_confidence = sum(s[1].confidence for s in buy_setups) / len(buy_setups)
                
                logger.info(f"[{self.agent.name}] SINAIS DE ALTA DETECTADOS: {len(buy_setups)} setups")
                logger.info(f"[{self.agent.name}] Setup mais forte: {strongest_buy[0]} (Conf: {strongest_buy[1].confidence:.1f}%)")
                
                return 'BUY', avg_confidence, f"ALTA_CONFIRMADA_{len(buy_setups)}_SETUPS"
                
            elif len(sell_setups) > len(buy_setups) and len(sell_setups) >= 1:
                # Sinais de baixa predominantes
                strongest_sell = max(sell_setups, key=lambda x: x[1].confidence)
                avg_confidence = sum(s[1].confidence for s in sell_setups) / len(sell_setups)
                
                logger.info(f"[{self.agent.name}] SINAIS DE BAIXA DETECTADOS: {len(sell_setups)} setups")
                logger.info(f"[{self.agent.name}] Setup mais forte: {strongest_sell[0]} (Conf: {strongest_sell[1].confidence:.1f}%)")
                
                return 'SELL', avg_confidence, f"BAIXA_CONFIRMADA_{len(sell_setups)}_SETUPS"
            
            # Se houver empate, verificar força dos greeks
            if len(buy_setups) == len(sell_setups) and len(buy_setups) > 0:
                # Analisar força dos greeks para desempate
                gamma_strength = market_analysis.get('gamma_data', {}).get('values', [0])
                delta_strength = market_analysis.get('delta_data', {}).get('values', [0])
                charm_strength = market_analysis.get('charm_data', {}).get('values', [0])
                
                if gamma_strength and delta_strength and charm_strength:
                    avg_gamma = sum(gamma_strength[-3:]) / len(gamma_strength[-3:]) if gamma_strength else 0
                    avg_delta = sum(delta_strength[-3:]) / len(delta_strength[-3:]) if delta_strength else 0
                    avg_charm = sum(charm_strength[-3:]) / len(charm_strength[-3:]) if charm_strength else 0
                    
                    # Se gamma positivo e delta > 0.3 = tendência de alta
                    if avg_gamma > 0 and avg_delta > 0.3:
                        return 'BUY', 75.0, f"DESEMPATE_GREEKS_ALTA"
                    # Se gamma negativo e delta < 0.3 = tendência de baixa
                    elif avg_gamma < 0 and avg_delta < 0.3:
                        return 'SELL', 75.0, f"DESEMPATE_GREEKS_BAIXA"
            
            logger.info(f"[{self.agent.name}] NENHUM SINAL CLARO DETECTADO")
            return None, 0, "SEM_SINAL_CLARO"
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro na análise de ordens pendentes: {e}")
            return None, 0, "ERRO_ANALISE"
    
    def execute_pending_orders(self, action, confidence, reason, current_price):
        """
        Executa ordens pendentes (STOP + LIMIT) baseado na ação
        """
        try:
            if not action or confidence < 65.0:  # Confiança mínima para ordens pendentes
                logger.info(f"[{self.agent.name}] CONFIDENÇA INSUFICIENTE PARA ORDENS PENDENTES ({confidence:.1f}%)")
                return False
            
            logger.info(f"[{self.agent.name}] === EXECUTANDO ORDENS PENDENTES ===")
            logger.info(f"[{self.agent.name}] Ação: {action} | Confiança: {confidence:.1f}%")
            logger.info(f"[{self.agent.name}] Razão: {reason}")
            
            # Calcular distâncias baseadas na volatilidade do mercado
            symbol_info = mt5.symbol_info(self.agent.symbol)
            if not symbol_info:
                logger.error(f"[{self.agent.name}] Não foi possível obter info do símbolo")
                return False
            
            # Distâncias em pontos do símbolo (ajustadas para US100)
            point_value = symbol_info.point
            stop_distance_points = max(5.0, 10.0 * point_value)  # Min 5 pontos, ajustável
            limit_distance_points = max(3.0, 5.0 * point_value)    # Min 3 pontos, ajustável
            
            # Obter tick atual
            tick = mt5.symbol_info_tick(self.agent.symbol)
            if not tick:
                logger.error(f"[{self.agent.name}] Não foi possível obter tick")
                return False
            
            # Calcular preços para ordens pendentes
            if action == 'BUY':
                # BUY STOP: Acima do preço atual para confirmar movimento de alta
                stop_price = tick.ask + stop_distance_points
                # BUY LIMIT: Abaixo do preço atual para entrada otimizada
                limit_price = tick.bid - limit_distance_points
                
                logger.info(f"[{self.agent.name}] BUY ORDENS - STOP: {stop_price:.2f}, LIMIT: {limit_price:.2f}")
                
                # Executar BUY STOP
                stop_success = self._place_pending_order(
                    mt5.ORDER_TYPE_BUY_STOP, 
                    stop_price, 
                    f"BUY_STOP_{reason}"
                )
                
                # Executar BUY LIMIT (opcional, pode ser removido para simplificar)
                limit_success = self._place_pending_order(
                    mt5.ORDER_TYPE_BUY_LIMIT, 
                    limit_price, 
                    f"BUY_LIMIT_{reason}"
                )
                
                return stop_success or limit_success
                
            elif action == 'SELL':
                # SELL STOP: Abaixo do preço atual para confirmar movimento de baixa
                stop_price = tick.bid - stop_distance_points
                # SELL LIMIT: Acima do preço atual para entrada otimizada
                limit_price = tick.ask + limit_distance_points
                
                logger.info(f"[{self.agent.name}] SELL ORDENS - STOP: {stop_price:.2f}, LIMIT: {limit_price:.2f}")
                
                # Executar SELL STOP
                stop_success = self._place_pending_order(
                    mt5.ORDER_TYPE_SELL_STOP, 
                    stop_price, 
                    f"SELL_STOP_{reason}"
                )
                
                # Executar SELL LIMIT (opcional, pode ser removido para simplificar)
                limit_success = self._place_pending_order(
                    mt5.ORDER_TYPE_SELL_LIMIT, 
                    limit_price, 
                    f"SELL_LIMIT_{reason}"
                )
                
                return stop_success or limit_success
            
            return False
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro ao executar ordens pendentes: {e}")
            return False
    
    def _place_pending_order(self, order_type, price, comment_suffix):
        """
        Coloca ordem pendente com tratamento de erros
        """
        try:
            # Verificar se já temos ordens pendentes do mesmo tipo
            existing_orders = mt5.orders_get(symbol=self.agent.symbol, magic=self.agent.magic_number)
            if existing_orders:
                for order in existing_orders:
                    # Se já temos ordem pendente do mesmo tipo, não colocar outra
                    if order.type == order_type:
                        logger.info(f"[{self.agent.name}] Ordem {order_type} já existe - não colocando duplicada")
                        return False
            
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
                self.pending_orders.append(result.order)
                return True
            else:
                error_msg = result.comment if result else "Sem resposta"
                logger.error(f"[{self.agent.name}] ❌ Falha na ordem pendente: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro ao colocar ordem pendente: {e}")
            return False
    
    def cancel_pending_orders(self):
        """
        Cancela todas as ordens pendentes do agente
        """
        try:
            orders = mt5.orders_get(magic=self.agent.magic_number)
            if not orders:
                return True
            
            cancelled_count = 0
            for order in orders:
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
            
            logger.info(f"[{self.agent.name}] {cancelled_count}/{len(orders)} ordens pendentes canceladas")
            return True
            
        except Exception as e:
            logger.error(f"[{self.agent.name}] Erro ao cancelar ordens pendentes: {e}")
            return False

# Função para integrar ao sistema principal
def integrate_pending_orders_system(agent):
    """
    Integra o sistema de ordens pendentes ao agente principal
    """
    logger.info(f"[{agent.name}] Integrando sistema de ordens pendentes...")
    
    # Adicionar sistema de ordens pendentes ao agente
    agent.pending_orders_system = PendingOrdersSystem(agent)
    
    # Adicionar métodos necessários ao agente
    agent.execute_pending_orders = lambda action, confidence, reason, price: \
        agent.pending_orders_system.execute_pending_orders(action, confidence, reason, price)
    
    agent.cancel_pending_orders = lambda: agent.pending_orders_system.cancel_pending_orders()
    
    logger.info(f"[{agent.name}] Sistema de ordens pendentes integrado com sucesso!")

# Exemplo de como usar no método execute_agent_recommendation do RealAgentSystem:
"""
# Adicionar após a análise de setups no método execute_agent_recommendation:

# ANALISAR OPORTUNIDADE DE ORDENS PENDENTES
if hasattr(self, 'pending_orders_system'):
    # Preparar dados de mercado para análise
    market_analysis_data = {
        'gamma_data': gamma_data,
        'delta_data': delta_data, 
        'charm_data': charm_data,
        'vwap_data': vwap_data,
        'price_data': self.get_recent_price_data(current_price),
        'volume_data': self.get_real_volume_data()
    }
    
    # Analisar oportunidade de ordens pendentes
    action, confidence, reason = self.pending_orders_system.analyze_pending_opportunity(
        setups_results, market_analysis_data
    )
    
    # Se houver oportunidade, executar ordens pendentes
    if action and confidence >= 70.0:  # Confiança alta para ordens pendentes
        logger.info(f"[{self.name}] OPORTUNIDADE DE ORDENS PENDENTES DETECTADA!")
        logger.info(f"[{self.name}] Ação: {action} | Confiança: {confidence:.1f}% | Razão: {reason}")
        
        # Cancelar ordens pendentes antigas
        self.cancel_pending_orders()
        
        # Executar novas ordens pendentes
        success = self.execute_pending_orders(action, confidence, reason, current_price)
        
        if success:
            logger.info(f"[{self.name}] ✅ ORDENS PENDENTES EXECUTADAS COM SUCESSO!")
        else:
            logger.error(f"[{self.name}] ❌ FALHA NA EXECUÇÃO DAS ORDENS PENDENTES")
"""

if __name__ == "__main__":
    logger.info("Sistema de ordens pendentes pronto para integração!")
    logger.info("Adicione ao real_agent_system.py conforme instruções acima.")