import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time
from agent_system import AgentSystem
from chart_utils import create_exposure_bar_chart

# --- Configuração do Agente Padrão ---
AGENT_CONFIG = {
    'name': 'Agent-Standard',
    'magic_number': 234001,
    'lot_size': 0.01,
    'risk_reward_ratio': 3.0,
}

# --- Funções Auxiliares e de Inicialização ---
def initialize_session_state():
    defaults = {
        'call_color': '#2E8B57',
        'put_color': '#B22222',
        'show_calls': True,
        'show_puts': True,
        'show_net': True,
        'chart_type': 'Bar',
        'gex_type': 'Absolute',
        'strike_range': 5.0,
        'chart_text_size': 12,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_agent_controller():
    """Initializes and returns the agent controller from session state."""
    if 'agent_controller' not in st.session_state:
        # Starts the agent thread in the background and immediately returns.
        # The dashboard will update asynchronously.
        controller = AgentSystem(AGENT_CONFIG)
        controller.start()
        st.session_state.agent_controller = controller
    return st.session_state.agent_controller

# --- Renderização do Painel ---
def run_dashboard():
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
    initialize_session_state()
    
    st.title("🤖 Painel de Controle do Agente de IA")

    with st.sidebar:
        st.header("Configurações do Dashboard")
        refresh_rate = st.slider("Taxa de Atualização (segundos)", 10, 120, 30, key="refresh_rate")

    controller = get_agent_controller()

    # --- Cabeçalho ---
    # These will display immediately and update on each refresh.
    ny_tz = pytz.timezone("America/New_York")
    now_ny = datetime.now(ny_tz)
    is_trading = controller.is_trading_hours()
    status_color = "#28a745" if is_trading else "#ffc107"
    connection_status = "Conectado" if controller.is_mt5_connected() else "Desconectado"
    market_status = "Aberto" if is_trading else "Fechado"

    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px; margin-bottom: 10px;"><h3>Horário NY: {now_ny.strftime('%H:%M:%S')}</h3></div>
        <div style="flex: 1; min-width: 200px; margin-bottom: 10px; text-align: center;"><h3>Mercado: <span style="color: {status_color};">{market_status}</span></h3></div>
        <div style="flex: 1; min-width: 200px; margin-bottom: 10px; text-align: right;"><h3>Conexão: <span style="color: #17a2b8;">{connection_status}</span></h3></div>
    </div><hr/>
    ''', unsafe_allow_html=True)

    # --- Cards de Métricas ---
    # These will show "Carregando..." initially and populate as the agent provides data.
    is_ready = controller.is_mt5_connected()
    balance = f"${controller.get_account_balance():,.2f}" if is_ready else "Carregando..."
    equity = f"${controller.get_account_equity():,.2f}" if is_ready else "Carregando..."
    margin = f"${controller.get_free_margin():,.2f}" if is_ready else "Carregando..."
    pnl = f"${controller.get_total_profit_loss():,.2f}" if is_ready else "Carregando..."
    positions = controller.get_active_positions_count() if is_ready else "Carregando..."

    cols = st.columns(5)
    cols[0].metric("Saldo", balance)
    cols[1].metric("Capital Líquido", equity)
    cols[2].metric("Margem Livre", margin)
    cols[3].metric("P&L Aberto", pnl)
    cols[4].metric("Posições Ativas", positions)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Análise de Setups e Decisão do Agente ---
    st.subheader("📊 Análise de Setups e Decisão do Agente")
    
    decision_output = controller.latest_decision

    if not decision_output:
        st.info(f"Aguardando a primeira análise do agente para {controller.options_symbol}... O painel será atualizado automaticamente.")
    else:
        setups_status = decision_output.get("setups", {})
        calls_processed = decision_output.get("calls")
        puts_processed = decision_output.get("puts")
        S_greeks = decision_output.get("S")

        if calls_processed is not None and puts_processed is not None and S_greeks is not None:
            setup_cols = st.columns(3)
            setup_map = {
                "bullish_breakout": "Bullish Breakout",
                "bearish_breakout": "Bearish Breakout",
                "pullback_top": "Pullback no Topo",
                "pullback_bottom": "Pullback no Fundo",
                "consolidated_market": "Mercado Consolidado",
                "gamma_negative_protection": "Proteção Gamma Negativo"
            }
            
            col_idx = 0
            for key, name in setup_map.items():
                with setup_cols[col_idx]:
                    # FIX: Unpack the tuple directly
                    status_tuple = setups_status.get(key, (False, 'N/A', None, None))
                    active = status_tuple[0]
                    details = status_tuple[1]
                    expander_title = f"Setup: {name} ({'Ativo' if active else 'Inativo'})"
                    
                    with st.expander(expander_title):
                        st.markdown(f"**Detalhes:** {details}")
                        fig_gex = create_exposure_bar_chart(calls_processed, puts_processed, "GEX", "Gamma Exposure", S_greeks, height=350)
                        st.plotly_chart(fig_gex, use_container_width=True, key=f"gex_{key}")
                col_idx = (col_idx + 1) % 3
        else:
            st.warning("Dados de opções ainda não disponíveis na última análise do agente.")

    # --- Atualização Automática ---
    time.sleep(refresh_rate)
    st.rerun()

if __name__ == "__main__":
    run_dashboard()
