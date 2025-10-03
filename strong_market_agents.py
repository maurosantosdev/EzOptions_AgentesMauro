"""
Implementação dos agentes de mercado forte conforme solicitado:
- BUY STOP: Comprar parar quando o mercado estiver comprando forte
- BUY LIMIT: Comprar limite até perceber que o mercado vai vender forte
- SELL STOP: Vender parar quando o mercado estiver vendendo forte  
- SELL LIMIT: Vender limite até perceber que o mercado vai comprar forte
"""

import threading
from trading_setups import SetupType
from agent_system import AgentSystem


class StrongMarketAgentSystem(AgentSystem):
    """Extensão do sistema de agentes para lidar especificamente com condições de mercado forte"""
    
    def __init__(self, config):
        super().__init__(config)
        # Atualizar o nome do agente para refletir seu propósito
        self.name = config.get('name', 'StrongMarketAgent')
    
    def should_activate_strong_market_agents(self):
        """Verifica se o mercado está em condições fortes para ativar os agentes"""
        # Verifica se pelo menos um dos setups de mercado forte tem alta confiança
        strong_market_confidence = 0
        if self.current_setups:
            for setup_key, setup_result in self.current_setups.items():
                if setup_result.setup_type in [
                    SetupType.BUY_STOP_STRONG_MARKET,
                    SetupType.BUY_LIMIT_STRONG_MARKET, 
                    SetupType.SELL_STOP_STRONG_MARKET,
                    SetupType.SELL_LIMIT_STRONG_MARKET
                ]:
                    strong_market_confidence = max(strong_market_confidence, setup_result.confidence)
        
        # Ativa agentes em condições de mercado forte (alta confiança)
        return strong_market_confidence >= 70.0  # Limiar para mercado forte
    
    def get_strong_market_signals(self):
        """Obtém os sinais dos agentes de mercado forte"""
        signals = {
            'buy_stop_strong': None,
            'buy_limit_strong': None, 
            'sell_stop_strong': None,
            'sell_limit_strong': None
        }
        
        if self.current_setups:
            for setup_key, setup_result in self.current_setups.items():
                if setup_result.active and setup_result.confidence >= self.confidence_system.operation_threshold:
                    if setup_result.setup_type == SetupType.BUY_STOP_STRONG_MARKET:
                        signals['buy_stop_strong'] = setup_result
                    elif setup_result.setup_type == SetupType.BUY_LIMIT_STRONG_MARKET:
                        signals['buy_limit_strong'] = setup_result
                    elif setup_result.setup_type == SetupType.SELL_STOP_STRONG_MARKET:
                        signals['sell_stop_strong'] = setup_result
                    elif setup_result.setup_type == SetupType.SELL_LIMIT_STRONG_MARKET:
                        signals['sell_limit_strong'] = setup_result
        
        return signals


class BuyStopStrongMarketAgent(AgentSystem):
    """Agente que executa buy stop quando percebe que o mercado está comprando forte"""
    
    def __init__(self, config):
        config['name'] = 'BuyStopStrongMarketAgent'
        super().__init__(config)
        
    def should_trade(self):
        """Verifica se deve operar baseado no setup de buy stop em mercado forte"""
        setup_result = self.current_setups.get(SetupType.BUY_STOP_STRONG_MARKET.value)
        return setup_result and setup_result.active and setup_result.confidence >= self.confidence_system.operation_threshold
    
    def get_trading_signal(self):
        """Obtém o sinal de compra para o agente"""
        setup_result = self.current_setups.get(SetupType.BUY_STOP_STRONG_MARKET.value)
        if setup_result and setup_result.active:
            return {
                'action': 'BUY',
                'order_type': 'BUY_STOP',
                'target_price': setup_result.target_price,
                'stop_loss': setup_result.stop_loss,
                'confidence': setup_result.confidence,
                'risk_level': setup_result.risk_level
            }
        return None


