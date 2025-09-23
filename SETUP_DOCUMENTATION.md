# EzOptions Analytics Pro - Sistema de 6 Setups Avançados

## 🎯 Visão Geral

O sistema foi completamente reimplementado com um framework avançado de análise de trading baseado em 6 setups específicos com sistema de confiança integrado. Agora os agentes só analisam estratégias com 90% de confiança e só operam com 60% de confiança mínima.

## 📊 Setups Implementados

### SETUP 1 - Bullish Breakout: Acima do alvo 🚀
**Condições:**
- Preço operando em CHARM positivo CHARM crescente até o alvo
- Barra de DELTA positivo até o alvo
- Maior barra de GAMMA acima do preço (preferencialmente no alvo)
- Sem barreiras de GAMMA abaixo do preço
- **Confirmação Price Action:** Rompimento do primeiro desvio da VWAP para cima
- **Stop Loss:** Ativado se o preço voltar abaixo do ponto de virada a estrutura de CHARM

### SETUP 2 - Bearish Breakout: Alvo abaixo 📉
**Condições:**
- Preço operando em CHARM negativo. CHARM decrescente até o alvo
- Barras de DELTA negativo até o alvo
- Maior barra de GAMMA abaixo do preço (preferencialmente no alvo)
- Sem barreiras do GAMMA acima do preço
- **Confirmação Price Action:** Rompimento do primeiro desvio da VWAP para baixo
- **Stop Loss:** Ativado se o preço voltar acima do ponto de virada ou perder a estrutura de CHARM

### SETUP 3 - Pullback no Topo: Reversão para baixo 🔄
**Condições:**
- Preço na maior barra de GAMMA positiva ou área de GAMMA Flip
- Próxima barra de GAMMA acima muito menor
- Maior barra de CHARM positivo antes de barra menor (indica perda de força)
- Última barra de DELTA positivo atingida (indica esgotamento de demanda)
- **Confirmação Extra:** Volume neutro ou fechando nos strikes acima (DDF LEVELS)
- **Stop Loss:** Ativado se DELTA e CHARM continuarem crescendo acima do nível de entrada

### SETUP 4 - Pullback no Fundo: Reversão para cima 🔄
**Condições:**
- Preço na maior barra de GAMMA negativo ou área de GAMMA Flip
- Próxima barra de GAMMA abaixo muito menor
- Maior barra de CHARM negativo antes de barra menor (indica perda de força vendedora)
- Última barra de DELTA negativo atingida (indica exaustão de oferta)
- **Confirmação Extra:** Volume neutro ou ausente nos strikes abaixo (DDF LEVELS)
- **Stop Loss:** Ativado se DELTA e CHARM continuarem crescendo abaixo do nível de entrada

### SETUP 5 - Mercado Consolidado (VWAP): Consolidado 🎯
**Condições:**
- Maior barra de GAMMA posicionada no centro do range (normalmente na VWAP)
- Maior barra de DELTA no centro do range
- CHARM neutro ou em Flip, sem direção clara
- Maior barra de THETA DECAY no centro do range
- VWAP e seus desvios formando linhas retas, indicando equilíbrio
- **Confirmação Extra:** Volume equilibrado nos strikes (DDF) e no Heat Map
- **Stop Loss:** Ativado caso haja rompimento claro do range com confirmação do CHARM

### SETUP 6 - Proteção contra GAMMA Negativo 🛡️
**Condições:**
- Preço operando em GAMMA e DELTA positivo
- Maior barra de GAMMA Positivo acima do preço
- Maior barra de DELTA Positivo acima do preço
- Grande barra de GAMMA e DELTA Negativo abaixo do preço (perigo iminente)
- **Confirmação Extra:** Aumento do ratio de Puts x Calls para calls (puts perdendo força)
- **Stop Loss:** Ativado caso o preço entre em GAMMA Negativo sem defesa

## 🤖 Sistema de Confiança

### Níveis de Confiança
- **90%+** - Análise Autorizada (pode analisar e processar)
- **60%+** - Operação Autorizada (pode executar trades)
- **<60%** - Setup Inativo (apenas monitoramento)

### Fatores de Confiança
Cada setup é avaliado com base em 6 critérios ponderados:
1. **CHARM Strength** (25%) - Força e direção do CHARM
2. **DELTA Alignment** (25%) - Alinhamento do DELTA com a estratégia
3. **GAMMA Position** (20%) - Posicionamento das barras de GAMMA
4. **Price Action Confirmation** (15%) - Confirmação com VWAP e price action
5. **Volume Confirmation** (10%) - Confirmação de volume
6. **VWAP Alignment** (5%) - Alinhamento com VWAP

