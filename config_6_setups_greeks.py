#!/usr/bin/env python3
"""
CONFIGURAÇÃO DOS 6 SETUPS + GREEKS PARA TRAILING STOP
Arquivo para personalizar os setups e parâmetros dos greeks
"""

# Configurações dos 6 Setups
SETUPS_CONFIG = {
    'bullish_breakout': {
        'enabled': True,
        'weight': 0.18,  # Peso na decisão
        'min_strength': 0.7,  # Força mínima para influenciar
        'description': 'Rompimento de alta com volume'
    },
    'bearish_breakout': {
        'enabled': True,
        'weight': 0.18,
        'min_strength': 0.7,
        'description': 'Rompimento de baixa com volume'
    },
    'pullback_top': {
        'enabled': True,
        'weight': 0.16,
        'min_strength': 0.6,
        'description': 'Pullback no topo com suporte'
    },
    'pullback_bottom': {
        'enabled': True,
        'weight': 0.16,
        'min_strength': 0.6,
        'description': 'Pullback no fundo com resistência'
    },
    'consolidated_market': {
        'enabled': True,
        'weight': 0.12,
        'min_strength': 0.5,
        'description': 'Mercado consolidado/range'
    },
    'gamma_negative_protection': {
        'enabled': True,
        'weight': 0.20,
        'min_strength': 0.8,
        'description': 'Proteção contra gamma negativo'
    }
}

# Configurações dos Greeks
GREEKS_CONFIG = {
    'delta': {
        'enabled': True,
        'weight': 0.35,  # Peso na decisão
        'calculation_method': 'trend_based',  # trend_based, volatility_based
        'sensitivity_threshold': 0.6,  # Threshold para influência
        'description': 'Sensibilidade ao movimento do preço'
    },
    'gamma': {
        'enabled': True,
        'weight': 0.40,
        'calculation_method': 'volatility_based',
        'sensitivity_threshold': 0.7,
        'description': 'Aceleração das mudanças de delta'
    },
    'charm': {
        'enabled': True,
        'weight': 0.25,
        'calculation_method': 'time_decay',
        'sensitivity_threshold': 0.5,
        'description': 'Decaimento do delta no tempo'
    }
}

# Configurações de Trailing Stop
TRAILING_CONFIG = {
    'target_price': 100.0,  # Preço alvo futuro
    'profit_target_pct': 2.0,  # 2% de lucro alvo

    # Distâncias base do trailing stop
    'base_distance': 30,  # Distância base em pontos
    'profit_thresholds': {
        'level_1': {'profit': 0.5, 'distance': 35},  # Lucro $0.5 = 35 pts
        'level_2': {'profit': 1.0, 'distance': 50},  # Lucro $1.0 = 50 pts
        'level_3': {'profit': 2.0, 'distance': 80},  # Lucro $2.0 = 80 pts
        'level_4': {'profit': 3.0, 'distance': 120}, # Lucro $3.0 = 120 pts
    },

    # Modificadores baseados em greeks
    'greeks_modifiers': {
        'high_favorability': 1.3,   # Greeks muito favoráveis
        'low_favorability': 0.7,    # Greeks desfavoráveis
        'neutral': 1.0              # Greeks neutros
    },

    # Modificadores baseados em setups
    'setups_modifiers': {
        'multiple_active': 1.2,      # Múltiplos setups ativos
        'single_active': 1.0,        # Setup único ativo
        'none_active': 0.8           # Nenhum setup ativo
    }
}

# Configurações de Stop Loss de Emergência
EMERGENCY_CONFIG = {
    'stop_loss_limit': -0.15,        # Stop loss em dólar
    'max_positions': 2,              # Máximo de posições simultâneas
    'lot_size': 0.02,                # Tamanho do lote
    'max_daily_loss': -15.0,         # Perda máxima diária
    'max_operations_per_day': 8      # Máximo de operações por dia
}

def get_setups_config():
    """Retorna configuração dos 6 setups"""
    return SETUPS_CONFIG

def get_greeks_config():
    """Retorna configuração dos greeks"""
    return GREEKS_CONFIG

def get_trailing_config():
    """Retorna configuração do trailing stop"""
    return TRAILING_CONFIG

def get_emergency_config():
    """Retorna configuração de emergência"""
    return EMERGENCY_CONFIG

# Exemplo de uso e teste
if __name__ == '__main__':
    print("=== CONFIGURAÇÃO DOS 6 SETUPS + GREEKS ===")
    print()

    print("📊 6 SETUPS CONFIGURADOS:")
    for setup, config in SETUPS_CONFIG.items():
        print(f"  ✅ {setup}: {config['description']}")
        print(f"     Peso: {config['weight']}, Min. Força: {config['min_strength']}")
    print()

    print("📈 GREEKS CONFIGURADOS:")
    for greek, config in GREEKS_CONFIG.items():
        print(f"  ✅ {greek.upper()}: {config['description']}")
        print(f"     Peso: {config['weight']}, Método: {config['calculation_method']}")
    print()

    print("🎯 TRAILING STOP CONFIGURADO:")
    print(f"  🎯 Preço Alvo: ${TRAILING_CONFIG['target_price']}")
    print(f"  📈 Meta de Lucro: {TRAILING_CONFIG['profit_target_pct']}%")
    print(f"  📏 Distância Base: {TRAILING_CONFIG['base_distance']} pontos")
    print()

    print("🛡️ EMERGÊNCIA CONFIGURADA:")
    print(f"  🛑 Stop Loss: ${EMERGENCY_CONFIG['stop_loss_limit']}")
    print(f"  📊 Máx Posições: {EMERGENCY_CONFIG['max_positions']}")
    print(f"  💰 Perda Diária Máx: ${EMERGENCY_CONFIG['max_daily_loss']}")