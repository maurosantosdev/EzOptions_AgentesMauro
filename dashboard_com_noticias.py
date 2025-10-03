#!/usr/bin/env python3
"""
DASHBOARD COMPLETO COM NOTÍCIAS - VERSÃO INTEGRADA
Dashboard otimizado com análise de notícias em tempo real
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import dashboard_completo
    print("🚀 Iniciando Dashboard Completo com Notícias...")
    print("=" * 60)
    print()
    print("✅ Funcionalidades disponíveis:")
    print("  📊 Dashboard completo com todos os indicadores")
    print("  📰 Seção de notícias em tempo real")
    print("  🎯 Sistema de trailing stop")
    print("  🤖 15 agentes de análise")
    print("  💰 Monitoramento de conta real")
    print("  📈 Análise de setups")
    print()
    print("🌐 Abrindo dashboard na porta 8501...")
    print()

    # Iniciar o dashboard
    dashboard_completo.main()

except Exception as e:
    print(f"❌ Erro ao iniciar dashboard: {e}")
    print("Verifique se todas as dependências estão instaladas:")
    print("  pip install streamlit pandas plotly")