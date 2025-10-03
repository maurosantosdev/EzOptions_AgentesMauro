"""
MELHORIA NO SISTEMA DE AGENTES PARA IMPLEMENTAR:
- ORDENS PENDENTES COM OS 6 SETUPS
- COMUNICAÇÃO ENTRE 4 AGENTES
- USO DE GAMMA, DELTA E CHARM PARA DETECÇÃO DE FORÇA
- EXECUÇÃO DE BUY STOP + BUY LIMIT QUANDO PREVER ALTA
- EXECUÇÃO DE SELL STOP + SELL LIMIT QUANDO PREVER BAIXA
"""

import MetaTrader5 as mt5
import time
import logging
from datetime import datetime
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderStrategy(Enum):
    BUY_STOP_LIMIT = "BUY_STOP_LIMIT"
    SELL_STOP_LIMIT = "SELL_STOP_LIMIT"
    NO_ACTION = "NO_ACTION"

class AgentType(Enum):
    ANTI_PREJUIZO = "Anti-Prejuizo"
    PREVISAO_FORCA = "Previsao-Forca"
    6_SETUPS = "6-Setups"
    COORDENADOR = "Coordenador"

class AdvancedAgentSystem:
    """Sistema avançado com 4 agentes comunicando-se para ordens pendentes"""
    
    def __init__(self, symbol="US100", magic_number=234002, lot_size=0.02):
        self.symbol = symbol
        self.magic_number = magic_number
        self.lot_size = lot_size
        
        # Parâmetros otimizados para ordens pendentes
        self.stop_distance = 10  # 10 pontos para ativar stop
        self.limit_distance = 5  # 5 pontos para limit
        self.min_confidence = 75.0  # Confiança mínima para executar
        self.reversal_threshold = 15  # Threshold para reversão de força
        
        # Controle de ordens
        self.active_orders = []
        self.agent_decisions = {}
        self.market_strength = {
            'gamma': 0,
            'delta': 0,
            'charm': 0
        }
        
        logger.info(f"[AdvancedAgentSystem] Sistema inicializado para {symbol}")
        
    def analyze_market_strength(self):
        """Analisa força do mercado usando Gamma, Delta e Charm"""
        try:
            # Obter dados atuais para simular análise greeks
            current_price = self.get_current_price()
            if not current_price:
                return None
                
            # Simular análise de forças com base em dados reais
            # Esta seria uma implementação mais completa com dados reais
            price_data = self.get_recent_price_data()
            volume_data = self.get_real_volume_data()
            
            # Análise de força de curto prazo
            if len(price_data) >= 3:
                # Calculando variações recentes
                recent_changes = [price_data[i] - price_data[i-1] for i in range(1, len(price_data))]
                
                # Simular gamma (volatilidade)
                volatility = sum(abs(change) for change in recent_changes) / len(recent_changes) if recent_changes else 0
                gamma = volatility * 100  # Escalar para valores mais significativos
                
                # Simular delta (momentum)
                avg_change = sum(recent_changes) / len(recent_changes) if recent_changes else 0
                delta = avg_change * 10  # Escalar para representar momentum
                
                # Simular charm (aceleração)
                if len(recent_changes) >= 2:
                    acceleration = recent_changes[-1] - recent_changes[-2]
                    charm = acceleration * 50  # Escalar para representar aceleração
                
                self.market_strength = {
                    'gamma': gamma,
                    'delta': delta,
                    'charm': charm
                }
                
                logger.info(f"[Força Mercado] Gamma: {gamma:.2f}, Delta: {delta:.2f}, Charm: {charm:.2f}")
                
                return self.market_strength
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro na análise de força do mercado: {e}")
            return None
    
    def get_current_price(self):
        """Obtém preço atual"""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
                return (tick.bid + tick.ask) / 2
            return None
        except:
            return None
    
    def get_recent_price_data(self):
        """Obtém dados recentes de preços"""
        try:
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 5)
            if rates is not None:
                return [float(rate.close) for rate in rates]
            return []
        except:
            return []
    
    def get_real_volume_data(self):
        """Obtém dados reais de volume"""
        try:
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 5)
            if rates is not None:
                return [int(rate.tick_volume) for rate in rates]
            return []
        except:
            return []
    
    def agent_anti_prejuizo(self):
        """Agente Anti-Prejuízo - Identifica quando mercado está se movendo contra"""
        logger.info(f"[{AgentType.ANTI_PREJUIZO.value}] Analisando para evitar prejuízos")
        
        current_price = self.get_current_price()
        if not current_price:
            return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Sem preço'}
        
        # Verificar se há sinais de reversão ou fraqueza
        strength = self.market_strength
        if not strength:
            return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Sem força'}
        
        # Se gamma estiver muito alto e delta for negativo, indica volatilidade e possível reversão
        if strength['gamma'] > 50 and strength['delta'] < -0.3:
            # Possível reversão de baixa
            confidence = min(90, max(30, strength['gamma'] / 2))
            return {
                'decision': OrderStrategy.SELL_STOP_LIMIT,
                'confidence': confidence,
                'reason': f'Alta volatilidade e momentum negativo (Gamma:{strength["gamma"]:.1f}, Delta:{strength["delta"]:.2f})'
            }
        
        # Se gamma estiver muito alto e delta for positivo, indica possível reversão
        elif strength['gamma'] > 50 and strength['delta'] > 0.5:
            # Possível reversão de alta
            confidence = min(90, max(30, strength['gamma'] / 2))
            return {
                'decision': OrderStrategy.BUY_STOP_LIMIT,
                'confidence': confidence,
                'reason': f'Alta volatilidade e momentum positivo (Gamma:{strength["gamma"]:.1f}, Delta:{strength["delta"]:.2f})'
            }
        
        return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Força equilibrada'}
    
    def agent_previsao_forca(self):
        """Agente Previsão de Força - Prevê direção baseado em força do mercado"""
        logger.info(f"[{AgentType.PREVISAO_FORCA.value}] Prevendo força do mercado")
        
        current_price = self.get_current_price()
        if not current_price:
            return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Sem preço'}
        
        strength = self.market_strength
        if not strength:
            return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Sem força'}
        
        # Análise combinada de força
        positive_force = (strength['delta'] > 0.2 and strength['charm'] > 5) and strength['gamma'] < 30
        negative_force = (strength['delta'] < -0.2 and strength['charm'] < -5) and strength['gamma'] < 30
        
        if positive_force:
            # Força de alta sem volatilidade extrema
            confidence = min(95, max(40, 30 + abs(strength['delta']) * 50 + abs(strength['charm']) / 2))
            return {
                'decision': OrderStrategy.BUY_STOP_LIMIT,
                'confidence': confidence,
                'reason': f'Força de alta detectada (Delta:{strength["delta"]:.2f}, Charm:{strength["charm"]:.2f}, Gamma:{strength["gamma"]:.1f})'
            }
        
        elif negative_force:
            # Força de baixa sem volatilidade extrema
            confidence = min(95, max(40, 30 + abs(strength['delta']) * 50 + abs(strength['charm']) / 2))
            return {
                'decision': OrderStrategy.SELL_STOP_LIMIT,
                'confidence': confidence,
                'reason': f'Força de baixa detectada (Delta:{strength["delta"]:.2f}, Charm:{strength["charm"]:.2f}, Gamma:{strength["gamma"]:.1f})'
            }
        
        return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Força não clara'}
    
    def agent_6_setups(self):
        """Agente 6 Setups - Analisa os 6 setups tradicionais com greeks"""
        logger.info(f"[{AgentType.6_SETUPS.value}] Analisando 6 setups com greeks")
        
        current_price = self.get_current_price()
        if not current_price:
            return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Sem preço'}
        
        strength = self.market_strength
        if not strength:
            return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Sem força'}
        
        # Simular análise dos 6 setups
        setup_decisions = []
        
        # SETUP 1: Breakout de alta confirmado por greeks
        if strength['delta'] > 0.4 and strength['charm'] > 0 and strength['gamma'] < 40:
            setup_decisions.append(('BULLISH_BREAKOUT', 85, 'Setup 1 - Breakout de alta confirmado'))
        
        # SETUP 2: Breakout de baixa confirmado por greeks
        elif strength['delta'] < -0.4 and strength['charm'] < 0 and strength['gamma'] < 40:
            setup_decisions.append(('BEARISH_BREAKOUT', 85, 'Setup 2 - Breakout de baixa confirmado'))
        
        # SETUP 3: Pullback no topo (demanda esgotada)
        elif strength['delta'] > 0.7 and strength['gamma'] > 50:  # Delta alto indica demanda esgotada
            setup_decisions.append(('TOP_PULLBACK', 80, 'Setup 3 - Pullback no topo, vender'))
        
        # SETUP 4: Pullback no fundo (oferta esgotada)
        elif strength['delta'] < -0.7 and strength['gamma'] > 50:  # Delta negativo alto indica oferta esgotada
            setup_decisions.append(('BOTTOM_PULLBACK', 80, 'Setup 4 - Pullback no fundo, comprar'))
        
        # SETUP 5: Mercado consolidado (aguardar)
        elif abs(strength['delta']) < 0.3 and strength['gamma'] < 20:
            setup_decisions.append(('CONSOLIDATION', 40, 'Setup 5 - Mercado consolidado, aguardar'))
        
        # SETUP 6: Proteção gamma (indicativo de reversão)
        elif strength['gamma'] > 60:
            if strength['delta'] > 0:  # Gamma alto com delta positivo = potencial reversão de alta para baixa
                setup_decisions.append(('GAMMA_REVERSAL_SELL', 75, 'Setup 6 - Proteção gamma, reverte para baixa'))
            else:  # Gamma alto com delta negativo = potencial reversão de baixa para alta
                setup_decisions.append(('GAMMA_REVERSAL_BUY', 75, 'Setup 6 - Proteção gamma, reverte para alta'))
        
        if setup_decisions:
            # Pegar o setup com maior confiança
            best_setup = max(setup_decisions, key=lambda x: x[1])
            setup_type, confidence, reason = best_setup
            
            if setup_type in ['BULLISH_BREAKOUT', 'BOTTOM_PULLBACK', 'GAMMA_REVERSAL_BUY']:
                return {
                    'decision': OrderStrategy.BUY_STOP_LIMIT,
                    'confidence': confidence,
                    'reason': reason
                }
            elif setup_type in ['BEARISH_BREAKOUT', 'TOP_PULLBACK', 'GAMMA_REVERSAL_SELL']:
                return {
                    'decision': OrderStrategy.SELL_STOP_LIMIT,
                    'confidence': confidence,
                    'reason': reason
                }
        
        return {'decision': OrderStrategy.NO_ACTION, 'confidence': 0, 'reason': 'Nenhum setup ativo'}
    
    def agent_coordenador(self, agent_decisions):
        """Agente Coordenador - Consolida decisões e decide estratégia final"""
        logger.info(f"[{AgentType.COORDENADOR.value}] Consolidando decisões dos agentes")
        
        # Contar decisões
        buy_decisions = 0
        sell_decisions = 0
        total_confidence = 0
        reasons = []
        
        for agent_name, decision in agent_decisions.items():
            if decision['decision'] == OrderStrategy.BUY_STOP_LIMIT:
                buy_decisions += 1
                total_confidence += decision['confidence']
                reasons.append(f"{agent_name}: {decision['reason']}")
            elif decision['decision'] == OrderStrategy.SELL_STOP_LIMIT:
                sell_decisions += 1
                total_confidence += decision['confidence']
                reasons.append(f"{agent_name}: {decision['reason']}")
        
        # Decisão final baseada em consenso
        if buy_decisions > sell_decisions and buy_decisions >= 2:  # Maioria concorda em comprar
            avg_confidence = total_confidence / len([d for d in agent_decisions.values() if d['decision'] != OrderStrategy.NO_ACTION]) if any(d['decision'] != OrderStrategy.NO_ACTION for d in agent_decisions.values()) else 0
            final_confidence = min(95, avg_confidence * 1.2)  # Boost para decisão em consenso
            
            return {
                'final_decision': OrderStrategy.BUY_STOP_LIMIT,
                'confidence': final_confidence,
                'consensus': f"{buy_decisions}/{len(agent_decisions)} agentes favoráveis à compra",
                'reasons': reasons
            }
        
        elif sell_decisions > buy_decisions and sell_decisions >= 2:  # Maioria concorda em vender
            avg_confidence = total_confidence / len([d for d in agent_decisions.values() if d['decision'] != OrderStrategy.NO_ACTION]) if any(d['decision'] != OrderStrategy.NO_ACTION for d in agent_decisions.values()) else 0
            final_confidence = min(95, avg_confidence * 1.2)  # Boost para decisão em consenso
            
            return {
                'final_decision': OrderStrategy.SELL_STOP_LIMIT,
                'confidence': final_confidence,
                'consensus': f"{sell_decisions}/{len(agent_decisions)} agentes favoráveis à venda",
                'reasons': reasons
            }
        
        # Se não houver consenso claro, usar confiança ponderada
        elif any(d['decision'] != OrderStrategy.NO_ACTION for d in agent_decisions.values()):
            # Encontrar decisão com maior confiança
            best_decision = OrderStrategy.NO_ACTION
            best_confidence = 0
            best_reason = ""
            
            for agent_name, decision in agent_decisions.items():
                if decision['decision'] != OrderStrategy.NO_ACTION and decision['confidence'] > best_confidence:
                    best_decision = decision['decision']
                    best_confidence = decision['confidence']
                    best_reason = f"{agent_name}: {decision['reason']}"
            
            if best_confidence >= self.min_confidence:
                return {
                    'final_decision': best_decision,
                    'confidence': best_confidence,
                    'consensus': "Decisão baseada na maior confiança",
                    'reasons': [best_reason]
                }
        
        return {
            'final_decision': OrderStrategy.NO_ACTION,
            'confidence': 0,
            'consensus': "Nenhum consenso claro",
            'reasons': ["Nenhuma decisão satisfaz os critérios mínimos"]
        }
    
    def execute_pending_orders(self, strategy, current_price, confidence):
        """Executa ordens pendentes (STOP + LIMIT)"""
        if strategy == OrderStrategy.NO_ACTION:
            return False
        
        try:
            logger.info(f"[EXECUÇÃO] Executando ordens pendentes: {strategy.value} (Confiança: {confidence:.1f}%)")
            
            # Calcular preços para ordens pendentes
            if strategy == OrderStrategy.BUY_STOP_LIMIT:
                # BUY STOP: Acima do preço atual para confirmar alta
                stop_price = current_price + (self.stop_distance / 100)  # Ajuste baseado em ponto do símbolo
                # BUY LIMIT: Abaixo do preço atual para entrada secundária
                limit_price = current_price - (self.limit_distance / 100)  # Ajuste baseado em ponto do símbolo
                
                logger.info(f"[BUY ORDENS] STOP: {stop_price:.2f}, LIMIT: {limit_price:.2f}")
                
                # Executar BUY STOP
                success1 = self.place_order_with_retry(mt5.ORDER_TYPE_BUY_STOP, stop_price, "BUY_STOP")
                # Executar BUY LIMIT (se necessário)
                success2 = self.place_order_with_retry(mt5.ORDER_TYPE_BUY_LIMIT, limit_price, "BUY_LIMIT")
                
                return success1 or success2
                
            elif strategy == OrderStrategy.SELL_STOP_LIMIT:
                # SELL STOP: Abaixo do preço atual para confirmar baixa
                stop_price = current_price - (self.stop_distance / 100)  # Ajuste baseado em ponto do símbolo
                # SELL LIMIT: Acima do preço atual para entrada secundária
                limit_price = current_price + (self.limit_distance / 100)  # Ajuste baseado em ponto do símbolo
                
                logger.info(f"[SELL ORDENS] STOP: {stop_price:.2f}, LIMIT: {limit_price:.2f}")
                
                # Executar SELL STOP
                success1 = self.place_order_with_retry(mt5.ORDER_TYPE_SELL_STOP, stop_price, "SELL_STOP")
                # Executar SELL LIMIT (se necessário)
                success2 = self.place_order_with_retry(mt5.ORDER_TYPE_SELL_LIMIT, limit_price, "SELL_LIMIT")
                
                return success1 or success2
        
        except Exception as e:
            logger.error(f"Erro na execução de ordens pendentes: {e}")
            return False
    
    def place_order_with_retry(self, order_type, price, order_tag):
        """Coloca ordem com sistema de retry"""
        max_retries = 3
        current_price = self.get_current_price()
        
        for attempt in range(max_retries):
            try:
                # Verificar se o preço é válido
                if not current_price:
                    logger.error(f"Falha: Não foi possível obter preço atual")
                    return False
                
                # Montar solicitação de ordem pendente
                request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.symbol,
                    "volume": self.lot_size,
                    "type": order_type,
                    "price": price,
                    "deviation": 20,
                    "magic": self.magic_number,
                    "comment": f"Auto-{order_tag}-{datetime.now().strftime('%H:%M:%S')}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_RETURN,
                }
                
                logger.info(f"Tentativa {attempt + 1}: Colocando ordem {order_type} @ {price}")
                
                result = mt5.order_send(request)
                
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"✅ Ordem {order_tag} executada com sucesso: Ticket {result.order}")
                    return True
                else:
                    logger.warning(f"⚠️  Tentativa {attempt + 1} falhou: {result.comment if result else 'Sem resultado'}")
                    
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {e}")
            
            # Esperar antes da próxima tentativa
            if attempt < max_retries - 1:
                time.sleep(1)
        
        logger.error(f"❌ Falha após {max_retries} tentativas para ordem {order_tag}")
        return False
    
    def run_single_cycle(self):
        """Executa um único ciclo de decisão dos agentes"""
        logger.info("=" * 60)
        logger.info("INICIANDO CICLO DE DECISÃO DOS 4 AGENTES")
        logger.info("=" * 60)
        
        # Primeiro, analisar força do mercado
        market_strength = self.analyze_market_strength()
        if not market_strength:
            logger.error("Não foi possível analisar força do mercado")
            return False
        
        # Executar cada agente
        agent_results = {}
        
        # Agente Anti-Prejuízo
        agent_results[AgentType.ANTI_PREJUIZO.value] = self.agent_anti_prejuizo()
        logger.info(f"[{AgentType.ANTI_PREJUIZO.value}] Resultado: {agent_results[AgentType.ANTI_PREJUIZO.value]['decision'].value} ({agent_results[AgentType.ANTI_PREJUIZO.value]['confidence']:.1f}%)")
        
        # Agente Previsão de Força
        agent_results[AgentType.PREVISAO_FORCA.value] = self.agent_previsao_forca()
        logger.info(f"[{AgentType.PREVISAO_FORCA.value}] Resultado: {agent_results[AgentType.PREVISAO_FORCA.value]['decision'].value} ({agent_results[AgentType.PREVISAO_FORCA.value]['confidence']:.1f}%)")
        
        # Agente 6 Setups
        agent_results[AgentType.6_SETUPS.value] = self.agent_6_setups()
        logger.info(f"[{AgentType.6_SETUPS.value}] Resultado: {agent_results[AgentType.6_SETUPS.value]['decision'].value} ({agent_results[AgentType.6_SETUPS.value]['confidence']:.1f}%)")
        
        # Coordenador (toma decisão final)
        coordination_result = self.agent_coordenador(agent_results)
        logger.info(f"[{AgentType.COORDENADOR.value}] Decisão final: {coordination_result['final_decision'].value}")
        logger.info(f"[{AgentType.COORDENADOR.value}] Confiança: {coordination_result['confidence']:.1f}%")
        logger.info(f"[{AgentType.COORDENADOR.value}] Consenso: {coordination_result['consensus']}")
        
        # Executar ordens se for uma decisão válida
        if coordination_result['final_decision'] != OrderStrategy.NO_ACTION and coordination_result['confidence'] >= self.min_confidence:
            current_price = self.get_current_price()
            if current_price:
                success = self.execute_pending_orders(
                    coordination_result['final_decision'],
                    current_price,
                    coordination_result['confidence']
                )
                
                if success:
                    logger.info(f"✅ EXECUÇÃO BEM SUCEDIDA: {coordination_result['final_decision'].value}")
                    for reason in coordination_result['reasons']:
                        logger.info(f"   - {reason}")
                else:
                    logger.error("❌ FALHA NA EXECUÇÃO DAS ORDENS")
            else:
                logger.error("❌ Não foi possível obter preço para execução")
        else:
            logger.info("⏳ Nenhuma ordem executada - critérios não atendidos")
        
        logger.info("=" * 60)
        logger.info("CICLO DE AGENTES CONCLUÍDO")
        logger.info("=" * 60)
        
        return coordination_result['final_decision'] != OrderStrategy.NO_ACTION

def main():
    """Função principal para testar o sistema"""
    logger.info("🚀 INICIANDO SISTEMA AVANÇADO DE 4 AGENTES")
    logger.info("🎯 Objetivo: Executar BUY STOP/BUY LIMIT ou SELL STOP/SELL LIMIT")
    logger.info("🔍 Baseado em análise dos 6 setups + Gamma/Delta/Charm")
    
    # Inicializar sistema
    system = AdvancedAgentSystem()
    
    # Executar um ciclo de teste
    try:
        cycle_result = system.run_single_cycle()
        logger.info(f"Resultado do ciclo: {'EXECUTADO' if cycle_result else 'NENHUMA AÇÃO'}")
    except Exception as e:
        logger.error(f"Erro no sistema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()