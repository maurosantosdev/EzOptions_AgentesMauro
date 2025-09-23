#!/usr/bin/env python3
"""
EzOptions Analytics Pro - Launcher Simples
==========================================

Launcher simples que abre o dashboard no navegador automaticamente.
"""

import os
import sys
import time
import subprocess
import webbrowser
import threading
from pathlib import Path

def log(message):
    """Print com timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    # Remove emojis para evitar problemas de encoding
    clean_message = message.encode('ascii', 'ignore').decode('ascii')
    print(f"[{timestamp}] {clean_message}")

def check_python():
    """Verifica Python"""
    log("🐍 Verificando Python...")
    try:
        version = sys.version.split()[0]
        log(f"✅ Python {version} encontrado")
        return True
    except Exception as e:
        log(f"❌ Erro no Python: {e}")
        return False

def install_streamlit():
    """Instala Streamlit se necessário"""
    log("📦 Verificando Streamlit...")

    try:
        import streamlit
        log("✅ Streamlit já instalado")
        return True
    except ImportError:
        log("⚠️ Instalando Streamlit...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "streamlit", "plotly", "--quiet"
            ])
            log("✅ Streamlit instalado com sucesso")
            return True
        except Exception as e:
            log(f"❌ Erro ao instalar Streamlit: {e}")
            return False

def start_dashboard():
    """Inicia o dashboard"""
    log("🚀 Iniciando dashboard...")

    try:
        # Comando para iniciar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "modern_dashboard.py",
            "--server.headless", "true"
        ]

        log(f"📝 Executando: {' '.join(cmd)}")

        # Iniciar processo
        process = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        log(f"✅ Processo iniciado (PID: {process.pid})")

        # Aguardar alguns segundos
        log("⏳ Aguardando servidor inicializar...")
        time.sleep(8)

        # Abrir navegador
        url = "http://localhost:8501"
        log(f"🌐 Abrindo navegador: {url}")
        webbrowser.open(url)

        log("=" * 60)
        log("✅ DASHBOARD ABERTO NO NAVEGADOR!")
        log(f"🔗 URL: {url}")
        log("📊 Recursos:")
        log("   • 6 Setups de Trading Implementados")
        log("   • Sistema de Confiança 90%/60%")
        log("   • Gráficos Interativos")
        log("   • Análise em Tempo Real")
        log("=" * 60)
        log("⏹️ Pressione Ctrl+C para parar")

        # Aguardar o processo
        try:
            process.wait()
        except KeyboardInterrupt:
            log("🛑 Parando servidor...")
            process.terminate()
            process.wait()

        return True

    except Exception as e:
        log(f"❌ Erro ao iniciar dashboard: {e}")
        return False

def fallback_dashboard():
    """Dashboard fallback no terminal"""
    log("🔄 Usando dashboard alternativo...")

    try:
        cmd = [sys.executable, "standalone_dashboard.py", "--mode", "continuous"]
        log("🚀 Iniciando dashboard no terminal...")
        subprocess.run(cmd)
        return True
    except Exception as e:
        log(f"❌ Erro no dashboard alternativo: {e}")
        return False

def main():
    """Função principal"""
    log("=" * 60)
    log("🚀 EzOptions Analytics Pro")
    log("   Launcher Automático")
    log("=" * 60)

    # Verificar Python
    if not check_python():
        input("Pressione Enter para sair...")
        return

    # Instalar Streamlit
    if not install_streamlit():
        log("⚠️ Falha no Streamlit. Usando dashboard alternativo...")
        fallback_dashboard()
        return

    # Iniciar dashboard web
    if not start_dashboard():
        log("⚠️ Falha no dashboard web. Usando alternativo...")
        fallback_dashboard()
        return

    log("✅ Execução concluída!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Interrompido pelo usuário")
    except Exception as e:
        log(f"❌ Erro crítico: {e}")
        input("Pressione Enter para sair...")