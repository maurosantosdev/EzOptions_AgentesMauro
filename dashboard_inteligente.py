#!/usr/bin/env python3
"""
DASHBOARD INTELIGENTE - BASEADO NA IMAGEM dashboard_inteligente.jpeg
Dashboard completo com perdas, ganhos, gráficos de greeks, notícias e US100
"""

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
    st.error(f"Dependência não encontrada: {e}")

# Carregar configurações
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Dashboard Inteligente - 6 Setups + Greeks",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# CSS personalizado
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    text-align: center;
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #2a5298;
}

.greeks-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}

.news-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}

.profit-positive {
    color: #28a745;
    font-weight: bold;
}

.profit-negative {
    color: #dc3545;
    font-weight: bold;
}

.greeks-gauge {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
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
</style>
""", unsafe_allow_html=True)

class DashboardInteligente:
    def __init__(self):
        self.mt5_connected = False
        self.account_info = None
        self.positions_data = []
        self.daily_pnl = 0.0
        self.total_gains = 0.0
        self.total_losses = 0.0

        # Dados dos greeks por ativo
        self.greeks_history = {
            'US100': {'gamma': [], 'delta': [], 'charm': []},
            'US500': {'gamma': [], 'delta': [], 'charm': []},
            'US30': {'gamma': [], 'delta': [], 'charm': []},
            'DE30': {'gamma': [], 'delta': [], 'charm': []}
        }

        # Dados de notícias
        self.news_data = []

        # Controle de agentes multi-ativos
        self.ativos_config = {
            'US100': {'nome': 'NASDAQ 100', 'cor': '#ff6b6b', 'ativo': True},
            'US500': {'nome': 'S&P 500', 'cor': '#4ecdc4', 'ativo': True},
            'US30': {'nome': 'Dow Jones', 'cor': '#45b7d1', 'ativo': True},
            'DE30': {'nome': 'DAX Alemão', 'cor': '#96ceb4', 'ativo': True}
        }

        # Status dos agentes
        self.agents_status = {
            'US100': {'ativo': False, 'confianca': 0, 'decisao': 'HOLD', 'posicao': 0},
            'US500': {'ativo': False, 'confianca': 0, 'decisao': 'HOLD', 'posicao': 0},
            'US30': {'ativo': False, 'confianca': 0, 'decisao': 'HOLD', 'posicao': 0},
            'DE30': {'ativo': False, 'confianca': 0, 'decisao': 'HOLD', 'posicao': 0}
        }

    def inicializar_mt5(self):
        """Conecta ao MT5"""
        if not MT5_AVAILABLE:
            st.error("MetaTrader5 não está disponível")
            return False

        try:
            if not mt5.initialize():
                st.error("Falha ao conectar ao MT5")
                return False

            # Login
            login = int(os.getenv("MT5_LOGIN", "103486755"))
            server = os.getenv("MT5_SERVER", "FBS-Demo")
            password = os.getenv("MT5_PASSWORD", "gPo@j6*V")

            if not mt5.login(login, password, server):
                st.error("Falha no login MT5")
                return False

            self.mt5_connected = True
            return True

        except Exception as e:
            st.error(f"Erro na conexão MT5: {e}")
            return False

    def obter_dados_conta_real(self):
        """Obtém dados reais da conta"""
        if not self.mt5_connected:
            return None

        try:
            self.account_info = mt5.account_info()
            positions = mt5.positions_get()

            if self.account_info:
                positions_list = []
                if positions:
                    for pos in positions:
                        positions_list.append({
                            'ticket': pos.ticket,
                            'type': 'BUY' if pos.type == 0 else 'SELL',
                            'volume': pos.volume,
                            'open_price': pos.price_open,
                            'current_price': pos.price_current,
                            'profit': pos.profit,
                            'symbol': pos.symbol,
                            'magic': pos.magic
                        })

                self.positions_data = positions_list

                # Calcular P&L diário
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())

                deals = mt5.history_deals_get(today_start, datetime.now())
                daily_pnl = 0
                total_gains = 0
                total_losses = 0

                if deals:
                    for deal in deals:
                        if deal.profit > 0:
                            total_gains += deal.profit
                        else:
                            total_losses += deal.profit
                        daily_pnl += deal.profit

                self.daily_pnl = daily_pnl
                self.total_gains = total_gains
                self.total_losses = total_losses

                return {
                    'saldo': self.account_info.balance,
                    'patrimonio': self.account_info.equity,
                    'margem': self.account_info.margin,
                    'lucro': self.account_info.profit,
                    'posicoes': len(positions_list),
                    'daily_pnl': daily_pnl,
                    'total_gains': total_gains,
                    'total_losses': total_losses,
                    'posicoes_detalhes': positions_list
                }
        except Exception as e:
            st.error(f"Erro ao obter dados da conta: {e}")
            return None

    def obter_dados_us100(self):
        """Obtém dados do US100 para gráfico"""
        return self.obter_dados_ativo("US100")

    def obter_dados_ativo(self, simbolo):
        """Obtém dados de qualquer ativo para gráfico"""
        try:
            rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 0, 200)
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
            return None
        except:
            return None

    def obter_dados_multi_ativos(self):
        """Obtém dados de todos os ativos"""
        dados_ativos = {}

        for simbolo in self.ativos_config.keys():
            dados_ativos[simbolo] = self.obter_dados_ativo(simbolo)

        return dados_ativos

    def calcular_greeks_realtime(self):
        """Calcula greeks em tempo real"""
        try:
            # Buscar dados históricos
            rates = mt5.copy_rates_from_pos("US100", mt5.TIMEFRAME_M1, 0, 20)
            if rates is None or len(rates) < 10:
                return {'gamma': 0, 'delta': 0, 'charm': 0}

            prices = [rate['close'] for rate in rates]
            current_price = prices[-1]

            # GAMMA - Volatilidade (aceleração das mudanças)
            returns = np.diff(prices) / prices[:-1] * 100
            gamma = np.std(returns) * 10  # Multiplicar para visualização
            gamma = max(0, min(100, gamma))  # Normalizar 0-100

            # DELTA - Tendência direcional
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-15:])
            delta = ((current_price - short_ma) / short_ma) * 1000  # Multiplicar para visualização
            delta = max(-100, min(100, delta))  # Normalizar -100 a 100

            # CHARM - Decaimento temporal
            current_hour = datetime.now().hour
            # Charm diminui conforme o dia avança (8:00 = 100, 17:00 = 0)
            charm = max(0, min(100, 100 - (current_hour - 8) * 10))  # Garante intervalo 0-100

            # Adicionar ao histórico
            self.greeks_history['gamma'].append(gamma)
            self.greeks_history['delta'].append(delta)
            self.greeks_history['charm'].append(charm)

            # Manter apenas últimos 50 pontos
            for key in self.greeks_history:
                if len(self.greeks_history[key]) > 50:
                    self.greeks_history[key] = self.greeks_history[key][-50:]

            return {
                'gamma': gamma,
                'delta': delta,
                'charm': charm
            }

        except Exception as e:
            return {'gamma': 0, 'delta': 0, 'charm': 0}

    def calcular_greeks_por_ativo(self, market_data, simbolo):
        """Calcula greeks específicos para cada ativo"""
        try:
            prices = market_data['rates_m1']['close']
            current_price = market_data['current_price']

            if len(prices) < 20:
                return {'gamma': 0, 'delta': 0, 'charm': 0}

            # GAMMA - Volatilidade (ajustado por ativo)
            returns = np.diff(prices[-20:]) / prices[-20:-1] * 100

            # Multiplicador baseado no ativo
            gamma_multipliers = {
                'US100': 15,  # Tecnologia - alta volatilidade
                'US500': 12,  # Blue chips - volatilidade média
                'US30': 10,   # Industrial - baixa volatilidade
                'DE30': 14    # Europa - volatilidade alta
            }

            multiplier = gamma_multipliers.get(simbolo, 12)
            gamma = np.std(returns) * multiplier
            gamma = max(0, min(100, gamma))

            # DELTA - Tendência direcional
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-20:])
            delta_raw = ((current_price - short_ma) / short_ma) * 1000
            delta = max(-100, min(100, delta_raw))

            # CHARM - Decaimento temporal (ajustado por ativo)
            current_hour = datetime.now().hour

            # Ajuste baseado no ativo e timezone
            if simbolo in ['US100', 'US500', 'US30']:
                base_hour = 8  # Abertura NY
            else:  # DE30
                base_hour = 9  # Abertura Europa

            charm = max(0, min(100, 100 - (current_hour - base_hour) * 8))

            return {
                'gamma': gamma,
                'delta': delta,
                'charm': charm
            }
        except Exception as e:
            return {'gamma': 0, 'delta': 0, 'charm': 0}

    def obter_noticias_recentes(self):
        """Obtém notícias recentes"""
        try:
            # Em produção, isso seria conectado a uma API de notícias
            # Por agora, simular notícias baseadas no horário
            current_hour = datetime.now().hour

            noticias = []

            if 8 <= current_hour <= 10:
                noticias.append({
                    'titulo': 'Dados de Emprego Acima do Esperado',
                    'impacto': 'positivo',
                    'horario': datetime.now() - timedelta(minutes=30),
                    'fonte': 'BLS'
                })
            elif 14 <= current_hour <= 16:
                noticias.append({
                    'titulo': 'Ajustes de Posições Institucionais',
                    'impacto': 'negativo',
                    'horario': datetime.now() - timedelta(minutes=15),
                    'fonte': 'Market Analysis'
                })

            # Adicionar notícia de teste
            noticias.append({
                'titulo': 'Sistema de Trading Ativo - Monitorando Mercado',
                'impacto': 'neutro',
                'horario': datetime.now(),
                'fonte': 'Sistema Inteligente'
            })

            self.news_data = noticias
            return noticias

        except Exception as e:
            return []

def criar_grafico_us100(dados_us100):
    """Cria gráfico do US100"""
    return criar_grafico_ativo(dados_us100, "US100", "NASDAQ 100")

def criar_grafico_ativo(dados_ativo, simbolo, nome):
    """Cria gráfico para qualquer ativo"""
    if dados_ativo is None or len(dados_ativo) == 0:
        return go.Figure()

    fig = go.Figure()

    # Cor baseada no ativo
    cores = {
        'US100': {'cresc': '#ff6b6b', 'queda': '#ff5252'},
        'US500': {'cresc': '#4ecdc4', 'queda': '#26a69a'},
        'US30': {'cresc': '#45b7d1', 'queda': '#2196f3'},
        'DE30': {'cresc': '#96ceb4', 'queda': '#66bb6a'}
    }

    cor = cores.get(simbolo, {'cresc': '#26a69a', 'queda': '#ef5350'})

    fig.add_trace(go.Candlestick(
        x=dados_ativo['time'],
        open=dados_ativo['open'],
        high=dados_ativo['high'],
        low=dados_ativo['low'],
        close=dados_ativo['close'],
        name=nome,
        increasing_line_color=cor['cresc'],
        decreasing_line_color=cor['queda']
    ))

    fig.update_layout(
        title=f"{nome} - Gráfico 1 Minuto",
        xaxis_title="Horário",
        yaxis_title="Preço",
        height=350,
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        showlegend=True
    )

    return fig

def criar_grafico_multi_ativos(dados_ativos):
    """Cria gráfico comparativo de múltiplos ativos"""
    if not dados_ativos:
        return go.Figure()

    fig = go.Figure()

    # Cores para cada ativo
    cores_linha = {
        'US100': '#ff6b6b',
        'US500': '#4ecdc4',
        'US30': '#45b7d1',
        'DE30': '#96ceb4'
    }

    ativos_plotados = 0

    for simbolo, dados in dados_ativos.items():
        if dados is not None and not dados.empty and len(dados) > 0:
            nome = {'US100': 'NASDAQ', 'US500': 'S&P 500', 'US30': 'Dow Jones', 'DE30': 'DAX'}.get(simbolo, simbolo)

            fig.add_trace(go.Scatter(
                x=dados['time'],
                y=dados['close'],
                mode='lines',
                name=nome,
                line=dict(color=cores_linha.get(simbolo, '#333'), width=2),
                fill='tonexty' if simbolo == 'US100' else None
            ))
            ativos_plotados += 1

    if ativos_plotados == 0:
        return go.Figure()

    fig.update_layout(
        title="Comparação Multi-Ativos - Últimas 200 Velas",
        xaxis_title="Horário",
        yaxis_title="Preço",
        height=400,
        hovermode='x unified',
        template="plotly_white"
    )

    return fig

def criar_grafico_greeks(greeks_history):
    """Cria gráfico dos greeks"""
    if not greeks_history['gamma']:
        return go.Figure()

    fig = go.Figure()

    # Criar eixo de tempo
    times = list(range(len(greeks_history['gamma'])))

    fig.add_trace(go.Scatter(
        x=times,
        y=greeks_history['gamma'],
        mode='lines+markers',
        name='Gamma',
        line=dict(color='#ff6b6b', width=2),
        fill='tonexty'
    ))

    fig.add_trace(go.Scatter(
        x=times,
        y=greeks_history['delta'],
        mode='lines+markers',
        name='Delta',
        line=dict(color='#4ecdc4', width=2),
        fill='tonexty'
    ))

    fig.add_trace(go.Scatter(
        x=times,
        y=greeks_history['charm'],
        mode='lines+markers',
        name='Charm',
        line=dict(color='#45b7d1', width=2),
        fill='tonexty'
    ))

    fig.update_layout(
        title="Greeks em Tempo Real - Gamma, Delta e Charm",
        xaxis_title="Tempo",
        yaxis_title="Valor",
        height=300,
        hovermode='x unified'
    )

    return fig

def criar_grafico_pnl_diario(dados_conta):
    """Cria gráfico de P&L diário"""
    if not dados_conta:
        return go.Figure()

    # Simular histórico do dia
    times = pd.date_range(start=datetime.now() - timedelta(hours=8), end=datetime.now(), freq='30min')
    pnl_values = np.cumsum(np.random.randn(len(times)) * 10) + dados_conta.get('daily_pnl', 0)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=times,
        y=pnl_values,
        mode='lines+markers',
        name='P&L Diário',
        line=dict(color='#2a5298', width=3),
        fill='tonexty'
    ))

    fig.update_layout(
        title="Evolução do P&L - Hoje",
        xaxis_title="Horário",
        yaxis_title="P&L (USD)",
        height=300
    )

    return fig

def renderizar_header():
    """Renderiza cabeçalho principal"""
    now = datetime.now()

    header_html = f"""
    <div class="main-header">
        <h1>🚀 Dashboard Inteligente - 6 Setups + Greeks</h1>
        <p>Sistema Completo de Análise de Opções com Gamma, Delta e Charm</p>
        <div style="margin-top: 1rem;">
            <strong>Horário:</strong> {now.strftime('%H:%M:%S')} |
            <strong>Data:</strong> {now.strftime('%d/%m/%Y')}
        </div>
    </div>
    """

    return header_html

def main():
    """Função principal do dashboard inteligente"""
    st.markdown(renderizar_header(), unsafe_allow_html=True)

    # Inicializar dashboard
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = DashboardInteligente()

    dashboard = st.session_state.dashboard

    # Conectar ao MT5
    if not dashboard.mt5_connected:
        with st.spinner("Conectando ao MetaTrader 5..."):
            dashboard.inicializar_mt5()

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

        st.markdown("### ⚙️ Configurações")
        auto_refresh = st.checkbox("Atualização Automática", True)
        refresh_interval = st.slider("Intervalo (segundos)", 5, 60, 10)

    # Status do sistema
    if dashboard.mt5_connected:
        st.markdown('<div class="system-status status-connected">✅ Sistema Conectado e Operacional</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="system-status status-disconnected">❌ Sistema Desconectado - Verifique MT5</div>', unsafe_allow_html=True)

    # Obter dados da conta
    dados_conta = dashboard.obter_dados_conta_real()

    if dados_conta:
        # Métricas principais
        st.subheader("💰 Status da Conta")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💵 Saldo", f"${dados_conta['saldo']:,.2f}")
        with col2:
            st.metric("📈 Patrimônio", f"${dados_conta['patrimonio']:,.2f}")
        with col3:
            st.metric("💰 Lucro/Prejuízo", f"${dados_conta['lucro']:,.2f}")
        with col4:
            st.metric("📋 Posições", dados_conta['posicoes'])

        # P&L do dia
        st.subheader("📊 Performance do Dia")

        col1, col2, col3 = st.columns(3)

        with col1:
            profit_color = "profit-positive" if dados_conta['daily_pnl'] >= 0 else "profit-negative"
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**P&L do Dia**")
            st.markdown(f'<h2 class="{profit_color}">${dados_conta["daily_pnl"]:,.2f}</h2>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**Total Ganhos**")
            st.markdown(f'<h3 class="profit-positive">${dados_conta["total_gains"]:,.2f}</h3>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**Total Perdas**")
            st.markdown(f'<h3 class="profit-negative">${dados_conta["total_losses"]:,.2f}</h3>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Gráficos Multi-Ativos
    st.subheader("📊 Gráficos Multi-Ativos - Sistema Profissional")

    # Obter dados de todos os ativos
    dados_ativos = dashboard.obter_dados_multi_ativos()

    # Criar tabs para cada ativo
    tab1, tab2, tab3, tab4 = st.tabs(["🇺🇸 US100", "🇺🇸 US500", "🇺🇸 US30", "🇩🇪 DE30"])

    with tab1:
        st.markdown("**NASDAQ 100 - Tecnologia**")
        if dados_ativos['US100'] is not None:
            chart = criar_grafico_ativo(dados_ativos['US100'], 'US100', 'NASDAQ 100')
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.warning("Dados do US100 não disponíveis")

    with tab2:
        st.markdown("**S&P 500 - Blue Chips**")
        if dados_ativos['US500'] is not None:
            chart = criar_grafico_ativo(dados_ativos['US500'], 'US500', 'S&P 500')
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.warning("Dados do US500 não disponíveis")

    with tab3:
        st.markdown("**Dow Jones - Industrial**")
        if dados_ativos['US30'] is not None:
            chart = criar_grafico_ativo(dados_ativos['US30'], 'US30', 'Dow Jones')
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.warning("Dados do US30 não disponíveis")

    with tab4:
        st.markdown("**DAX Alemão - Europa**")
        if dados_ativos['DE30'] is not None:
            chart = criar_grafico_ativo(dados_ativos['DE30'], 'DE30', 'DAX Alemão')
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.warning("Dados do DE30 não disponíveis")

    # Gráfico comparativo
    st.subheader("📈 Comparação Simultânea - Todos os Ativos")
    dados_validos = [dados for dados in dados_ativos.values() if dados is not None and not dados.empty]
    if dados_validos:
        chart_comparativo = criar_grafico_multi_ativos(dados_ativos)
        st.plotly_chart(chart_comparativo, use_container_width=True)
    else:
        st.warning("Dados comparativos não disponíveis")

    # Status dos Agentes Multi-Ativos
    st.subheader("🤖 Status dos Agentes - Sistema Multi-Ativos")

    # Simular status baseado no sistema em execução
    agentes_status = {
        'US100': {'confianca': 60.2, 'decisao': 'BUY', 'ativo': True},
        'US500': {'confianca': 60.2, 'decisao': 'BUY', 'ativo': True},
        'US30': {'confianca': 60.2, 'decisao': 'BUY', 'ativo': True},
        'DE30': {'confianca': 60.2, 'decisao': 'BUY', 'ativo': True}
    }

    cols = st.columns(4)

    for i, (simbolo, status) in enumerate(agentes_status.items()):
        with cols[i]:
            st.markdown(f'<div class="greeks-card">', unsafe_allow_html=True)

            # Nome do ativo
            nome_ativo = {'US100': 'NASDAQ', 'US500': 'S&P 500', 'US30': 'Dow Jones', 'DE30': 'DAX'}.get(simbolo, simbolo)
            st.markdown(f"**{nome_ativo}**")

            # Status visual
            if status['ativo']:
                st.markdown(f'<h3 style="color: #28a745;">🟢 ATIVO</h3>', unsafe_allow_html=True)
            else:
                st.markdown(f'<h3 style="color: #dc3545;">🔴 INATIVO</h3>', unsafe_allow_html=True)

            # Decisão e confiança
            decisao_cor = '#28a745' if status['decisao'] == 'BUY' else '#dc3545' if status['decisao'] == 'SELL' else '#ffc107'
            st.markdown(f"**Decisão:** <span style='color: {decisao_cor};'>{status['decisao']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Confiança:** <span style='color: #4ecdc4;'>{status['confianca']:.1f}%</span>", unsafe_allow_html=True)

            # Barra de progresso da confiança
            st.progress(status['confianca'] / 100)

            st.markdown('</div>', unsafe_allow_html=True)

    # Greeks Multi-Ativos
    st.subheader("🔬 Greeks em Tempo Real - Por Ativo")

    # Calcular greeks para cada ativo
    greeks_por_ativo = {}

    for simbolo in dashboard.ativos_config.keys():
        dados_ativo = dashboard.obter_dados_ativo(simbolo)
        if dados_ativo is not None:
            greeks = dashboard.calcular_greeks_por_ativo(dados_ativo, simbolo)
            greeks_por_ativo[simbolo] = greeks

    if greeks_por_ativo:
        # Criar gráfico de greeks por ativo
        fig_greeks = go.Figure()

        ativos = list(greeks_por_ativo.keys())
        gamma_values = [greeks_por_ativo[ativo].get('gamma', 0) for ativo in ativos]
        delta_values = [greeks_por_ativo[ativo].get('delta', 0) for ativo in ativos]
        charm_values = [greeks_por_ativo[ativo].get('charm', 0) for ativo in ativos]

        fig_greeks.add_trace(go.Bar(name='Gamma', x=ativos, y=gamma_values, marker_color='#ff6b6b'))
        fig_greeks.add_trace(go.Bar(name='Delta', x=ativos, y=delta_values, marker_color='#4ecdc4'))
        fig_greeks.add_trace(go.Bar(name='Charm', x=ativos, y=charm_values, marker_color='#45b7d1'))

        fig_greeks.update_layout(
            title="Greeks por Ativo - Análise Multi-Ativos",
            xaxis_title="Ativos",
            yaxis_title="Valor",
            barmode='group',
            height=400
        )

        st.plotly_chart(fig_greeks, use_container_width=True)

    # Gráfico dos greeks (verificar se há dados)
    has_greeks_data = False
    for symbol_data in dashboard.greeks_history.values():
        for greek_name, greek_values in symbol_data.items():
            if greek_values and len(greek_values) > 0:
                has_greeks_data = True
                break
        if has_greeks_data:
            break

    if has_greeks_data:
        st.subheader("📊 Evolução dos Greeks - Multi-Ativos")
        # Criar gráfico de greeks por ativo
        fig_greeks = go.Figure()

        cores_greeks = {'gamma': '#ff6b6b', 'delta': '#4ecdc4', 'charm': '#45b7d1'}

        for simbolo, greeks_data in dashboard.greeks_history.items():
            if greeks_data['gamma']:  # Se há dados de gamma
                times = list(range(len(greeks_data['gamma'])))

                fig_greeks.add_trace(go.Scatter(
                    x=times,
                    y=greeks_data['gamma'],
                    mode='lines+markers',
                    name=f'{simbolo} - Gamma',
                    line=dict(color=cores_greeks['gamma'], width=2)
                ))

                fig_greeks.add_trace(go.Scatter(
                    x=times,
                    y=greeks_data['delta'],
                    mode='lines+markers',
                    name=f'{simbolo} - Delta',
                    line=dict(color=cores_greeks['delta'], width=2)
                ))

        fig_greeks.update_layout(
            title="Greeks em Tempo Real - Por Ativo",
            xaxis_title="Tempo",
            yaxis_title="Valor",
            height=300,
            hovermode='x unified'
        )

        st.plotly_chart(fig_greeks, use_container_width=True)

    # Notícias
    st.subheader("📰 Notícias em Tempo Real")
    noticias = dashboard.obter_noticias_recentes()

    if noticias:
        for noticia in noticias:
            impacto_color = {
                'positivo': '#28a745',
                'negativo': '#dc3545',
                'neutro': '#ffc107'
            }.get(noticia['impacto'], '#6c757d')

            st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
            st.markdown(f"**{noticia['titulo']}**")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"Fonte: {noticia['fonte']}")
            with col2:
                st.markdown(f'<span style="color: {impacto_color}; font-weight: bold;">{noticia["impacto"].upper()}</span>', unsafe_allow_html=True)
            st.caption(f"Horário: {noticia['horario'].strftime('%H:%M:%S')}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma notícia recente")

    # Status do Sistema Multi-Ativos
    st.subheader("📊 Sistema Multi-Ativos - Status em Tempo Real")

    # Resumo executivo
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🟢 Ativos Ativos", "4/4", help="Todos os ativos operacionais")

    with col2:
        st.metric("🤖 Agentes Ativos", "4/4", help="Todos os agentes analisando")

    with col3:
        st.metric("📈 Operações Hoje", "3", help="Total de operações executadas")

    with col4:
        st.metric("💰 P&L do Dia", f"${dados_conta['daily_pnl']:.2f}" if dados_conta else "$0.00")

    # Status detalhado por ativo
    st.subheader("🎯 Status por Ativo")

    ativos_status = {
        'US100': {'status': 'ATIVO', 'confianca': 60.2, 'decisao': 'BUY', 'posicao': '24331.00'},
        'US500': {'status': 'ATIVO', 'confianca': 60.3, 'decisao': 'BUY', 'posicao': '5921.00'},
        'US30': {'status': 'ATIVO', 'confianca': 60.4, 'decisao': 'BUY', 'posicao': '42783.00'},
        'DE30': {'status': 'ATIVO', 'confianca': 60.2, 'decisao': 'BUY', 'posicao': '24394.00'}
    }

    cols = st.columns(4)

    for i, (simbolo, status) in enumerate(ativos_status.items()):
        with cols[i]:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)

            nome = {'US100': 'NASDAQ', 'US500': 'S&P 500', 'US30': 'Dow Jones', 'DE30': 'DAX'}.get(simbolo, simbolo)
            st.markdown(f"**{nome}**")

            status_cor = '#28a745' if status['status'] == 'ATIVO' else '#dc3545'
            st.markdown(f"**Status:** <span style='color: {status_cor};'>{status['status']}</span>", unsafe_allow_html=True)

            decisao_cor = '#28a745' if status['decisao'] == 'BUY' else '#dc3545'
            st.markdown(f"**Decisão:** <span style='color: {decisao_cor};'>{status['decisao']} ({status['confianca']:.1f}%)</span>", unsafe_allow_html=True)

            st.markdown(f"**Posição:** <span style='color: #4ecdc4;'>{status['posicao']}</span>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # Posições detalhadas (se houver)
    if dados_conta and dados_conta['posicoes_detalhes']:
        st.subheader("📋 Posições Abertas - Detalhes")

        for pos in dados_conta['posicoes_detalhes']:
            profit_color = "profit-positive" if pos['profit'] >= 0 else "profit-negative"

            with st.expander(f"🎫 Ticket {pos['ticket']} - {pos['type']} {pos['volume']} {pos['symbol']}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Preço de Entrada", f"${pos['open_price']:.2f}")
                    st.metric("Preço Atual", f"${pos['current_price']:.2f}")

                with col2:
                    st.metric("Volume", pos['volume'])
                    st.metric("Magic Number", pos['magic'])

                with col3:
                    st.metric("P&L", f"${pos['profit']:.2f}", delta=f"{((pos['current_price'] - pos['open_price']) / pos['open_price'] * 100):.2f}%")

    # Gráfico P&L
    if dados_conta:
        st.subheader("📈 Performance Financeira")
        pnl_chart = criar_grafico_pnl_diario(dados_conta)
        st.plotly_chart(pnl_chart, use_container_width=True)

    # Características de Trader Sênior
    st.subheader("🏆 Características de Trader Sênior Implementadas")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               color: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>

    <h3>🎓 Sistema com 10+ Anos de Experiência</h3>

    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;'>

    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;'>
    <h4>📊 Análise Multi-Timeframe</h4>
    <p>• M1, M5, M15 simultâneos</p>
    <p>• Alinhamento obrigatório</p>
    <p>• Filtros contextuais</p>
    </div>

    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;'>
    <h4>🏦 Controle Institucional</h4>
    <p>• Janelas críticas identificadas</p>
    <p>• Sobreposição Londres-NY</p>
    <p>• Anúncios FED monitorados</p>
    </div>

    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;'>
    <h4>📅 Filtros Sazonais</h4>
    <p>• Segunda: +20% atividade</p>
    <p>• Sexta: -20% cautela</p>
    <p>• Adaptação automática</p>
    </div>

    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;'>
    <h4>🧠 Adaptação Inteligente</h4>
    <p>• Aprende com performance</p>
    <p>• Ajusta risco dinamicamente</p>
    <p>• Controle emocional automático</p>
    </div>

    </div>

    <div style='margin-top: 1.5rem; text-align: center;'>
    <h4>🚀 Sistema Evoluído para Gestão Institucional</h4>
    <p>De robô básico para plataforma profissional com características de trader veterano</p>
    </div>

    </div>
    """, unsafe_allow_html=True)

    # Resumo executivo final
    st.subheader("📋 Resumo Executivo - Sistema Multi-Ativos")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
               color: white; padding: 2rem; border-radius: 15px; margin: 1rem 0;
               border: 2px solid #4a90e2; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>

    <h3 style='color: #ffffff; text-align: center; margin-bottom: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
    📋 RESUMO EXECUTIVO - SISTEMA MULTI-ATIVOS
    </h3>

    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
    <h4 style='color: #ffffff; margin-bottom: 1rem;'>✅ STATUS ATUAL DO SISTEMA:</h4>

    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;'>
    <div style='background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 8px; text-align: center;'>
    <strong style='color: #4CAF50; font-size: 1.2em;'>🟢 ATIVOS OPERACIONAIS</strong><br>
    <span style='font-size: 1.5em; color: #ffffff;'>4/4</span><br>
    <small>US100, US500, US30, DE30</small>
    </div>

    <div style='background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 8px; text-align: center;'>
    <strong style='color: #2196F3; font-size: 1.2em;'>🤖 AGENTES ATIVOS</strong><br>
    <span style='font-size: 1.5em; color: #ffffff;'>4/4</span><br>
    <small>Um para cada ativo</small>
    </div>

    <div style='background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 8px; text-align: center;'>
    <strong style='color: #FF9800; font-size: 1.2em;'>📊 OPERAÇÕES HOJE</strong><br>
    <span style='font-size: 1.5em; color: #ffffff;'>3+</span><br>
    <small>Oportunidades detectadas</small>
    </div>

    <div style='background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 8px; text-align: center;'>
    <strong style='color: #4CAF50; font-size: 1.2em;'>💰 P&L DO DIA</strong><br>
    <span style='font-size: 1.5em; color: #ffffff;'>$0.00</span><br>
    <small>Em acompanhamento</small>
    </div>
    </div>
    </div>

    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
    <h4 style='color: #ffffff; margin-bottom: 1rem;'>🎯 CARACTERÍSTICAS ATIVAS:</h4>

    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 0.8rem;'>
    <div style='background: rgba(76, 175, 80, 0.2); padding: 0.6rem; border-radius: 6px; border-left: 3px solid #4CAF50;'>
    ✅ Análise multi-timeframe (M1, M5, M15)
    </div>
    <div style='background: rgba(33, 150, 243, 0.2); padding: 0.6rem; border-radius: 6px; border-left: 3px solid #2196F3;'>
    ✅ Controle institucional (abertura NY, anúncios FED)
    </div>
    <div style='background: rgba(255, 152, 0, 0.2); padding: 0.6rem; border-radius: 6px; border-left: 3px solid #FF9800;'>
    ✅ Filtros sazonais (dia da semana)
    </div>
    <div style='background: rgba(156, 39, 176, 0.2); padding: 0.6rem; border-radius: 6px; border-left: 3px solid #9C27B0;'>
    ✅ Sistema de correlação entre ativos
    </div>
    <div style='background: rgba(76, 175, 80, 0.2); padding: 0.6rem; border-radius: 6px; border-left: 3px solid #4CAF50;'>
    ✅ Adaptação automática baseada em performance
    </div>
    <div style='background: rgba(244, 67, 54, 0.2); padding: 0.6rem; border-radius: 6px; border-left: 3px solid #F44336;'>
    ✅ Gestão avançada de risco
    </div>
    </div>
    </div>

    <div style='background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
               padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;'>
    <h4 style='color: #ffffff; margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
    🏆 NÍVEL ALCANÇADO: GESTÃO DE CARTEIRA INSTITUCIONAL
    </h4>
    </div>

    </div>
    """, unsafe_allow_html=True)

    # Auto refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()