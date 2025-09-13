import subprocess
import sys
import logging

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def install_requirements():
    """Verifica e instala as dependências do requirements.txt."""
    logging.info("Verificando e instalando dependências...")
    try:
        # Usar DEVNULL para suprimir a saída do pip, a menos que haja um erro
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.PIPE)
        logging.info("Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao instalar dependências. Verifique o `requirements.txt` e sua conexão.")
        logging.error(f"Saída do Pip: {e.stderr.decode()}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro inesperado ao instalar dependências: {e}")
        sys.exit(1)

def run_streamlit_app(script_name):
    """Executa um script Streamlit especificado."""
    logging.info(f"Iniciando a aplicação Streamlit: {script_name}")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", script_name], check=True)
    except FileNotFoundError:
        logging.error("Comando 'streamlit' não encontrado. Verifique se o Streamlit está instalado corretamente.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro ao executar a aplicação Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 1. Garante que as dependências estão instaladas
    install_requirements()

    # 2. Escolha do Sistema a ser Executado
    #    Modifique a variável `SYSTEM_TO_RUN` para escolher qual sistema iniciar.
    #    Opções válidas: "AGENTS" ou "ORIGINAL"
    
    SYSTEM_TO_RUN = "AGENTS"
    # SYSTEM_TO_RUN = "ORIGINAL"

    # 3. Executa o sistema escolhido
    if SYSTEM_TO_RUN == "AGENTS":
        # Executa o novo dashboard que controla o sistema de agentes
        run_streamlit_app("agent_dashboard.py")
    elif SYSTEM_TO_RUN == "ORIGINAL":
        # Executa o dashboard de análise de opções original
        run_streamlit_app("ezoptions_set.py")
    else:
        logging.error(f"Valor inválido para SYSTEM_TO_RUN: '{SYSTEM_TO_RUN}'. Use 'AGENTS' ou 'ORIGINAL'.")