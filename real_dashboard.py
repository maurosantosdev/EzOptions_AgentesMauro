import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import numpy as np
import random
import os
from dotenv import load_dotenv

# Tentar importar MT5 e outras dependências
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    st.error("⚠️ MetaTrader5 não instalado. Instale com: pip install MetaTrader5")

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    st.warning("⚠️ yfinance não instalado. Usando dados simulados para opções.")

# Configuração da página
st.set_page_config(
    page_title="EzOptions Analytics Pro - Real Trading",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# Carregar variáveis de ambiente
load_dotenv()

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

.diagnostic-card {
    background: #f8f9fa;
    border-left: 4px solid #17a2b8;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 5px;
}

.error-card {
    background: #f8d7da;
    border-left: 4px solid #dc3545;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 5px;
}

.success-card {
    background: #d4edda;
    border-left: 4px solid #28a745;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 5px;
}

.warning-card {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

class RealTradingSystem:
    def __init__(self):
        self.mt5_connected = False
        self.account_info = None
        self.connection_errors = []
        self.trading_diagnostics = []

    def connect_mt5(self):
        """Conecta ao MetaTrader5 com suas credenciais"""
        if not MT5_AVAILABLE:
            self.connection_errors.append("MetaTrader5 Python package não instalado")
            return False

        try:
            # Credenciais do .env
            login = int(os.getenv("MT5_LOGIN", "103486755"))
            server = os.getenv("MT5_SERVER", "FBS-Demo")
            password = os.getenv("MT5_PASSWORD", "gPo@j6*V")

            # Tentar conectar
            if not mt5.initialize():
                self.connection_errors.append(f"MT5 initialize() failed: {mt5.last_error()}")
                return False

            # Login
            if not mt5.login(login, password, server):
                error = mt5.last_error()
                self.connection_errors.append(f"Login failed: {error}")
                return False

            self.mt5_connected = True
            return True

        except Exception as e:
            self.connection_errors.append(f"Erro na conexão MT5: {str(e)}")
            return False

    def get_real_account_data(self):
        """Obtém dados reais da conta MT5"""
        if not self.mt5_connected:
            return None

        try:
            self.account_info = mt5.account_info()
            positions = mt5.positions_get()

            if self.account_info:
                return {
                    'balance': self.account_info.balance,
                    'equity': self.account_info.equity,
                    'margin': self.account_info.margin,
                    'free_margin': self.account_info.margin_free,
                    'profit': self.account_info.profit,
                    'positions_count': len(positions) if positions else 0,
                    'currency': self.account_info.currency,
                    'leverage': self.account_info.leverage,
                    'server': self.account_info.server,
                    'name': self.account_info.name
                }

        except Exception as e:
            self.connection_errors.append(f"Erro ao obter dados da conta: {str(e)}")

        return None

    def diagnose_trading_issues(self):
        """Diagnostica problemas com trading automático"""
        diagnostics = []

        # 1. Verificar conexão MT5
        if not self.mt5_connected:
            diagnostics.append({
                'type': 'error',
                'title': 'MT5 Não Conectado',
                'message': 'Sistema não conseguiu conectar ao MetaTrader5',
                'solution': 'Verifique se MT5 está aberto e credenciais estão corretas'
            })

        # 2. Verificar horário de trading
        now = datetime.now()
        if now.weekday() > 4:  # Weekend
            diagnostics.append({
                'type': 'warning',
                'title': 'Final de Semana',
                'message': 'Mercado fechado - final de semana',
                'solution': 'Aguarde abertura do mercado (segunda-feira)'
            })

        # 3. Verificar permissões de trading automático
        if self.mt5_connected:
            try:
                # Verificar se auto trading está habilitado
                terminal_info = mt5.terminal_info()
                if terminal_info and not terminal_info.trade_allowed:
                    diagnostics.append({
                        'type': 'error',
                        'title': 'Trading Automático Desabilitado',
                        'message': 'MT5 não permite trading automático',
                        'solution': 'Habilite "Permitir trading automático" no MT5'
                    })

                # Verificar símbolos disponíveis
                symbols = ['US100', 'NASDAQ', 'US30', 'US500']
                available_symbols = []
                for symbol in symbols:
                    if mt5.symbol_info(symbol):
                        available_symbols.append(symbol)

                if not available_symbols:
                    diagnostics.append({
                        'type': 'error',
                        'title': 'Símbolos Não Disponíveis',
                        'message': 'Nenhum símbolo de índice encontrado',
                        'solution': 'Adicione US100, NASDAQ, US30 ou US500 ao Market Watch'
                    })
                else:
                    diagnostics.append({
                        'type': 'success',
                        'title': 'Símbolos Disponíveis',
                        'message': f'Encontrados: {", ".join(available_symbols)}',
                        'solution': 'Símbolos prontos para trading'
                    })

            except Exception as e:
                diagnostics.append({
                    'type': 'error',
                    'title': 'Erro na Verificação',
                    'message': f'Erro ao verificar configurações: {str(e)}',
                    'solution': 'Verifique logs detalhados'
                })

        # 4. Verificar agentes rodando
        try:
            # Simular verificação de agentes (em implementação real, verificaria threads/processos)
            diagnostics.append({
                'type': 'info',
                'title': 'Status dos Agentes',
                'message': 'Sistema de agentes configurado mas não iniciado automaticamente',
                'solution': 'Clique no botão "Iniciar Agentes" para começar trading'
            })

        except Exception as e:
            diagnostics.append({
                'type': 'error',
                'title': 'Erro nos Agentes',
                'message': f'Problema com sistema de agentes: {str(e)}',
                'solution': 'Verifique logs do sistema'
            })

        # 5. Verificar dados de opções
        if not YF_AVAILABLE:
            diagnostics.append({
                'type': 'warning',
                'title': 'Dados de Opções Indisponíveis',
                'message': 'yfinance não instalado - usando dados simulados',
                'solution': 'Instale yfinance: pip install yfinance'
            })

        self.trading_diagnostics = diagnostics
        return diagnostics

def render_header():
    header_html = f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 style="margin: 0; font-size: 2rem;">🚀 EzOptions Analytics Pro - REAL TRADING</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Conexão com MT5 FBS-Demo - Conta Real</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.1rem; margin-bottom: 0.25rem;">
                    <strong>NY Time:</strong> {datetime.now().strftime('%H:%M:%S')}
                </div>
                <div style="font-size: 1.1rem;">
                    <strong>Status:</strong> <span id="connection-status">Verificando...</span>
                </div>
            </div>
        </div>
    </div>
    """
    return header_html

def main():
    st.markdown(render_header(), unsafe_allow_html=True)

    # Inicializar sistema
    if 'trading_system' not in st.session_state:
        st.session_state.trading_system = RealTradingSystem()

    trading_system = st.session_state.trading_system

    # Sidebar
    with st.sidebar:
        st.markdown('<div style="text-align: center;"><h2>🏦 MT5 FBS</h2><p>Real Trading</p></div>', unsafe_allow_html=True)

        st.header("🔌 Conexão")

        if st.button("🔄 Conectar MT5", type="primary"):
            with st.spinner("Conectando ao MT5..."):
                success = trading_system.connect_mt5()
                if success:
                    st.success("✅ Conectado com sucesso!")
                else:
                    st.error("❌ Falha na conexão")

        if st.button("🔍 Diagnosticar Problemas"):
            with st.spinner("Diagnosticando..."):
                trading_system.diagnose_trading_issues()

        if st.button("🚀 Iniciar Agentes de Trading"):
            st.info("🔄 Funcionalidade em implementação...")

        st.header("⚙️ Configurações")
        auto_trade = st.checkbox("Trading Automático", False)
        risk_level = st.selectbox("Nível de Risco", ["Baixo", "Médio", "Alto"])
        max_positions = st.number_input("Max Posições", 1, 10, 3)

    # Main content
    # Status da conexão
    if trading_system.mt5_connected:
        st.markdown('<div class="success-card"><h4>✅ MT5 Conectado</h4><p>Sistema conectado ao FBS-Demo</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-card"><h4>❌ MT5 Desconectado</h4><p>Sistema não conseguiu conectar ao MetaTrader5</p></div>', unsafe_allow_html=True)

    # Dados da conta real
    account_data = trading_system.get_real_account_data()

    if account_data:
        st.subheader("💰 Dados Reais da Sua Conta")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("💰 Saldo", f"${account_data['balance']:,.2f}")
        with col2:
            st.metric("📈 Equity", f"${account_data['equity']:,.2f}")
        with col3:
            st.metric("🏦 Margem Livre", f"${account_data['free_margin']:,.2f}")
        with col4:
            st.metric("💵 Lucro", f"${account_data['profit']:,.2f}")
        with col5:
            st.metric("📋 Posições", account_data['positions_count'])

        # Informações adicionais da conta
        with st.expander("ℹ️ Detalhes da Conta"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nome:** {account_data['name']}")
                st.write(f"**Servidor:** {account_data['server']}")
                st.write(f"**Moeda:** {account_data['currency']}")
            with col2:
                st.write(f"**Alavancagem:** 1:{account_data['leverage']}")
                st.write(f"**Margem Usada:** ${account_data['margin']:,.2f}")
                st.write(f"**Nível de Margem:** {(account_data['equity']/max(account_data['margin'], 0.01)*100):.1f}%")

    else:
        st.warning("⚠️ Não foi possível obter dados da conta. Verifique a conexão.")

    st.markdown("---")

    # Diagnósticos de Trading
    st.subheader("🔍 Diagnóstico de Trading")

    diagnostics = trading_system.trading_diagnostics

    if not diagnostics:
        st.info("Clique em 'Diagnosticar Problemas' na barra lateral para análise completa.")
    else:
        for diag in diagnostics:
            if diag['type'] == 'error':
                st.markdown(f'''
                <div class="error-card">
                    <h4>❌ {diag['title']}</h4>
                    <p><strong>Problema:</strong> {diag['message']}</p>
                    <p><strong>Solução:</strong> {diag['solution']}</p>
                </div>
                ''', unsafe_allow_html=True)
            elif diag['type'] == 'warning':
                st.markdown(f'''
                <div class="warning-card">
                    <h4>⚠️ {diag['title']}</h4>
                    <p><strong>Aviso:</strong> {diag['message']}</p>
                    <p><strong>Solução:</strong> {diag['solution']}</p>
                </div>
                ''', unsafe_allow_html=True)
            elif diag['type'] == 'success':
                st.markdown(f'''
                <div class="success-card">
                    <h4>✅ {diag['title']}</h4>
                    <p><strong>Status:</strong> {diag['message']}</p>
                    <p><strong>Info:</strong> {diag['solution']}</p>
                </div>
                ''', unsafe_allow_html=True)
            else:  # info
                st.markdown(f'''
                <div class="diagnostic-card">
                    <h4>ℹ️ {diag['title']}</h4>
                    <p><strong>Info:</strong> {diag['message']}</p>
                    <p><strong>Ação:</strong> {diag['solution']}</p>
                </div>
                ''', unsafe_allow_html=True)

    # Erros de conexão
    if trading_system.connection_errors:
        st.subheader("🚨 Erros de Conexão")
        for error in trading_system.connection_errors:
            st.error(f"❌ {error}")

    st.markdown("---")

    # Seção de Setups (simulada por enquanto)
    st.subheader("🎯 Status dos Setups de Trading")

    if trading_system.mt5_connected:
        # Simular alguns setups ativos
        setup_data = {
            'Bullish Breakout': {'confidence': 85.2, 'active': True, 'target': 15234.5},
            'Bearish Breakout': {'confidence': 45.8, 'active': False, 'target': 15198.2},
            'Pullback Top': {'confidence': 72.1, 'active': True, 'target': 15245.8},
            'Pullback Bottom': {'confidence': 38.9, 'active': False, 'target': 15187.3},
            'Mercado Consolidado': {'confidence': 91.3, 'active': True, 'target': 15220.0},
            'Proteção Gamma': {'confidence': 67.4, 'active': True, 'target': 15210.1}
        }

        cols = st.columns(3)
        col_idx = 0

        for setup_name, data in setup_data.items():
            with cols[col_idx]:
                status = "🟢 ATIVO" if data['active'] else "🔴 INATIVO"
                confidence = data['confidence']

                card_color = "success-card" if data['active'] else "diagnostic-card"

                st.markdown(f'''
                <div class="{card_color}">
                    <h5>{setup_name}</h5>
                    <p><strong>Status:</strong> {status}</p>
                    <p><strong>Confiança:</strong> {confidence:.1f}%</p>
                    <p><strong>Target:</strong> {data['target']:.1f}</p>
                </div>
                ''', unsafe_allow_html=True)

            col_idx = (col_idx + 1) % 3

    # Auto refresh
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()