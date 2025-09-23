import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import numpy as np
import random

# Configuração da página
st.set_page_config(
    page_title="EzOptions Analytics Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# CSS Customizado
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
</style>
""", unsafe_allow_html=True)

# Gerador de dados mock
class MockDataGenerator:
    def __init__(self):
        self.current_price = 450.50
        self.base_time = datetime.now()

    def get_account_data(self):
        return {
            'balance': 10000 + random.uniform(-500, 1500),
            'equity': 10000 + random.uniform(-500, 1500),
            'free_margin': 8000 + random.uniform(-300, 1000),
            'pnl': random.uniform(-200, 300),
            'positions': random.randint(0, 5)
        }

    def get_setups_data(self):
        setups = [
            'bullish_breakout',
            'bearish_breakout',
            'pullback_top',
            'pullback_bottom',
            'consolidated_market',
            'gamma_negative_protection'
        ]

        data = {}
        for setup in setups:
            confidence = random.uniform(30, 95)
            active = confidence >= 60
            can_analyze = confidence >= 90

            data[setup] = {
                'confidence': confidence,
                'active': active,
                'can_analyze': can_analyze,
                'risk_level': 'LOW' if confidence > 85 else 'MEDIUM' if confidence > 70 else 'HIGH',
                'target_price': self.current_price * (1 + random.uniform(-0.02, 0.02)),
                'details': f"Confiança: {confidence:.1f}% | Target: {self.current_price * (1 + random.uniform(-0.02, 0.02)):.2f}"
            }

        return data

# Inicializar dados
if 'data_generator' not in st.session_state:
    st.session_state.data_generator = MockDataGenerator()

# Função para criar gráficos
def create_confidence_gauge(confidence, setup_name):
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

def create_pnl_chart():
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    pnl_data = np.cumsum(np.random.randn(len(dates)) * 10) + random.uniform(-100, 300)

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

def create_setup_overview_chart(setups_data):
    active_count = sum(1 for s in setups_data.values() if s['active'])
    analysis_count = sum(1 for s in setups_data.values() if s['can_analyze'] and not s['active'])
    inactive_count = len(setups_data) - active_count - analysis_count

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

def render_header():
    header_html = f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 style="margin: 0; font-size: 2rem;">🚀 EzOptions Analytics Pro</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Advanced Options Flow Analysis & Trading</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.1rem; margin-bottom: 0.25rem;">
                    <strong>NY Time:</strong> {datetime.now().strftime('%H:%M:%S')}
                </div>
                <div style="font-size: 1.1rem;">
                    <strong>Market:</strong> 🟢 OPEN | <strong>Status:</strong> 🟢 Connected
                </div>
            </div>
        </div>
    </div>
    """
    return header_html

# Interface principal
def main():
    st.markdown(render_header(), unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown('<div style="text-align: center;"><h2>🚀 EzOptions</h2><p>Analytics Pro</p></div>', unsafe_allow_html=True)

        st.header("⚙️ Settings")
        refresh_rate = st.slider("Refresh Rate (seconds)", 10, 120, 30)
        show_charts = st.checkbox("Show Charts", True)
        show_confidence = st.checkbox("Show Confidence Gauges", True)
        alert_threshold = st.slider("Alert Threshold (%)", 0.0, 100.0, 60.0)

        st.header("📊 Quick Stats")
        account_data = st.session_state.data_generator.get_account_data()
        st.metric("Balance", f"${account_data['balance']:,.2f}")
        st.metric("P&L", f"${account_data['pnl']:,.2f}")
        st.metric("Positions", account_data['positions'])

    # Main content
    # Account metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    account_data = st.session_state.data_generator.get_account_data()

    with col1:
        st.metric("💰 Balance", f"${account_data['balance']:,.2f}")
    with col2:
        st.metric("📈 Equity", f"${account_data['equity']:,.2f}")
    with col3:
        st.metric("🏦 Free Margin", f"${account_data['free_margin']:,.2f}")
    with col4:
        st.metric("💵 P&L", f"${account_data['pnl']:,.2f}", delta=f"{account_data['pnl']:,.2f}")
    with col5:
        st.metric("📋 Positions", account_data['positions'])

    st.markdown("---")

    # Overview row
    col1, col2 = st.columns([1, 1])

    setups_data = st.session_state.data_generator.get_setups_data()

    with col1:
        overview_fig = create_setup_overview_chart(setups_data)
        st.plotly_chart(overview_fig, use_container_width=True)

    with col2:
        pnl_fig = create_pnl_chart()
        st.plotly_chart(pnl_fig, use_container_width=True)

    # Setups analysis
    st.subheader("🎯 Trading Setups Analysis")

    setup_names = {
        'bullish_breakout': '🚀 Bullish Breakout',
        'bearish_breakout': '📉 Bearish Breakout',
        'pullback_top': '🔄 Pullback Top',
        'pullback_bottom': '🔄 Pullback Bottom',
        'consolidated_market': '🎯 Consolidated Market',
        'gamma_negative_protection': '🛡️ Gamma Protection'
    }

    # Create 3 columns for setup cards
    setup_cols = st.columns(3)
    col_index = 0

    for setup_key, setup_data in setups_data.items():
        with setup_cols[col_index]:
            name = setup_names.get(setup_key, setup_key.title())
            confidence = setup_data['confidence']
            is_active = setup_data['active']
            can_analyze = setup_data['can_analyze']
            risk_level = setup_data['risk_level']

            # Determine card style
            if confidence >= 90:
                card_class = "confidence-high"
            elif confidence >= 60:
                card_class = "confidence-medium"
            else:
                card_class = "confidence-low"

            # Status
            if is_active:
                status_html = '<span class="status-active">🟢 ACTIVE</span>'
            else:
                status_html = '<span class="status-inactive">🔴 INACTIVE</span>'

            # Card HTML
            card_html = f"""
            <div class="setup-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; color: #2a5298;">{name}</h4>
                    {status_html}
                </div>

                <div style="margin-bottom: 0.5rem;">
                    <strong>Confidence: {confidence:.1f}%</strong>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.875rem;">
                    <div><strong>Risk:</strong> {risk_level}</div>
                    <div><strong>Target:</strong> {setup_data['target_price']:.2f}</div>
                </div>

                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #6c757d;">
                    {setup_data['details']}
                </div>
            </div>
            """

            st.markdown(card_html, unsafe_allow_html=True)

            # Show confidence gauge if enabled
            if show_confidence:
                gauge_fig = create_confidence_gauge(confidence, setup_key.replace('_', ' ').title())
                st.plotly_chart(gauge_fig, use_container_width=True, key=f"gauge_{setup_key}")

        col_index = (col_index + 1) % 3

    # System performance
    st.markdown("---")
    st.subheader("📊 System Performance")

    avg_confidence = sum(data['confidence'] for data in setups_data.values()) / len(setups_data)
    high_confidence = sum(1 for data in setups_data.values() if data['confidence'] >= 90)
    operational_ready = sum(1 for data in setups_data.values() if data['confidence'] >= 60)

    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

    with perf_col1:
        st.metric("Average Confidence", f"{avg_confidence:.1f}%")
    with perf_col2:
        st.metric("Analysis Ready", f"{high_confidence}/6")
    with perf_col3:
        st.metric("Operation Ready", f"{operational_ready}/6")
    with perf_col4:
        st.metric("System Health", "Operational")

    # Auto refresh
    time.sleep(refresh_rate)
    st.rerun()

if __name__ == "__main__":
    main()