#!/usr/bin/env python3
"""
EzOptions Analytics Pro - Dashboard Launcher
============================================

Launcher que abre automaticamente o dashboard no navegador.
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
    print(f"[{timestamp}] {message}")

def check_python():
    """Verifica Python"""
    log("Verificando Python...")
    try:
        version = sys.version.split()[0]
        log(f"OK - Python {version} encontrado")
        return True
    except Exception as e:
        log(f"ERRO - Problema no Python: {e}")
        return False

def install_streamlit():
    """Instala Streamlit se necessário"""
    log("Verificando Streamlit...")

    try:
        import streamlit
        log("OK - Streamlit ja instalado")
        return True
    except ImportError:
        log("AVISO - Instalando Streamlit...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "streamlit", "plotly", "--quiet"
            ])
            log("OK - Streamlit instalado com sucesso")
            return True
        except Exception as e:
            log(f"ERRO - Falha ao instalar Streamlit: {e}")
            return False

def start_dashboard():
    """Inicia o dashboard"""
    log("Iniciando dashboard web...")

    try:
        # Comando para iniciar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "web_dashboard.py",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]

        log(f"Executando comando: {' '.join(cmd)}")

        # Iniciar processo
        process = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        log(f"OK - Processo iniciado (PID: {process.pid})")

        # Aguardar servidor inicializar
        log("Aguardando servidor inicializar...")
        time.sleep(10)

        # Verificar se processo ainda está rodando
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            log(f"ERRO - Processo terminou inesperadamente")
            log(f"STDOUT: {stdout}")
            log(f"STDERR: {stderr}")
            return False

        # Abrir navegador
        url = "http://localhost:8501"
        log(f"Abrindo navegador: {url}")
        webbrowser.open(url)

        print("=" * 70)
        log("SUCESSO - DASHBOARD ABERTO NO NAVEGADOR!")
        print(f"URL: {url}")
        print("Recursos disponíveis:")
        print("  * 6 Setups de Trading Implementados")
        print("  * Sistema de Confianca 90%/60%")
        print("  * Graficos Interativos")
        print("  * Analise em Tempo Real")
        print("=" * 70)
        print("Pressione Ctrl+C para parar o servidor")

        # Aguardar o processo
        try:
            process.wait()
        except KeyboardInterrupt:
            log("Parando servidor...")
            process.terminate()
            process.wait()

        return True

    except Exception as e:
        log(f"ERRO - Falha ao iniciar dashboard: {e}")
        return False

def fallback_dashboard():
    """Dashboard fallback no terminal"""
    log("Usando dashboard alternativo no terminal...")

    try:
        cmd = [sys.executable, "standalone_dashboard.py", "--mode", "continuous"]
        log("Iniciando dashboard no terminal...")
        subprocess.run(cmd)
        return True
    except Exception as e:
        log(f"ERRO - Falha no dashboard alternativo: {e}")
        return False

def check_files():
    """Verifica arquivos necessários"""
    log("Verificando arquivos necessarios...")

    required_files = [
        "web_dashboard.py",
        "standalone_dashboard.py"
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        log(f"ERRO - Arquivos nao encontrados: {', '.join(missing)}")
        return False

    log("OK - Todos os arquivos encontrados")
    return True

def main():
    """Função principal"""
    print("=" * 70)
    print("      EzOptions Analytics Pro - Dashboard Launcher")
    print("=" * 70)

    # Verificar arquivos
    if not check_files():
        input("Pressione Enter para sair...")
        return

    # Verificar Python
    if not check_python():
        input("Pressione Enter para sair...")
        return

    # Instalar Streamlit
    if not install_streamlit():
        log("AVISO - Falha no Streamlit. Usando dashboard alternativo...")
        fallback_dashboard()
        return

    # Iniciar dashboard web
    if not start_dashboard():
        log("AVISO - Falha no dashboard web. Usando alternativo...")
        fallback_dashboard()
        return

    log("Execucao concluida!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrompido pelo usuario")
    except Exception as e:
        log(f"ERRO CRITICO: {e}")
        input("Pressione Enter para sair...")