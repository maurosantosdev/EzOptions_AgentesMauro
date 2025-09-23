#!/usr/bin/env python3
"""
EzOptions Analytics Pro - Simple Dashboard
==========================================

Dashboard básico que funciona sem Streamlit, apenas com Flask ou output direto.
Para situações onde as dependências não podem ser instaladas facilmente.
"""

import sys
import os
import time
import json
from datetime import datetime
import threading
from agent_system import AgentSystem

# Configuração do Agente
AGENT_CONFIG = {
    'name': 'EzOptions-Pro-Simple',
    'magic_number': 234001,
    'lot_size': 0.01,
    'risk_reward_ratio': 3.0,
}

class SimpleDashboard:
    def __init__(self):
        self.controller = None
        self.running = False

    def initialize_agent(self):
        """Inicializa o controller do agente"""
        try:
            print("Inicializando sistema de agentes...")
            self.controller = AgentSystem(AGENT_CONFIG)
            self.controller.start()
            print("✓ Sistema inicializado com sucesso!")
            return True
        except Exception as e:
            print(f"✗ Erro ao inicializar sistema: {e}")
            return False

    def print_header(self):
        """Imprime o cabeçalho do dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 80)
        print("🚀 EzOptions Analytics Pro - Simple Dashboard")
        print("   Sistema Avançado de Análise de Opções")
        print("=" * 80)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")

    def print_account_info(self):
        """Imprime informações da conta"""
        if not self.controller or not self.controller.is_mt5_connected():
            print("❌ MT5 não conectado")
            return

        print("💰 INFORMAÇÕES DA CONTA")
        print("-" * 40)
        print(f"Saldo:          ${self.controller.get_account_balance():,.2f}")
        print(f"Equity:         ${self.controller.get_account_equity():,.2f}")
        print(f"Margem Livre:   ${self.controller.get_free_margin():,.2f}")
        print(f"P&L Aberto:     ${self.controller.get_total_profit_loss():,.2f}")
        print(f"Posições:       {self.controller.get_active_positions_count()}")
        print("")

    def print_market_status(self):
        """Imprime status do mercado"""
        is_trading = self.controller.is_trading_hours() if self.controller else False
        connection = "Conectado" if (self.controller and self.controller.is_mt5_connected()) else "Desconectado"
        market = "🟢 ABERTO" if is_trading else "🔴 FECHADO"

        print("📊 STATUS DO MERCADO")
        print("-" * 40)
        print(f"Conexão MT5:    {connection}")
        print(f"Status Mercado: {market}")
        print(f"Horário Trading: {'Sim' if is_trading else 'Não'}")
        print("")

    def print_setups_analysis(self):
        """Imprime análise dos setups"""
        if not self.controller:
            return

        print("🎯 ANÁLISE DOS SETUPS DE TRADING")
        print("-" * 50)

        decision_output = self.controller.latest_decision
        if not decision_output:
            print("⏳ Aguardando primeira análise do sistema...")
            return

        setups_detailed = decision_output.get("setups_detailed", {})
        if not setups_detailed:
            print("📊 Usando análise legada...")
            setups = decision_output.get("setups", {})
            for setup_name, setup_data in setups.items():
                if isinstance(setup_data, tuple) and len(setup_data) >= 2:
                    active, details = setup_data[0], setup_data[1]
                    status = "🟢 ATIVO" if active else "🔴 INATIVO"
                    print(f"{setup_name.replace('_', ' ').title()}: {status}")
                    print(f"  Detalhes: {details}")
            return

        # Análise detalhada dos novos setups
        setup_names = {
            'bullish_breakout': '🚀 Bullish Breakout',
            'bearish_breakout': '📉 Bearish Breakout',
            'pullback_top': '🔄 Pullback Top',
            'pullback_bottom': '🔄 Pullback Bottom',
            'consolidated_market': '🎯 Mercado Consolidado',
            'gamma_negative_protection': '🛡️ Proteção Gamma'
        }

        active_count = 0
        analysis_count = 0

        for setup_key, setup_result in setups_detailed.items():
            name = setup_names.get(setup_key, setup_key.title())
            confidence = setup_result.confidence
            is_active = setup_result.active
            risk_level = setup_result.risk_level

            if is_active:
                status = "🟢 ATIVO"
                active_count += 1
            elif confidence >= 90:
                status = "🟡 ANÁLISE"
                analysis_count += 1
            else:
                status = "🔴 INATIVO"

            print(f"{name}")
            print(f"  Status:     {status}")
            print(f"  Confiança:  {confidence:.1f}%")
            print(f"  Risco:      {risk_level}")
            if setup_result.target_price:
                print(f"  Target:     {setup_result.target_price:.2f}")
            print(f"  Detalhes:   {setup_result.details}")
            print("")

        print(f"📈 RESUMO: {active_count} Ativos | {analysis_count} Análise | {6-active_count-analysis_count} Inativos")
        print("")

    def print_confidence_summary(self):
        """Imprime resumo de confiança"""
        if not self.controller:
            return

        summary = self.controller.get_setup_confidence_summary()
        if not summary:
            return

        print("📊 RESUMO DE CONFIANÇA")
        print("-" * 40)

        high_confidence = sum(1 for s in summary.values() if s['confidence'] >= 90)
        medium_confidence = sum(1 for s in summary.values() if 60 <= s['confidence'] < 90)
        low_confidence = sum(1 for s in summary.values() if s['confidence'] < 60)

        print(f"Alta Confiança (90%+):   {high_confidence}/6 setups")
        print(f"Média Confiança (60%+):  {medium_confidence}/6 setups")
        print(f"Baixa Confiança (<60%):  {low_confidence}/6 setups")
        print("")

        avg_confidence = sum(s['confidence'] for s in summary.values()) / len(summary) if summary else 0
        print(f"Confiança Média Total: {avg_confidence:.1f}%")
        print("")

    def run_continuous(self):
        """Executa dashboard em modo contínuo"""
        self.running = True

        if not self.initialize_agent():
            return

        try:
            while self.running:
                self.print_header()
                self.print_account_info()
                self.print_market_status()
                self.print_setups_analysis()
                self.print_confidence_summary()

                print("⚙️  CONTROLES")
                print("-" * 20)
                print("Pressione Ctrl+C para sair")
                print("Atualizando a cada 30 segundos...")
                print("")
                print("=" * 80)

                time.sleep(30)

        except KeyboardInterrupt:
            print("\n🛑 Dashboard interrompido pelo usuário")
        finally:
            self.cleanup()

    def run_single(self):
        """Executa dashboard uma única vez"""
        if not self.initialize_agent():
            return

        # Aguarda alguns segundos para primeira análise
        print("⏳ Aguardando análise inicial...")
        time.sleep(10)

        try:
            self.print_header()
            self.print_account_info()
            self.print_market_status()
            self.print_setups_analysis()
            self.print_confidence_summary()
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpa recursos"""
        self.running = False
        if self.controller:
            self.controller.shutdown()
        print("✓ Sistema finalizado")

def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description="EzOptions Simple Dashboard")
    parser.add_argument("--mode", choices=["single", "continuous"], default="single",
                       help="Modo de execução (single=uma vez, continuous=contínuo)")

    args = parser.parse_args()

    dashboard = SimpleDashboard()

    print("EzOptions Analytics Pro - Simple Dashboard")
    print("=========================================")
    print("")

    if args.mode == "continuous":
        print("🔄 Modo Contínuo - Atualizações a cada 30 segundos")
        dashboard.run_continuous()
    else:
        print("📸 Modo Single - Análise única")
        dashboard.run_single()

if __name__ == "__main__":
    main()