#!/usr/bin/env python3
"""
EzOptions Analytics Pro - Launcher
==================================

Script para executar o dashboard moderno do sistema de trading de opções.
Oferece opções para executar tanto o dashboard legado quanto o moderno.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_modern_dashboard():
    """Executa o dashboard moderno"""
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", "modern_dashboard.py"]
        print("Iniciando EzOptions Analytics Pro...")
        print("Dashboard sera aberto automaticamente no navegador")
        print("Configuracoes disponiveis na barra lateral")
        print("=" * 50)
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao iniciar o dashboard: {e}")
        return False
    except KeyboardInterrupt:
        print("\nDashboard interrompido pelo usuario")
        return True

def run_legacy_dashboard():
    """Executa o dashboard legado"""
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", "agent_dashboard.py"]
        print("Iniciando Dashboard Legado...")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao iniciar o dashboard legado: {e}")
        return False
    except KeyboardInterrupt:
        print("\nDashboard interrompido pelo usuario")
        return True

def run_simple_dashboard():
    """Executa o dashboard simples (sem dependências web)"""
    try:
        cmd = [sys.executable, "simple_dashboard.py", "--mode", "continuous"]
        print("Iniciando Dashboard Simples...")
        print("Dashboard sera executado no terminal")
        print("Pressione Ctrl+C para sair")
        print("=" * 50)
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao iniciar o dashboard simples: {e}")
        return False
    except KeyboardInterrupt:
        print("\nDashboard interrompido pelo usuario")
        return True

def run_standalone_dashboard():
    """Executa o dashboard standalone (apenas bibliotecas padrão)"""
    try:
        cmd = [sys.executable, "standalone_dashboard.py", "--mode", "continuous"]
        print("Iniciando Dashboard Standalone...")
        print("Modo demonstracao - dados simulados")
        print("Dashboard sera executado no terminal")
        print("Pressione Ctrl+C para sair")
        print("=" * 50)
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao iniciar o dashboard standalone: {e}")
        return False
    except KeyboardInterrupt:
        print("\nDashboard interrompido pelo usuario")
        return True

def check_requirements():
    """Verifica se os arquivos necessários existem"""
    required_files = [
        "modern_dashboard.py",
        "agent_dashboard.py",
        "simple_dashboard.py",
        "standalone_dashboard.py",
        "agent_system.py",
        "trading_setups.py",
        "greeks_calculator.py",
        "chart_utils.py"
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print("Arquivos necessarios nao encontrados:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    print("Todos os arquivos necessarios encontrados")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="EzOptions Analytics Pro - Sistema de Trading de Opções"
    )
    parser.add_argument(
        "--version",
        choices=["modern", "legacy", "simple", "standalone"],
        default="standalone",
        help="Versão do dashboard para executar (default: standalone)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Apenas verifica os requisitos sem executar"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("EzOptions Analytics Pro")
    print("   Sistema Avancado de Analise de Opcoes")
    print("=" * 60)

    # Verificar requisitos
    if not check_requirements():
        print("\nVerifique se todos os arquivos estao presentes e tente novamente.")
        sys.exit(1)

    if args.check:
        print("Sistema pronto para execucao!")
        return

    # Executar dashboard
    if args.version == "modern":
        print("\nExecutando Dashboard Moderno com:")
        print("   - 6 Setups de Trading Avancados")
        print("   - Sistema de Confianca (90% analise / 60% operacao)")
        print("   - Interface Moderna com Metricas em Tempo Real")
        print("   - Analise Completa de CHARM, DELTA e GAMMA")
        print("   - Confirmacao Price Action e VWAP")
        success = run_modern_dashboard()
    elif args.version == "legacy":
        print("\nExecutando Dashboard Legado...")
        success = run_legacy_dashboard()
    elif args.version == "simple":
        print("\nExecutando Dashboard Simples com:")
        print("   - 6 Setups de Trading Avancados")
        print("   - Sistema de Confianca (90% analise / 60% operacao)")
        print("   - Interface Terminal (sem dependencias web)")
        print("   - Analise Completa em Tempo Real")
        print("   - Atualizacao Automatica a cada 30s")
        success = run_simple_dashboard()
    else:  # standalone
        print("\nExecutando Dashboard Standalone com:")
        print("   - 6 Setups de Trading Avancados")
        print("   - Sistema de Confianca (90% analise / 60% operacao)")
        print("   - Interface Terminal (apenas bibliotecas padrao)")
        print("   - Dados simulados para demonstracao")
        print("   - Sem dependencias externas")
        success = run_standalone_dashboard()

    if success:
        print("\nDashboard executado com sucesso!")
    else:
        print("\nFalha na execucao do dashboard!")
        sys.exit(1)

if __name__ == "__main__":
    main()