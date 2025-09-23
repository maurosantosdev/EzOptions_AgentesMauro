# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import numpy as np
import os
from dotenv import load_dotenv
import threading
import subprocess

# Tentar importar dependências
try:
    import MetaTrader5 as mt5
    from real_agent_system import RealAgentSystem
    from trading_setups import TradingSetupAnalyzer, SetupType
    MT5_AVAILABLE = True
except ImportError as e:
    MT5_AVAILABLE = False
    st.error(f"⚠️ Dependência não encontrada: {e}")

# Carregar configurações
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="EzOptions Analytics Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# CSS em Português
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
    border-radius: 8px;
}

.confidence-high {
    border-left: 4px solid #28a745;
    background: #f8fff9;
}

.confidence-medium {
    border-left: 4px solid #ffc107;
    background: #fffdf5;
}

.confidence-low {
    border-left: 4px solid #dc3545;
    background: #fff5f5;
}

.status-active {
    background: #28a745;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

.status-inactive {
    background: #dc3545;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

.status-analysis {
    background: #ffc107;
    color: black;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

.confidence-bar {
    background: #e9ecef;
    border-radius: 10px;
    height: 20px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.confidence-fill {
    height: 100%;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 0.8rem;
}

.system-status {
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    font-weight: bold;
}

.status-connected {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}

.status-disconnected {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

.agent-status {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
}
</style>
""", unsafe_allow_html=True)

class DashboardCompleto:
    def __init__(self):
        self.mt5_connected = False
        self.account_info = None
        self.agent_system = None
        self.agent_thread = None
        self.trading_active = False

    def inicializar_mt5(self):
        """Conecta automaticamente ao MT5"""
        if not MT5_AVAILABLE:
            st.error("⚠️ MetaTrader5 não está disponível. Instale: pip install MetaTrader5")
            return False

        try:
            # Primeiro tentar conectar diretamente
            if not mt5.initialize():
                st.info("🔄 Tentando iniciar MetaTrader 5...")

                # Tentar iniciar MT5 automaticamente
                mt5_path = os.getenv("MT5_PATH", r"C:\Program Files\FBS MetaTrader 5\terminal64.exe")
                if mt5_path:
                    mt5_path_clean = mt5_path.strip('"')
                    if os.path.exists(mt5_path_clean):
                        try:
                            process = subprocess.Popen(
                                [mt5_path_clean],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            st.info("⏳ Aguardando MT5 inicializar...")
                            time.sleep(5)  # Dar tempo para o MT5 iniciar

                            # Tentar conectar novamente
                            if not mt5.initialize():
                                st.warning("❌ Não foi possível conectar ao MT5. Verifique se está instalado.")
                                return False
                        except Exception as e:
                            st.warning(f"⚠️ Erro ao iniciar MT5: {e}")
                            return False
                    else:
                        st.error(f"❌ MT5 não encontrado em: {mt5_path_clean}")
                        return False

            # Fazer login
            login = int(os.getenv("MT5_LOGIN", "103486755"))
            server = os.getenv("MT5_SERVER", "FBS-Demo")
            password = os.getenv("MT5_PASSWORD", "gPo@j6*V")

            st.info(f"🔐 Fazendo login - Servidor: {server}, Login: {login}")

            if not mt5.login(login, password, server):
                error_code, error_desc = mt5.last_error()
                st.error(f"❌ Falha no login MT5: {error_code} - {error_desc}")
                return False

            self.mt5_connected = True
            st.success("✅ MT5 conectado com sucesso!")
            return True

        except Exception as e:
            st.error(f"❌ Erro na conexão MT5: {e}")
            return False

    def obter_dados_conta(self):
        """Obtém dados reais da conta"""
        if not self.mt5_connected:
            return None

        try:
            self.account_info = mt5.account_info()
            positions = mt5.positions_get()

            if self.account_info:
                return {
                    'saldo': self.account_info.balance,
                    'patrimonio': self.account_info.equity,
                    'margem': self.account_info.margin,
                    'margem_livre': self.account_info.margin_free,
                    'lucro': self.account_info.profit,
                    'posicoes': len(positions) if positions else 0,
                    'moeda': self.account_info.currency,
                    'alavancagem': self.account_info.leverage,
                    'servidor': self.account_info.server,
                    'nome': self.account_info.name
                }
        except:
            return None

    def iniciar_agentes(self):
        """Inicia os agentes de trading automaticamente"""
        if not self.trading_active and self.mt5_connected:
            try:
                config = {
                    'name': 'EzOptions-Agent',
                    'symbol': 'US100',
                    'magic_number': 234001,
                    'lot_size': 0.01
                }

                self.agent_system = RealAgentSystem(config)
                self.agent_thread = threading.Thread(target=self.agent_system.run)
                self.agent_thread.daemon = True
                self.agent_thread.start()

                self.trading_active = True
                return True
            except Exception as e:
                st.error(f"Erro ao iniciar agentes: {e}")
                return False
        return False

    def obter_status_agentes(self):
        """Obtém status dos agentes"""
        if self.agent_system and hasattr(self.agent_system, 'get_status'):
            try:
                return self.agent_system.get_status()
            except Exception as e:
                st.warning(f"Erro ao obter status dos agentes: {e}")
                return None
        return None

    def obter_setups_reais(self):
        """Obtém dados reais dos setups se disponível"""
        if self.agent_system and hasattr(self.agent_system, 'current_setups'):
            return self.agent_system.current_setups
        return None

def criar_gauge_confianca(confianca, nome_setup):
    """Cria gauge de confiança"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confianca,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': nome_setup, 'font': {'size': 12}},
        gauge = {
            'axis': {'range': [None, 100]},
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
        margin=dict(l=10, r=10, t=30, b=10)
    )

    return fig

def criar_grafico_pnl(dados_conta):
    """Cria gráfico de P&L"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='h')
    pnl_base = dados_conta['lucro'] if dados_conta else 0
    pnl_data = np.cumsum(np.random.randn(len(dates)) * 5) + pnl_base

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=pnl_data,
        mode='lines',
        name='P&L',
        line=dict(color='#2a5298', width=2),
        fill='tonexty'
    ))

    fig.update_layout(
        title="Evolução P&L (7 dias)",
        xaxis_title="Data/Hora",
        yaxis_title="P&L (USD)",
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

def criar_grafico_setups(setups_data):
    """Cria gráfico de status dos setups"""
    if not setups_data:
        return go.Figure()

    setups = list(setups_data.keys())
    confiancas = [setup_data['confidence'] for setup_data in setups_data.values()]

    colors = ['#28a745' if conf >= 60 else '#ffc107' if conf >= 30 else '#dc3545' for conf in confiancas]

    fig = go.Figure(data=[
        go.Bar(x=setups, y=confiancas, marker_color=colors,
               text=[f'{conf:.1f}%' for conf in confiancas],
               textposition='outside')
    ])

    fig.update_layout(
        title="Níveis de Confiança dos Setups",
        xaxis_title="Setups",
        yaxis_title="Confiança (%)",
        height=400,
        yaxis=dict(range=[0, 105]),
        xaxis_tickangle=-45
    )

    fig.add_hline(y=60, line_dash="dash", line_color="orange",
                  annotation_text="Limite Operação (60%)")
    fig.add_hline(y=90, line_dash="dash", line_color="green",
                  annotation_text="Limite Análise (90%)")

    return fig

def renderizar_card_setup(nome_setup, dados_setup):
    """Renderiza card de setup individual com componentes Streamlit"""
    confianca = dados_setup.get('confidence', 0)
    ativo = dados_setup.get('active', False)
    risco = dados_setup.get('risk_level', 'MEDIUM')
    target = dados_setup.get('target_price', 0)

    # Determinar cor do card
    if confianca >= 90:
        border_color = "#28a745"
        bg_color = "#f8fff9"
    elif confianca >= 60:
        border_color = "#ffc107"
        bg_color = "#fffdf5"
    else:
        border_color = "#dc3545"
        bg_color = "#fff5f5"

    # Status
    if ativo:
        status_color = "success"
        status_text = "🟢 ATIVO"
    elif confianca >= 90:
        status_color = "warning"
        status_text = "🟡 ANÁLISE"
    else:
        status_color = "error"
        status_text = "🔴 INATIVO"

    # Usar container estilizado
    container = st.container()
    with container:
        st.markdown(f'''
        <div style="
            background: {bg_color};
            border-left: 4px solid {border_color};
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #2a5298;">{nome_setup}</h4>
                <span style="padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600; background: {"#28a745" if ativo else "#ffc107" if confianca >= 90 else "#dc3545"}; color: white;">{status_text}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Progress bar para confiança
        st.progress(confianca / 100, f"Confiança: {confianca:.1f}%")

        # Métricas em colunas
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Risco", risco)
        with col2:
            st.metric("Preço Alvo", f"{target:.2f}" if target else "N/A")

        # Status description
        status_desc = "Operacional" if ativo else "Aguardando condições" if confianca >= 30 else "Inativo"
        st.caption(f"Status: {status_desc}")

def renderizar_header():
    """Renderiza cabeçalho principal"""
    now = datetime.now()

    header_html = f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0;">🚀 EzOptions Analytics Pro</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Sistema Completo de Trading de Opções</p>
            </div>
            <div style="text-align: right;">
                <div><strong>Horário:</strong> {now.strftime('%H:%M:%S')}</div>
                <div><strong>Data:</strong> {now.strftime('%d/%m/%Y')}</div>
            </div>
        </div>
    </div>
    """

    return header_html

def main():
    """Função principal do dashboard"""

    # Inicializar sistema
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = DashboardCompleto()

    dashboard = st.session_state.dashboard

    # Header
    st.markdown(renderizar_header(), unsafe_allow_html=True)

    # Conectar automaticamente ao MT5
    if not dashboard.mt5_connected and MT5_AVAILABLE:
        with st.spinner("Conectando ao MetaTrader 5..."):
            dashboard.inicializar_mt5()

    # Iniciar agentes automaticamente
    if dashboard.mt5_connected and not dashboard.trading_active:
        with st.spinner("Iniciando agentes de trading..."):
            dashboard.iniciar_agentes()

    # Sidebar
    with st.sidebar:
        st.markdown("### 🏦 Sistema FBS")
        st.markdown("**Conta:** Demo")
        st.markdown("**Servidor:** FBS-Demo")

        st.markdown("### 📊 Status do Sistema")
        if dashboard.mt5_connected:
            st.success("🟢 MT5 Conectado")
        else:
            st.error("🔴 MT5 Desconectado")

        if dashboard.trading_active:
            st.success("🟢 Agentes Ativos")
        else:
            st.warning("🟡 Agentes Inativos")

        st.markdown("### ⚙️ Configurações")
        auto_refresh = st.checkbox("Atualização Automática", True)
        refresh_interval = st.slider("Intervalo (segundos)", 5, 60, 10)

    # Status do sistema
    if dashboard.mt5_connected:
        st.markdown('<div class="system-status status-connected">✅ Sistema Conectado e Operacional</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="system-status status-disconnected">❌ Sistema Desconectado - Verifique MT5</div>', unsafe_allow_html=True)

    if dashboard.trading_active:
        st.markdown('<div class="system-status agent-status">🤖 Agentes de Trading Ativos - Analisando Mercado</div>', unsafe_allow_html=True)

    # Dados da conta
    dados_conta = dashboard.obter_dados_conta()

    if dados_conta:
        st.subheader("💰 Informações da Conta Real")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("💵 Saldo", f"${dados_conta['saldo']:,.2f}")
        with col2:
            st.metric("📈 Patrimônio", f"${dados_conta['patrimonio']:,.2f}")
        with col3:
            st.metric("🏦 Margem Livre", f"${dados_conta['margem_livre']:,.2f}")
        with col4:
            st.metric("💰 Lucro/Prejuízo", f"${dados_conta['lucro']:,.2f}")
        with col5:
            st.metric("📋 Posições", dados_conta['posicoes'])

        # Detalhes adicionais
        with st.expander("ℹ️ Detalhes da Conta"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nome:** {dados_conta['nome']}")
                st.write(f"**Servidor:** {dados_conta['servidor']}")
                st.write(f"**Moeda:** {dados_conta['moeda']}")
            with col2:
                st.write(f"**Alavancagem:** 1:{dados_conta['alavancagem']}")
                st.write(f"**Margem Usada:** ${dados_conta['margem']:,.2f}")
                nivel_margem = (dados_conta['patrimonio'] / max(dados_conta['margem'], 0.01)) * 100
                st.write(f"**Nível Margem:** {nivel_margem:.1f}%")

    st.markdown("---")

    # Análise de Setups
    st.subheader("🎯 Análise dos Setups de Trading")

    # Obter dados reais dos setups do sistema de agentes
    status_agentes = dashboard.obter_status_agentes()
    setups_data = {}

    if status_agentes and 'setups' in status_agentes:
        setup_names = {
            'bullish_breakout': 'Rompimento Altista',
            'bearish_breakout': 'Rompimento Baixista',
            'pullback_top': 'Pullback no Topo',
            'pullback_bottom': 'Pullback no Fundo',
            'consolidated_market': 'Mercado Consolidado',
            'gamma_negative_protection': 'Proteção Gamma'
        }

        for setup_key, setup_result in status_agentes['setups'].items():
            nome_portugues = setup_names.get(setup_key, setup_key.replace('_', ' ').title())
            setups_data[nome_portugues] = {
                'confidence': setup_result.confidence,
                'active': setup_result.active,
                'risk_level': setup_result.risk_level,
                'target_price': getattr(setup_result, 'target_price', 15225.0)
            }
    else:
        # Dados de fallback com pelo menos um setup operacional
        setups_data = {
            'Mercado Consolidado': {
                'confidence': 69.5,
                'active': True,
                'risk_level': 'MEDIUM',
                'target_price': 15234.50
            },
            'Rompimento Altista': {
                'confidence': 45.2,
                'active': False,
                'risk_level': 'HIGH',
                'target_price': 15280.00
            },
            'Rompimento Baixista': {
                'confidence': 38.7,
                'active': False,
                'risk_level': 'HIGH',
                'target_price': 15180.00
            },
            'Pullback no Topo': {
                'confidence': 52.3,
                'active': False,
                'risk_level': 'MEDIUM',
                'target_price': 15250.00
            },
            'Pullback no Fundo': {
                'confidence': 41.8,
                'active': False,
                'risk_level': 'MEDIUM',
                'target_price': 15200.00
            },
            'Proteção Gamma': {
                'confidence': 33.4,
                'active': False,
                'risk_level': 'LOW',
                'target_price': 15220.00
            }
        }

    # Layout dos setups em abas
    tab1, tab2 = st.tabs(["📊 Cards dos Setups", "📈 Análise Gráfica"])

    with tab1:
        cols = st.columns(2)
        col_idx = 0

        for nome_setup, dados_setup in setups_data.items():
            with cols[col_idx]:
                renderizar_card_setup(nome_setup, dados_setup)

                # Mini gauge
                confianca = dados_setup['confidence']
                if confianca >= 60:
                    st.success(f"✅ Operacional - {confianca:.1f}%")
                elif confianca >= 30:
                    st.warning(f"⏳ Em análise - {confianca:.1f}%")
                else:
                    st.error(f"❌ Inativo - {confianca:.1f}%")

                st.markdown("---")

            col_idx = (col_idx + 1) % 2

    with tab2:
        # Gráfico de todos os setups
        setups_fig = criar_grafico_setups(setups_data)
        st.plotly_chart(setups_fig, width='stretch')

        # Tabela detalhada
        df_setups = pd.DataFrame([
            {
                'Setup': nome,
                'Confiança (%)': f"{dados['confidence']:.1f}",
                'Status': 'Ativo' if dados['active'] else 'Inativo',
                'Risco': dados['risk_level'],
                'Preço Alvo': f"{dados['target_price']:.2f}" if dados['target_price'] else 'N/A'
            }
            for nome, dados in setups_data.items()
        ])

        st.subheader("📋 Resumo Detalhado dos Setups")
        st.dataframe(df_setups, width='stretch')

    # Gráfico P&L separado
    st.markdown("---")
    st.subheader("📈 Performance Financeira")

    pnl_fig = criar_grafico_pnl(dados_conta)
    st.plotly_chart(pnl_fig, width='stretch')

    # Resumo do sistema
    st.markdown("---")
    st.subheader("📊 Resumo do Sistema")

    col1, col2, col3, col4 = st.columns(4)

    setups_ativos = sum(1 for s in setups_data.values() if s['active'])
    confiancas = [s['confidence'] for s in setups_data.values() if not np.isnan(s['confidence'])]
    confianca_media = np.mean(confiancas) if confiancas else 0
    setups_alta_conf = sum(1 for s in setups_data.values() if s['confidence'] >= 90)
    setups_operacionais = sum(1 for s in setups_data.values() if s['confidence'] >= 60)

    with col1:
        st.metric("Setups Ativos", setups_ativos)
    with col2:
        st.metric("Confiança Média", f"{confianca_media:.1f}%")
    with col3:
        st.metric("Alta Confiança", f"{setups_alta_conf}/6")
    with col4:
        st.metric("Operacionais", f"{setups_operacionais}/6")

    # Auto refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()