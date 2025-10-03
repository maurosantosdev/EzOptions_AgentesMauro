#!/usr/bin/env python3
"""
CONFIGURAÇÃO DE PALAVRAS-CHAVE PARA ANÁLISE DE NOTÍCIAS
Arquivo para personalizar as palavras-chave que o agente de notícias usa
"""

# Palavras-chave que indicam sentimento positivo (BULLISH)
BULLISH_KEYWORDS = [
    # Português
    'crescimento', 'aumento', 'alta', 'ganho', 'lucro', 'positivo',
    'melhora', 'recuperação', 'forte', 'robusto', 'sólido', 'excelente',
    'superávit', 'expansão', 'otimismo', 'confiança', 'dados positivos',
    'expectativas superadas', 'surpreende positivamente', 'bom desempenho',
    'resultado recorde', 'melhor que o esperado', 'dados fortes',

    # Inglês
    'growth', 'increase', 'rise', 'gain', 'profit', 'positive',
    'improvement', 'recovery', 'strong', 'robust', 'solid', 'excellent',
    'surplus', 'expansion', 'optimism', 'confidence', 'beat expectations',
    'better than expected', 'strong data', 'record results', 'bullish'
]

# Palavras-chave que indicam sentimento negativo (BEARISH)
BEARISH_KEYWORDS = [
    # Português
    'queda', 'baixa', 'perda', 'prejuízo', 'negativo', 'piora',
    'recessão', 'contração', 'fraco', 'preocupante', 'dados negativos',
    'expectativas frustradas', 'surpreende negativamente', 'mau desempenho',
    'pior que o esperado', 'dados fracos', 'desaceleração', 'crise',

    # Inglês
    'decline', 'drop', 'fall', 'loss', 'negative', 'worsen',
    'recession', 'contraction', 'weak', 'concerning', 'miss expectations',
    'disappointing', 'poor performance', 'worse than expected',
    'weak data', 'slowdown', 'crisis', 'bearish'
]

# Configurações de impacto
NEWS_IMPACT_SETTINGS = {
    'min_keywords_for_impact': 2,      # Mínimo de palavras-chave para considerar impacto
    'max_news_age_hours': 24,          # Considerar apenas notícias das últimas 24h
    'confidence_boost': 1.3,           # Multiplicador de confiança para sinais de notícias
    'min_impact_strength': 0.2         # Força mínima para influenciar decisões
}

def get_bullish_keywords():
    """Retorna lista de palavras-chave bullish"""
    return BULLISH_KEYWORDS

def get_bearish_keywords():
    """Retorna lista de palavras-chave bearish"""
    return BEARISH_KEYWORDS

def get_impact_settings():
    """Retorna configurações de impacto das notícias"""
    return NEWS_IMPACT_SETTINGS

# Exemplo de uso:
if __name__ == '__main__':
    print("Palavras-chave BULLISH:")
    for keyword in BULLISH_KEYWORDS[:10]:  # Mostra primeiras 10
        print(f"  • {keyword}")

    print(f"\nTotal de palavras-chave positivas: {len(BULLISH_KEYWORDS)}")

    print("\nPalavras-chave BEARISH:")
    for keyword in BEARISH_KEYWORDS[:10]:  # Mostra primeiras 10
        print(f"  • {keyword}")

    print(f"\nTotal de palavras-chave negativas: {len(BEARISH_KEYWORDS)}")

    print("\nConfigurações de impacto:")
    for key, value in NEWS_IMPACT_SETTINGS.items():
        print(f"  • {key}: {value}")