### Classificação de Risco
- **LOW** - Setups com alta confiança e baixa volatilidade
- **MEDIUM** - Setups com confiança moderada
- **HIGH** - Setups em condições de alta volatilidade ou baixa confiança

## 🖥️ Interface Moderna

### Dashboard Analytics Pro
A nova interface oferece:
- **Design Responsivo** - Adaptável a diferentes tamanhos de tela
- **Cards Intuitivos** - Visualização clara de cada setup
- **Gauges de Confiança** - Medidores visuais de confiança
- **Gráficos Interativos** - Plotly charts com análise em tempo real
- **Status em Tempo Real** - Indicadores visuais de status dos setups
- **Overview Dashboard** - Visão geral do status de todos os setups

### Funcionalidades
1. **Métricas em Tempo Real**
   - Saldo, Equity, Margem Livre
   - P&L em tempo real
   - Número de posições ativas

2. **Análise de Setups**
   - Status visual de cada setup (Ativo/Análise/Inativo)
   - Nível de confiança com barra de progresso
   - Nível de risco (LOW/MEDIUM/HIGH)
   - Target price e stop loss

3. **Gráficos Avançados**
   - Gamma Exposure (GEX)
   - Delta Exposure
   - Charm Exposure
   - Theta Decay
   - P&L Evolution
   - Setup Status Overview (Donut Chart)

## 📁 Estrutura de Arquivos

### Novos Arquivos Criados
- `trading_setups.py` - Sistema completo dos 6 setups
- `modern_dashboard.py` - Interface moderna com analytics pro
- `run_dashboard.py` - Launcher para executar os dashboards
- `SETUP_DOCUMENTATION.md` - Esta documentação

### Arquivos Modificados
- `agent_system.py` - Integração com o novo sistema de setups

## 🚀 Como Executar

### Opção 1: Dashboard Moderno (Recomendado)
```bash
python run_dashboard.py --version modern
```

### Opção 2: Dashboard Legado
```bash
python run_dashboard.py --version legacy
```

### Opção 3: Execução Direta
```bash
streamlit run modern_dashboard.py
```

## ⚙️ Configurações Disponíveis

### Sidebar Settings
- **Refresh Rate** - Taxa de atualização dos dados
- **Show Charts** - Mostrar/ocultar gráficos de análise
- **Show Confidence Gauges** - Mostrar/ocultar medidores de confiança
- **Alert Threshold** - Limite para alertas de confiança

### Parâmetros do Sistema
- **Análise Mínima:** 90% de confiança
- **Operação Mínima:** 60% de confiança
- **Magic Number:** 234001
- **Lot Size:** 0.01
- **Risk/Reward Ratio:** 3.0

## 📊 Métricas e KPIs

### Indicadores Principais
1. **Confidence Score** - Pontuação de confiança (0-100%)
2. **Setup Status** - Estado atual do setup
3. **Risk Level** - Nível de risco da operação
4. **Target Price** - Preço alvo calculado
5. **Stop Loss** - Stop loss sugerido

### Análise de Performance
- **P&L Evolution** - Evolução do P&L ao longo do tempo
- **Setup Success Rate** - Taxa de sucesso por setup
- **Risk/Reward Analysis** - Análise de risco/retorno
- **Confidence Distribution** - Distribuição de confiança dos setups

## 🔧 Customização

### Ajuste de Parâmetros
Os limiares de confiança podem ser ajustados na classe `ConfidenceSystem`:
```python
self.analysis_threshold = 90.0  # Mínimo para análise
self.operation_threshold = 60.0  # Mínimo para operação
```

### Pesos dos Indicadores
Os pesos dos fatores de confiança podem ser modificados no método `calculate_confidence`:
```python
weights = {
    'charm_strength': 0.25,      # 25%
    'delta_alignment': 0.25,     # 25%
    'gamma_position': 0.20,      # 20%
    'price_action_confirmation': 0.15,  # 15%
    'volume_confirmation': 0.10, # 10%
    'vwap_alignment': 0.05       # 5%
}
```

## 🎨 Personalização Visual

### Cores do Tema
- **Primary:** #2a5298 (Azul)
- **Success:** #28a745 (Verde)
- **Warning:** #ffc107 (Amarelo)
- **Danger:** #dc3545 (Vermelho)
- **Background:** Gradientes modernos

### CSS Customizável
O arquivo `modern_dashboard.py` contém CSS customizável para personalizar:
- Cards de setup
- Barras de confiança
- Headers e métricas
- Responsive design

---

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema:
1. Verifique esta documentação primeiro
2. Execute `python run_dashboard.py --check` para verificar requisitos
3. Analise os logs de erro no console do Streamlit

**Sistema desenvolvido com foco em precisão, confiabilidade e usabilidade profissional.**