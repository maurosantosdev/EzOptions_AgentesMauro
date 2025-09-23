import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import time
import numpy as np
from agent_system import AgentSystem
from chart_utils import create_exposure_bar_chart
from trading_setups import SetupType

# --- Configuration ---
AGENT_CONFIG = {
    'name': 'EzOptions-Pro',
    'magic_number': 234001,
    'lot_size': 0.01,
    'risk_reward_ratio': 3.0,
}

# --- Custom CSS ---
def load_custom_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }

    .setup-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }

    .confidence-high {
        border-left: 4px solid #28a745;
    }

    .confidence-medium {
        border-left: 4px solid #ffc107;
    }

    .confidence-low {
        border-left: 4px solid #dc3545;
    }

    .status-active {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .status-inactive {
        background: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .status-analysis {
        background: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .confidence-bar {
        background: #e9ecef;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }

    .confidence-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }

    .sidebar-logo {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }

    .trading-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Initialize Session State ---
def initialize_session_state():
    defaults = {
        'refresh_rate': 30,
        'show_charts': True,
        'show_confidence': True,
        'alert_threshold': 60.0,
        'auto_refresh': True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_agent_controller():
    """Initialize and return the agent controller from session state."""
    if 'agent_controller' not in st.session_state:
        controller = AgentSystem(AGENT_CONFIG)
        controller.start()
        st.session_state.agent_controller = controller
    return st.session_state.agent_controller

def create_confidence_gauge(confidence, setup_name):
    """Create a confidence gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = confidence,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': setup_name, 'font': {'size': 14}},
        delta = {'reference': 60, 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': '#ffebee'},
                {'range': [60, 90], 'color': '#fff3e0'},
                {'range': [90, 100], 'color': '#e8f5e8'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )

    return fig

def create_pnl_chart(controller):
    """Create a P&L trend chart"""
    # Simulate some P&L data (in real implementation, fetch from trading history)
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    pnl_data = np.cumsum(np.random.randn(len(dates)) * 10) + controller.get_total_profit_loss()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=pnl_data,
        mode='lines',
        name='P&L',
        line=dict(color='#2a5298', width=2),
        fill='tonexty',
        fillcolor='rgba(42, 82, 152, 0.1)'
    ))

    fig.update_layout(
        title="P&L Evolution (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="P&L ($)",
        height=300,
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

def create_setup_overview_chart(setups_summary):
    """Create setup overview donut chart"""
    active_count = sum(1 for s in setups_summary.values() if s['active'])
    analysis_count = sum(1 for s in setups_summary.values() if s['can_analyze'] and not s['active'])
    inactive_count = len(setups_summary) - active_count - analysis_count

    labels = ['Active', 'Analysis Ready', 'Inactive']
    values = [active_count, analysis_count, inactive_count]
    colors = ['#28a745', '#ffc107', '#dc3545']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='inside'
    )])

    fig.update_layout(
        title="Setups Status Overview",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )

    return fig

def render_setup_card(setup_key, setup_result, setup_summary):
    """Render individual setup card"""
    setup_names = {
        'bullish_breakout': '🚀 Bullish Breakout',
        'bearish_breakout': '📉 Bearish Breakout',
        'pullback_top': '🔄 Pullback Top',
        'pullback_bottom': '🔄 Pullback Bottom',
        'consolidated_market': '🎯 Consolidated Market',
        'gamma_negative_protection': '🛡️ Gamma Protection'
    }

    confidence = setup_result.confidence
    is_active = setup_result.active
    can_analyze = setup_summary['can_analyze']
    can_operate = setup_summary['can_operate']
    risk_level = setup_result.risk_level

    # Determine card style based on confidence
    if confidence >= 90:
        card_class = "confidence-high"
    elif confidence >= 60:
        card_class = "confidence-medium"
    else:
        card_class = "confidence-low"

    # Status badge
    if is_active:
        status_html = '<span class="status-active">🟢 ACTIVE</span>'
    elif can_analyze:
        status_html = '<span class="status-analysis">🟡 ANALYSIS</span>'
    else:
        status_html = '<span class="status-inactive">🔴 INACTIVE</span>'

    # Confidence bar
    confidence_color = "#28a745" if confidence >= 90 else "#ffc107" if confidence >= 60 else "#dc3545"
    confidence_bar = f"""
    <div class="confidence-bar">
        <div class="confidence-fill" style="width: {confidence}%; background-color: {confidence_color};"></div>
    </div>
    """

    card_html = f"""
    <div class="setup-card {card_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h4 style="margin: 0; color: #2a5298;">{setup_names.get(setup_key, setup_key.title())}</h4>
            {status_html}
        </div>

        <div style="margin-bottom: 0.5rem;">
            <strong>Confidence: {confidence:.1f}%</strong>
            {confidence_bar}
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.875rem;">
            <div><strong>Risk:</strong> {risk_level}</div>
            <div><strong>Target:</strong> {setup_result.target_price:.2f if setup_result.target_price else 'N/A'}</div>
        </div>

        <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #6c757d;">
            {setup_result.details}
        </div>
    </div>
    """

    return card_html

def render_main_header(controller):
    """Render main dashboard header"""
    ny_tz = pytz.timezone("America/New_York")
    now_ny = datetime.now(ny_tz)
    is_trading = controller.is_trading_hours()
    connection_status = "🟢 Connected" if controller.is_mt5_connected() else "🔴 Disconnected"
    market_status = "🟢 OPEN" if is_trading else "🔴 CLOSED"

    header_html = f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 style="margin: 0; font-size: 2rem;">🤖 EzOptions Analytics Pro</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Advanced Options Flow Analysis & Trading</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.1rem; margin-bottom: 0.25rem;">
                    <strong>NY Time:</strong> {now_ny.strftime('%H:%M:%S')}
                </div>
                <div style="font-size: 1.1rem;">
                    <strong>Market:</strong> {market_status} | <strong>Status:</strong> {connection_status}
                </div>
            </div>
        </div>
    </div>
    """

    return header_html

def run_modern_dashboard():
    """Run the modern trading analytics dashboard"""
    st.set_page_config(
        page_title="EzOptions Analytics Pro",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🚀"
    )

    load_custom_css()
    initialize_session_state()
    controller = get_agent_controller()

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-logo"><h2>🚀 EzOptions</h2><p>Analytics Pro</p></div>', unsafe_allow_html=True)

        st.header("⚙️ Settings")
        st.session_state.refresh_rate = st.slider("Refresh Rate (seconds)", 10, 120, st.session_state.refresh_rate)
        st.session_state.show_charts = st.checkbox("Show Charts", st.session_state.show_charts)
        st.session_state.show_confidence = st.checkbox("Show Confidence Gauges", st.session_state.show_confidence)
        st.session_state.alert_threshold = st.slider("Alert Threshold (%)", 0.0, 100.0, st.session_state.alert_threshold)

        st.header("📊 Quick Stats")
        if controller.is_mt5_connected():
            st.metric("Balance", f"${controller.get_account_balance():,.2f}")
            st.metric("P&L", f"${controller.get_total_profit_loss():,.2f}")
            st.metric("Positions", controller.get_active_positions_count())
        else:
            st.warning("MT5 Not Connected")

    # Main content
    st.markdown(render_main_header(controller), unsafe_allow_html=True)

    # Account metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    is_ready = controller.is_mt5_connected()
    with col1:
        balance = controller.get_account_balance() if is_ready else 0
        st.metric("💰 Balance", f"${balance:,.2f}")

    with col2:
        equity = controller.get_account_equity() if is_ready else 0
        st.metric("📈 Equity", f"${equity:,.2f}")

    with col3:
        margin = controller.get_free_margin() if is_ready else 0
        st.metric("🏦 Free Margin", f"${margin:,.2f}")

    with col4:
        pnl = controller.get_total_profit_loss() if is_ready else 0
        pnl_delta = pnl
        st.metric("💵 P&L", f"${pnl:,.2f}", delta=f"{pnl_delta:,.2f}")

    with col5:
        positions = controller.get_active_positions_count() if is_ready else 0
        st.metric("📋 Positions", positions)

    # Main analysis section
    st.markdown("---")

    decision_output = controller.latest_decision

    if not decision_output:
        st.info("🔄 Aguardando primeira análise do sistema...")
        st.markdown(f"**Símbolo de Análise:** {controller.options_symbol}")
    else:
        setups_detailed = decision_output.get("setups_detailed", {})
        setups_summary = controller.get_setup_confidence_summary()

        if setups_detailed:
            # Overview row
            col1, col2 = st.columns([1, 1])

            with col1:
                # Setup overview chart
                overview_fig = create_setup_overview_chart(setups_summary)
                st.plotly_chart(overview_fig, use_container_width=True)

            with col2:
                # P&L trend chart
                pnl_fig = create_pnl_chart(controller)
                st.plotly_chart(pnl_fig, use_container_width=True)

            # Setups grid
            st.subheader("🎯 Trading Setups Analysis")

            # Create 3 columns for setup cards
            setup_cols = st.columns(3)
            col_index = 0

            for setup_key, setup_result in setups_detailed.items():
                with setup_cols[col_index]:
                    setup_summary = setups_summary[setup_key]
                    card_html = render_setup_card(setup_key, setup_result, setup_summary)
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Show confidence gauge if enabled
                    if st.session_state.show_confidence:
                        gauge_fig = create_confidence_gauge(setup_result.confidence,
                                                          setup_key.replace('_', ' ').title())
                        st.plotly_chart(gauge_fig, use_container_width=True, key=f"gauge_{setup_key}")

                col_index = (col_index + 1) % 3

            # Options flow analysis
            if st.session_state.show_charts:
                st.markdown("---")
                st.subheader("📊 Options Flow Analysis")

                calls_data = decision_output.get("calls")
                puts_data = decision_output.get("puts")
                current_price = decision_output.get("S")

                if calls_data is not None and puts_data is not None and current_price is not None:
                    # Create exposure charts
                    col1, col2 = st.columns(2)

                    with col1:
                        gex_fig = create_exposure_bar_chart(calls_data, puts_data, "GEX", "Gamma Exposure", current_price, height=400)
                        st.plotly_chart(gex_fig, use_container_width=True)

                    with col2:
                        if 'DELTA' in calls_data.columns:
                            delta_fig = create_exposure_bar_chart(calls_data, puts_data, "DELTA", "Delta Exposure", current_price, height=400)
                            st.plotly_chart(delta_fig, use_container_width=True)

                    # Additional analysis row
                    if 'CHARM' in calls_data.columns:
                        col1, col2 = st.columns(2)

                        with col1:
                            charm_fig = create_exposure_bar_chart(calls_data, puts_data, "CHARM", "Charm Exposure", current_price, height=300)
                            st.plotly_chart(charm_fig, use_container_width=True)

                        with col2:
                            if 'THETA' in calls_data.columns:
                                theta_fig = create_exposure_bar_chart(calls_data, puts_data, "THETA", "Theta Decay", current_price, height=300)
                                st.plotly_chart(theta_fig, use_container_width=True)

    # Auto refresh
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.refresh_rate)
        st.rerun()

if __name__ == "__main__":
    run_modern_dashboard()