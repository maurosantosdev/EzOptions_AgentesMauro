"""
Configuração do Sistema Lucrativo Otimizado
Arquivo separado para facilitar ajustes e manutenção
"""

# ============================================================================
# CONFIGURAÇÕES PRINCIPAIS DO SISTEMA
# ============================================================================

SYSTEM_CONFIG = {
    'name': 'SistemaLucrativoOtimizado',
    'symbol': 'US100',
    'magic_number': 234001,
    'lot_size': 0.015  # Lote menor para máxima segurança
}

# ============================================================================
# CONFIGURAÇÕES ULTRA-CONSERVADORAS (OTIMIZADAS PARA EVITAR PERDAS)
# ============================================================================

TRADING_CONFIG = {
    'min_confidence': 45.0,          # Confiança mínima reduzida para mais oportunidades
    'max_positions': 1,              # Apenas 1 posição por vez
    'stop_loss_pct': 0.08,           # Stop loss ultra-apertado (0.08%)
    'take_profit_pct': 0.4,          # Take profit menor (0.4%)
    'max_daily_loss': -5.0,          # Limite menor de perda (-$5)
    'max_operations_per_day': 5,     # Máximo 5 operações/dia
}

# ============================================================================
# CONFIGURAÇÕES DE GERENCIAMENTO DE RISCO
# ============================================================================

RISK_CONFIG = {
    'recovery_max_losses': 2,        # Máximo 2 perdas consecutivas para recuperação
    'recovery_multiplier': 1.2,      # Multiplicador conservador (1.2x)
    'max_lot_multiplier': 1.5,       # Máximo 1.5x o tamanho base
    'min_lot_size': 0.8,             # Mínimo 80% do tamanho base
    'loss_reduction_threshold': -3.0, # Reduzir lot se perda > $3
    'profit_increase_threshold': 10.0, # Aumentar lot se lucro > $10
}

# ============================================================================
# CONFIGURAÇÕES DE HORÁRIO OTIMIZADO
# ============================================================================

TIME_CONFIG = {
    'avoid_hours': [(12, 13), (15, 16)],  # Evitar almoço e fechamento
    'best_hours': [(9, 11), (14, 15)],    # Melhores horários para operar
    'min_operation_interval': 300,        # 5 minutos entre operações
    'trading_hours_start': 9,             # Início do horário de trading
    'trading_hours_end': 16,              # Fim do horário de trading
}

# ============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO CRUZADA
# ============================================================================

VALIDATION_CONFIG = {
    'cross_validation_required': True,    # Exigir validação cruzada
    'min_cross_validation_score': 0.7,    # Score mínimo de validação
    'min_signal_strength': 0.6,           # Força mínima do sinal (60%)
    'agent_correlation_threshold': 0.7,   # Correlação mínima entre agentes
    'min_volatility_threshold': 0.05,     # Volatilidade mínima (0.05%)
}

# ============================================================================
# CONFIGURAÇÕES DOS AGENTES
# ============================================================================

AGENTS_CONFIG = {
    'num_agents': 14,                     # Total de agentes
    'min_consensus': 3,                   # Mínimo 3 agentes concordando
    'confidence_weight': 0.6,             # Peso da confiança na decisão
    'correlation_bonus': 0.2,             # Bonus por correlação
    'greeks_weights': {                   # Pesos dos indicadores Greeks
        'gamma': 0.4,
        'delta': 0.35,
        'charm': 0.25
    }
}

# ============================================================================
# CONFIGURAÇÕES DE TRAILING STOP
# ============================================================================

TRAILING_CONFIG = {
    'min_profit_points': 50,              # Mínimo 50 pontos de lucro
    'trailing_distances': {               # Distâncias baseadas no lucro
        'level_1': 30,    # Até 100 pontos: 30 pontos trailing
        'level_2': 50,    # Até 200 pontos: 50 pontos trailing
        'level_3': 80,    # Até 300 pontos: 80 pontos trailing
        'level_4': 120    # Acima de 300 pontos: 120 pontos trailing
    }
}

# ============================================================================
# CONFIGURAÇÕES DE LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'log_file': 'sistema_lucrativo_otimizado.log',
    'log_level': 'INFO',
    'show_timestamp': True,
    'show_confidence': True,
    'show_pnl': True,
    'show_correlation': True,
}

# ============================================================================
# CONFIGURAÇÕES DE EMERGÊNCIA
# ============================================================================

EMERGENCY_CONFIG = {
    'emergency_stop_loss': -0.15,         # Stop loss de emergência
    'max_consecutive_losses': 3,          # Máximo 3 perdas consecutivas
    'emergency_cooldown': 3600,           # 1 hora de cooldown após emergência
    'force_close_all': True,              # Fechar todas as posições em emergência
}

# ============================================================================
# FUNÇÃO PARA CARREGAR TODAS AS CONFIGURAÇÕES
# ============================================================================

def get_all_configs():
    """Retorna todas as configurações em um único dicionário"""
    return {
        'system': SYSTEM_CONFIG,
        'trading': TRADING_CONFIG,
        'risk': RISK_CONFIG,
        'time': TIME_CONFIG,
        'validation': VALIDATION_CONFIG,
        'agents': AGENTS_CONFIG,
        'trailing': TRAILING_CONFIG,
        'logging': LOGGING_CONFIG,
        'emergency': EMERGENCY_CONFIG,
    }

def get_config(section=None):
    """Retorna configurações específicas ou todas"""
    if section:
        return get_all_configs().get(section.lower(), {})
    return get_all_configs()

# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

if __name__ == '__main__':
    # Exemplo de uso das configurações
    configs = get_all_configs()

    print("🚀 CONFIGURAÇÕES DO SISTEMA LUCRATIVO OTIMIZADO")
    print("=" * 60)

    for section, config in configs.items():
        print(f"\n📋 {section.upper()}:")
        for key, value in config.items():
            print(f"  {key}: {value}")

    print("\n✅ Configurações carregadas com sucesso!")