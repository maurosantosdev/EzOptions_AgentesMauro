#!/usr/bin/env python3
"""
EzOptions Analytics Pro - Auto Launch Web
=========================================

Launcher que abre automaticamente o dashboard no navegador com logs detalhados.
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path
import logging

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dashboard.log')
    ]
)

logger = logging.getLogger(__name__)

class WebDashboardLauncher:
    def __init__(self):
        self.streamlit_process = None
        self.port = 8501
        self.url = f"http://localhost:{self.port}"

    def check_requirements(self):
        """Verifica e instala dependências necessárias"""
        logger.info("🔍 Verificando dependências...")

        # Verificar se Streamlit está instalado
        try:
            import streamlit
            logger.info("✅ Streamlit já instalado")
        except ImportError:
            logger.info("⚠️ Streamlit não encontrado. Instalando...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info("✅ Streamlit instalado com sucesso")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Falha ao instalar Streamlit: {e}")
                return False

        # Verificar arquivos necessários
        required_files = ["modern_dashboard.py", "agent_system.py", "trading_setups.py"]
        for file in required_files:
            if not Path(file).exists():
                logger.error(f"❌ Arquivo necessário não encontrado: {file}")
                return False

        logger.info("✅ Todos os arquivos necessários encontrados")
        return True

    def find_available_port(self):
        """Encontra uma porta disponível"""
        import socket
        ports_to_try = [8501, 8502, 8503, 8504, 8505]

        for port in ports_to_try:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    self.port = port
                    self.url = f"http://localhost:{port}"
                    logger.info(f"✅ Porta {port} disponível")
                    return True
            except OSError:
                logger.warning(f"⚠️ Porta {port} ocupada")
                continue

        logger.error("❌ Nenhuma porta disponível encontrada")
        return False

    def start_streamlit(self):
        """Inicia o servidor Streamlit"""
        try:
            logger.info(f"🚀 Iniciando Streamlit na porta {self.port}...")

            cmd = [
                sys.executable, "-m", "streamlit", "run",
                "modern_dashboard.py",
                "--server.port", str(self.port),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false",
                "--server.address", "localhost"
            ]

            logger.info(f"🔧 Comando: {' '.join(cmd)}")

            # Iniciar processo em background
            self.streamlit_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            logger.info(f"✅ Processo Streamlit iniciado (PID: {self.streamlit_process.pid})")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Streamlit: {e}")
            return False

    def wait_for_server(self, timeout=30):
        """Aguarda o servidor ficar disponível"""
        import socket
        import time

        logger.info(f"⏳ Aguardando servidor ficar disponível em {self.url}...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', self.port))
                    if result == 0:
                        logger.info("✅ Servidor Streamlit está respondendo!")
                        return True
            except:
                pass

            # Verificar se processo ainda está rodando
            if self.streamlit_process and self.streamlit_process.poll() is not None:
                stdout, stderr = self.streamlit_process.communicate()
                logger.error(f"❌ Processo Streamlit terminou inesperadamente")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False

            time.sleep(1)
            print(".", end="", flush=True)

        logger.error(f"⏱️ Timeout aguardando servidor ({timeout}s)")
        return False

    def open_browser(self):
        """Abre o navegador automaticamente"""
        try:
            logger.info(f"🌐 Abrindo navegador: {self.url}")
            webbrowser.open(self.url)
            logger.info("✅ Navegador aberto com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao abrir navegador: {e}")
            logger.info(f"💡 Acesse manualmente: {self.url}")
            return False

    def monitor_process(self):
        """Monitor o processo Streamlit"""
        if not self.streamlit_process:
            return

        logger.info("📊 Monitorando processo Streamlit...")

        try:
            # Aguardar o processo terminar
            self.streamlit_process.wait()
        except KeyboardInterrupt:
            logger.info("⏹️ Interrompido pelo usuário")
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpa recursos"""
        logger.info("🧹 Limpando recursos...")

        if self.streamlit_process:
            try:
                self.streamlit_process.terminate()
                self.streamlit_process.wait(timeout=5)
                logger.info("✅ Processo Streamlit terminado")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Forçando término do processo...")
                self.streamlit_process.kill()
                self.streamlit_process.wait()
            except Exception as e:
                logger.error(f"❌ Erro ao terminar processo: {e}")

    def launch(self):
        """Executa o launcher completo"""
        logger.info("=" * 70)
        logger.info("🚀 EzOptions Analytics Pro - Web Launcher")
        logger.info("   Sistema Avançado de Análise de Opções")
        logger.info("=" * 70)

        try:
            # 1. Verificar requisitos
            if not self.check_requirements():
                logger.error("❌ Requisitos não atendidos")
                return False

            # 2. Encontrar porta disponível
            if not self.find_available_port():
                logger.error("❌ Porta não disponível")
                return False

            # 3. Iniciar Streamlit
            if not self.start_streamlit():
                logger.error("❌ Falha ao iniciar Streamlit")
                return False

            # 4. Aguardar servidor
            if not self.wait_for_server():
                logger.error("❌ Servidor não ficou disponível")
                return False

            # 5. Abrir navegador
            self.open_browser()

            logger.info("=" * 70)
            logger.info(f"✅ Dashboard disponível em: {self.url}")
            logger.info("📊 Recursos Disponíveis:")
            logger.info("   • 6 Setups de Trading Avançados")
            logger.info("   • Sistema de Confiança (90% análise / 60% operação)")
            logger.info("   • Interface Moderna com Gráficos Interativos")
            logger.info("   • Análise em Tempo Real de CHARM, DELTA, GAMMA")
            logger.info("   • Confirmação Price Action e VWAP")
            logger.info("=" * 70)
            logger.info("⏹️ Pressione Ctrl+C para parar o servidor")

            # 6. Monitorar processo
            self.monitor_process()

            return True

        except KeyboardInterrupt:
            logger.info("\n⏹️ Parando servidor...")
            return True
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Função principal"""
    launcher = WebDashboardLauncher()

    try:
        success = launcher.launch()
        if success:
            logger.info("✅ Dashboard executado com sucesso!")
        else:
            logger.error("❌ Falha na execução do dashboard!")
            return 1
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())