class BuyLimitStrongMarketAgent(AgentSystem):
    """Agente que executa buy limit até perceber que o mercado vai vender forte"""
    
    def __init__(self, config):
        config['name'] = 'BuyLimitStrongMarketAgent'
        super().__init__(config)
    
    def should_trade(self):
        """Verifica se deve operar baseado no setup de buy limit em mercado forte"""
        setup_result = self.current_setups.get(SetupType.BUY_LIMIT_STRONG_MARKET.value)
        # O agente para de operar se houver sinais de reversão
        return (setup_result and setup_result.active and 
                setup_result.confidence >= self.confidence_system.operation_threshold)
    
    def get_trading_signal(self):
        """Obtém o sinal de compra limit para o agente"""
        setup_result = self.current_setups.get(SetupType.BUY_LIMIT_STRONG_MARKET.value)
        if setup_result and setup_result.active:
            return {
                'action': 'BUY',
                'order_type': 'BUY_LIMIT',
                'target_price': setup_result.target_price,
                'stop_loss': setup_result.stop_loss,
                'confidence': setup_result.confidence,
                'risk_level': setup_result.risk_level
            }
        return None


class SellStopStrongMarketAgent(AgentSystem):
    """Agente que executa sell stop quando percebe que o mercado está vendendo forte"""
    
    def __init__(self, config):
        config['name'] = 'SellStopStrongMarketAgent'
        super().__init__(config)
    
    def should_trade(self):
        """Verifica se deve operar baseado no setup de sell stop em mercado forte"""
        setup_result = self.current_setups.get(SetupType.SELL_STOP_STRONG_MARKET.value)
        return setup_result and setup_result.active and setup_result.confidence >= self.confidence_system.operation_threshold
    
    def get_trading_signal(self):
        """Obtém o sinal de venda para o agente"""
        setup_result = self.current_setups.get(SetupType.SELL_STOP_STRONG_MARKET.value)
        if setup_result and setup_result.active:
            return {
                'action': 'SELL',
                'order_type': 'SELL_STOP',
                'target_price': setup_result.target_price,
                'stop_loss': setup_result.stop_loss,
                'confidence': setup_result.confidence,
                'risk_level': setup_result.risk_level
            }
        return None


class SellLimitStrongMarketAgent(AgentSystem):
    """Agente que executa sell limit até perceber que o mercado vai comprar forte"""
    
    def __init__(self, config):
        config['name'] = 'SellLimitStrongMarketAgent'
        super().__init__(config)
    
    def should_trade(self):
        """Verifica se deve operar baseado no setup de sell limit em mercado forte"""
        setup_result = self.current_setups.get(SetupType.SELL_LIMIT_STRONG_MARKET.value)
        # O agente para de operar se houver sinais de reversão
        return (setup_result and setup_result.active and 
                setup_result.confidence >= self.confidence_system.operation_threshold)
    
    def get_trading_signal(self):
        """Obtém o sinal de venda limit para o agente"""
        setup_result = self.current_setups.get(SetupType.SELL_LIMIT_STRONG_MARKET.value)
        if setup_result and setup_result.active:
            return {
                'action': 'SELL',
                'order_type': 'SELL_LIMIT',
                'target_price': setup_result.target_price,
                'stop_loss': setup_result.stop_loss,
                'confidence': setup_result.confidence,
                'risk_level': setup_result.risk_level
            }
        return None


class MultiStrongMarketAgentManager:
    """Gerenciador de múltiplos agentes de mercado forte"""
    
    def __init__(self, config):
        self.config = config
        self.agents = {
            'buy_stop': BuyStopStrongMarketAgent(config),
            'buy_limit': BuyLimitStrongMarketAgent(config),
            'sell_stop': SellStopStrongMarketAgent(config),
            'sell_limit': SellLimitStrongMarketAgent(config)
        }
        self.active_threads = []
        
    def start_all_agents(self):
        """Inicia todos os agentes de mercado forte"""
        for name, agent in self.agents.items():
            thread = threading.Thread(target=agent.run)
            thread.daemon = True
            thread.start()
            self.active_threads.append((name, thread))
            print(f"Agente {name} iniciado.")
    
    def get_all_signals(self):
        """Obtém sinais de todos os agentes"""
        signals = {}
        for name, agent in self.agents.items():
            signal = agent.get_trading_signal()
            if signal:
                signals[name] = signal
        return signals
    
    def stop_all_agents(self):
        """Para todos os agentes"""
        for name, agent in self.agents.items():
            # Em uma implementação completa, adicionaria lógica para parar adequadamente
            print(f"Parando agente {name}...")