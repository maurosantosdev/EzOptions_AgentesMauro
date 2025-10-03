"""
INICIAR SISTEMA DE AGENTES COMPLETO
==================================

Este script inicia todos os agentes necessários para o sistema funcionar corretamente.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from datetime import datetime

def iniciar_agente(nome, comando, porta_http=None, porta_ws=None):
    """Inicia um agente específico"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 INICIANDO {nome}...")
        
        # Criar processo
        processo = subprocess.Popen(
            comando,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {nome} INICIADO (PID: {processo.pid})")
        
        if porta_http:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 HTTP: http://localhost:{porta_http}")
        if porta_ws:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 WebSocket: ws://localhost:{porta_ws}")
            
        return processo
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ERRO AO INICIAR {nome}: {e}")
        return None

def parar_agente(processo, nome):
    """Para um agente específico"""
    try:
        if processo and processo.poll() is None:  # Se ainda estiver rodando
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 PARANDO {nome}...")
            processo.terminate()
            processo.wait(timeout=5)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {nome} PARADO")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {nome} JÁ ESTAVA PARADO")
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {nome} NÃO RESPONDEU - FORÇANDO ENCERRAMENTO...")
        processo.kill()
        processo.wait()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {nome} ENCERRADO FORÇADAMENTE")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ERRO AO PARAR {nome}: {e}")

def main():
    """Função principal para iniciar todos os agentes"""
    print("=" * 60)
    print("🚀 SISTEMA DE AGENTES COMPLETO - EZOPTIONS")
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando sistema de agentes...")
    print()
    
    # Lista de processos para controle
    processos = []
    
    try:
        # 1. INICIAR AGENTE DE EMERGENCY STOP LOSS (SEMPRE PRIMEIRO)
        print("1. INICIANDO AGENTE DE EMERGENCY STOP LOSS...")
        emergency_process = iniciar_agente(
            "EMERGENCY STOP LOSS",
            "python emergency_stop_loss.py",
            porta_http=8001
        )
        if emergency_process:
            processos.append(("EMERGENCY STOP LOSS", emergency_process))
            time.sleep(3)  # Esperar inicialização
        
        # 2. INICIAR SISTEMA DE LUCRO FINAL (SEGUNDO)
        print("\n2. INICIANDO SISTEMA DE LUCRO FINAL...")
        lucro_process = iniciar_agente(
            "LUCRO FINAL",
            "python sistema_lucro_final.py",
            porta_http=8002
        )
        if lucro_process:
            processos.append(("LUCRO FINAL", lucro_process))
            time.sleep(3)  # Esperar inicialização
        
        # 3. INICIAR DASHBOARD COMPLETO (POR ÚLTIMO)
        print("\n3. INICIANDO DASHBOARD COMPLETO...")
        dashboard_process = iniciar_agente(
            "DASHBOARD COMPLETO",
            "python -m streamlit run dashboard_completo.py --server.port 8502",
            porta_http=8502
        )
        if dashboard_process:
            processos.append(("DASHBOARD COMPLETO", dashboard_process))
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS AGENTES FORAM INICIADOS!")
        print("=" * 60)
        print("📊 STATUS DOS AGENTES:")
        for nome, processo in processos:
            status = "✅ RODANDO" if processo and processo.poll() is None else "❌ PARADO"
            print(f"   - {nome}: {status} (PID: {processo.pid if processo else 'N/A'})")
        
        print("\n🚀 SISTEMA OPERACIONAL!")
        print("🔗 Acesse o Dashboard: http://localhost:8502")
        print("⚠️  Pressione Ctrl+C para parar todos os agentes")
        print("=" * 60)
        
        # Manter o script rodando e monitorar os processos
        try:
            while True:
                # Verificar se algum processo parou inesperadamente
                for nome, processo in processos:
                    if processo and processo.poll() is not None:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {nome} PAROU INESPERADAMENTE!")
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 REINICIANDO {nome}...")
                        # Aqui você pode adicionar lógica para reiniciar automaticamente
                        
                time.sleep(5)  # Verificar a cada 5 segundos
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 CTRL+C DETECTADO - PARANDO TODOS OS AGENTES...")
            
            # Parar todos os processos em ordem inversa
            for nome, processo in reversed(processos):
                parar_agente(processo, nome)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ TODOS OS AGENTES PARADOS!")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 👋 SISTEMA ENCERRADO!")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ERRO CRÍTICO: {e}")
        # Parar todos os processos em caso de erro
        for nome, processo in reversed(processos):
            parar_agente(processo, nome)

if __name__ == "__main__":
    main()