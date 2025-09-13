import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
from datetime import datetime
import pytz
import time
from agent_system import AgentSystem
from ezoptions import compute_greeks_and_charts, create_exposure_bar_chart

# --- Funções Auxiliares e de Inicialização ---

def auto_refresh(interval_seconds):
    """Força a atualização da página via JavaScript para manter os dados em tempo real."""
    js_code = f"""
        <script>
            setTimeout(function() {{
                window.location.reload();
            }}, {interval_seconds * 1000});
        </script>
    """
    html(js_code, height=0, width=0)

def initialize_session_state():
    """Inicializa as variáveis de estado da sessão para evitar erros."""
    defaults = {
        'call_color': '#2E8B57',  # SeaGreen
        'put_color': '#B22222',   # FireBrick
        'show_calls': True,
        'show_puts': True,
        'show_net': True,
        'chart_type': 'Bar',
        'gex_type': 'Absolute',
        'strike_range': 5.0,
        'chart_text_size': 12
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_agent_controller():
    """Gerencia a instância do controlador do agente no estado da sessão."""
    if 'agent_controller' not in st.session_state:
        st.info("Iniciando o controlador de agentes. A primeira carga pode levar um momento...")
        controller = AgentSystem()
        controller.start()
        st.session_state.agent_controller = controller
        time.sleep(7) # Pausa para dar tempo à thread de buscar a primeira data de expiração
        st.rerun()
    return st.session_state.agent_controller

# --- Renderização do Painel ---

def run_dashboard():
    """Executa a renderização completa do painel do Streamlit."""
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
    initialize_session_state()
    
    st.title("🤖 Painel de Controle dos Agentes de IA")

    with st.sidebar:
        st.header("Configurações do Dashboard")
        refresh_rate = st.slider("Taxa de Atualização (segundos)", 15, 300, 60, key="refresh_rate")

    controller = get_agent_controller()

    # --- Cabeçalho ---
    ny_tz = pytz.timezone("America/New_York")
    now_ny = datetime.now(ny_tz)
    is_trading = controller.is_trading_hours()
    status_color = "#28a745" if is_trading else "#ffc107"
    connection_status = "Conectado (MT5)" if controller.is_mt5_connected() else "Desconectado"
    market_status = "Aberto" if is_trading else "Fechado"

    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px; margin-bottom: 10px;"><h3>Horário NY: {now_ny.strftime('%H:%M:%S')}</h3></div>
        <div style="flex: 1; min-width: 200px; margin-bottom: 10px; text-align: center;"><h3>Mercado: <span style="color: {status_color};">{market_status}</span></h3></div>
        <div style="flex: 1; min-width: 200px; margin-bottom: 10px; text-align: right;"><h3>Conexão: <span style="color: #17a2b8;">{connection_status}</span></h3></div>
    </div><hr/>
    ''', unsafe_allow_html=True)

    # --- Cards de Métricas ---
    cols = st.columns(4)
    with cols[0]:
        st.metric("Saldo da Conta", f"${controller.get_account_balance():,.2f}")
    with cols[1]:
        st.metric("P&L Total", f"${controller.get_total_profit_loss():,.2f}")
    with cols[2]:
        st.metric("Posições Ativas", controller.get_active_positions_count())
    with cols[3]:
        st.metric("Taxa de Acertos", f"{controller.get_win_rate():.2f}%")

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Análise de Setups e Decisão do Agente ---
    st.subheader("📊 Análise de Setups e Decisão do Agente")
    
    options_ticker = controller.options_symbol
    expiry_date_str = controller.get_nearest_expiry()

    if not (controller.options_analysis_enabled and expiry_date_str):
        st.info("Aguardando dados de expiração ou análise de opções desabilitada.")
    else:
        decision_output = controller.make_decision(options_ticker, expiry_date_str)
        setups_status = decision_output["setups"]
        agent_decision = decision_output["decision"]
        target_price = decision_output.get("target_price")

        # --- Card de Decisão do Agente ---
        decision_color = "#50fa7b" if agent_decision == "BUY" else "#ff5555" if agent_decision == "SELL" else "#f1fa8c"
        decision_text = f"{agent_decision}" 
        if target_price:
            decision_text += f" @ {target_price:.2f}"

        st.markdown(f'''
        <div style="background-color: #282a36; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);">
            <h3 style="color: #f8f8f2; margin-bottom: 10px;">Decisão do Agente</h3>
            <p style="color: {decision_color}; font-size: 28px; font-weight: bold;">{decision_text}</p>
        </div>
        ''', unsafe_allow_html=True)

        # --- Gráficos dos Setups ---
        with st.spinner("Calculando gregos e gerando gráficos..."):
            @st.cache_data(ttl=60)
            def get_chart_data(ticker, expiry):
                return compute_greeks_and_charts(ticker, expiry, "dashboard_setups", controller.get_current_price())
            
            calls_processed, puts_processed, S_greeks, t_greeks, _, _ = get_chart_data(options_ticker, expiry_date_str)

        if calls_processed is not None and puts_processed is not None:
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
                    status = setups_status.get(key, {})
                    active = status.get('active', False)
                    details = status.get('details', 'N/A')
                    expander_title = f"Setup: {name} ({'Ativo' if active else 'Inativo'})"
                    
                    with st.expander(expander_title):
                        st.markdown(f"**Detalhes:** {details}")
                        # Reduzindo a altura dos gráficos para 350px
                        fig_gex = create_exposure_bar_chart(calls_processed, puts_processed, "GEX", "Gamma Exposure", S_greeks, height=350)
                        st.plotly_chart(fig_gex, use_container_width=True, key=f"gex_{key}")
                        fig_dex = create_exposure_bar_chart(calls_processed, puts_processed, "DEX", "Delta Exposure", S_greeks, height=350)
                        st.plotly_chart(fig_dex, use_container_width=True, key=f"dex_{key}")
                col_idx = (col_idx + 1) % 3
        else:
            st.warning("Não foi possível carregar os dados de opções para os setups.")

    # --- Atualização Automática ---
    auto_refresh(refresh_rate)

if __name__ == "__main__":
    run_dashboard()