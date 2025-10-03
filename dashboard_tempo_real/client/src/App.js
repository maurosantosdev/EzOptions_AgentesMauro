import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Typography, Box, Grid, CircularProgress, Alert } from '@mui/material';

// Componentes
import ConnectionStatus from './components/ConnectionStatus';
import AccountInfo from './components/AccountInfo';
import MarketData from './components/MarketData';
import AgentsStatus from './components/AgentsStatus';
import PositionsTable from './components/PositionsTable';
import OrdersTable from './components/OrdersTable';
import PerformanceChart from './components/PerformanceChart';

// Tema customizado
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#4361ee',
    },
    secondary: {
      main: '#4cc9f0',
    },
    background: {
      default: '#0f0f1a',
      paper: '#1a1a2e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
  },
});

const DashboardContainer = styled(Container)`
  padding: 20px 0;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
`;

const Header = styled(Box)`
  text-align: center;
  margin-bottom: 30px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const Section = styled(Box)`
  background: rgba(255, 255, 255, 0.08);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  }
`;

const SectionTitle = styled(Typography)`
  color: #4cc9f0 !important;
  margin-bottom: 20px !important;
  font-weight: 600 !important;
  border-bottom: 2px solid rgba(76, 201, 240, 0.3);
  padding-bottom: 10px !important;
`;

const Footer = styled(Box)`
  text-align: center;
  margin-top: 30px;
  padding: 20px;
  color: #adb5bd;
  font-size: 0.9rem;
`;

function App() {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Simular conexão WebSocket
    const simulateWebSocketConnection = () => {
      console.log('[APP] Simulando conexão WebSocket...');
      
      // Simular conexão bem-sucedida após 1 segundo
      setTimeout(() => {
        setConnectionStatus('connected');
        setLoading(false);
        
        // Simular recepção de dados iniciais
        simulateDataReception();
        
        // Simular atualizações periódicas
        const interval = setInterval(simulateDataReception, 2000);
        
        return () => clearInterval(interval);
      }, 1000);
    };

    // Simular recepção de dados
    const simulateDataReception = () => {
      console.log('[APP] Simulando recepção de dados...');
      
      // Gerar dados mock realistas
      const mockData = generateMockData();
      setDashboardData(mockData);
    };

    // Gerar dados mock realistas
    const generateMockData = () => {
      const baseBalance = 9772.16;
      const profitVariation = (Math.random() * 200 - 100);
      
      return {
        account: {
          balance: baseBalance,
          equity: baseBalance + profitVariation,
          profit: profitVariation,
          margin: 0,
          freeMargin: baseBalance + profitVariation,
          login: 103486755,
          server: 'FBS-Demo'
        },
        positions: generateMockPositions(),
        orders: generateMockOrders(),
        market: generateMockMarket(),
        agents: generateMockAgents(),
        performance: generateMockPerformance()
      };
    };

    const generateMockPositions = () => {
      if (Math.random() > 0.7) {
        const numPositions = Math.floor(Math.random() * 3) + 1;
        return Array.from({ length: numPositions }, (_, i) => ({
          ticket: 1000000 + Math.floor(Math.random() * 9000000),
          symbol: 'US100',
          type: Math.random() > 0.5 ? 'BUY' : 'SELL',
          volume: parseFloat((0.01 + Math.random() * 0.09).toFixed(2)),
          price_open: parseFloat((24500 + Math.random() * 200 - 100).toFixed(2)),
          profit: parseFloat((Math.random() * 100 - 50).toFixed(2)),
          time_open: new Date(Date.now() - Math.floor(Math.random() * 86400000)).toISOString()
        }));
      }
      return [];
    };

    const generateMockOrders = () => {
      if (Math.random() > 0.8) {
        const numOrders = Math.floor(Math.random() * 2) + 1;
        const orderTypes = ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP'];
        return Array.from({ length: numOrders }, (_, i) => ({
          ticket: 2000000 + Math.floor(Math.random() * 8000000),
          symbol: 'US100',
          type: orderTypes[Math.floor(Math.random() * orderTypes.length)],
          volume_initial: parseFloat((0.01 + Math.random() * 0.04).toFixed(2)),
          price_open: parseFloat((24500 + Math.random() * 100 - 50).toFixed(2)),
          time_setup: new Date().toISOString()
        }));
      }
      return [];
    };

    const generateMockMarket = () => {
      const basePrice = 24578.37;
      const variation = Math.random() * 50 - 25;
      
      return {
        symbol: 'US100',
        bid: parseFloat((basePrice + variation - 1).toFixed(2)),
        ask: parseFloat((basePrice + variation + 1).toFixed(2)),
        last: parseFloat((basePrice + variation).toFixed(2)),
        spread: 2,
        volume: Math.floor(1000 + Math.random() * 9000)
      };
    };

    const generateMockAgents = () => ({
      active: Math.floor(6 + Math.random() * 4),
      total: 10,
      communicating: Math.floor(4 + Math.random() * 6),
      decisions: {
        buy: Math.floor(Math.random() * 5),
        sell: Math.floor(Math.random() * 3),
        hold: Math.floor(Math.random() * 4)
      },
      systemHealth: Math.floor(70 + Math.random() * 30),
      averageConfidence: Math.floor(60 + Math.random() * 40),
      status: Math.random() > 0.8 ? 'Alerta' : 'Operacional'
    });

    const generateMockPerformance = () => ({
      dailyPnL: parseFloat((Math.random() * 100 - 50).toFixed(2)),
      winRate: parseFloat((60 + Math.random() * 30).toFixed(1)),
      profitFactor: parseFloat((1.2 + Math.random() * 1.8).toFixed(2)),
      sharpeRatio: parseFloat((0.5 + Math.random() * 1.5).toFixed(2)),
      maxDrawdown: parseFloat((-5 - Math.random() * 15).toFixed(2))
    });

    // Iniciar simulação
    const cleanup = simulateWebSocketConnection();
    
    // Cleanup
    return () => {
      if (cleanup) cleanup();
    };
  }, []);

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          flexDirection="column"
        >
          <CircularProgress size={60} thickness={4} />
          <Typography variant="h6" style={{ marginTop: 20 }}>
            Carregando Dashboard em Tempo Real...
          </Typography>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DashboardContainer maxWidth="xl">
        <Header>
          <Typography variant="h1" component="h1" gutterBottom>
            📊 DASHBOARD EM TEMPO REAL - EZOPTIONS AGENTS
          </Typography>
          <Typography variant="h5" component="h2" color="textSecondary">
            Monitoramento Avançado de Agentes de Trading Automáticos
          </Typography>
        </Header>

        <ConnectionStatus status={connectionStatus} />

        {error && (
          <Alert severity="error" style={{ marginBottom: 20 }}>
            {error}
          </Alert>
        )}

        {/* Resumo Rápido */}
        <Section>
          <SectionTitle variant="h3">
            🚀 RESUMO RÁPIDO
          </SectionTitle>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} borderRadius={2} bgcolor="rgba(67, 97, 238, 0.2)">
                <Typography variant="h4" color="primary">
                  ${(dashboardData.account?.equity || 0).toFixed(2)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Equity Total
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} borderRadius={2} bgcolor="rgba(76, 201, 240, 0.2)">
                <Typography variant="h4" color="secondary">
                  {dashboardData.positions?.length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Posições Abertas
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} borderRadius={2} bgcolor="rgba(46, 204, 113, 0.2)">
                <Typography variant="h4" style={{ color: '#2ecc71' }}>
                  {(dashboardData.agents?.systemHealth || 0).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Saúde do Sistema
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} borderRadius={2} bgcolor="rgba(231, 76, 60, 0.2)">
                <Typography variant="h4" style={{ color: '#e74c3c' }}>
                  {dashboardData.orders?.length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Ordens Pendentes
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Section>

        {/* Dados Principais */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Section>
              <SectionTitle variant="h3">
                💰 CONTA
              </SectionTitle>
              <AccountInfo data={dashboardData.account} />
            </Section>
          </Grid>

          <Grid item xs={12} md={4}>
            <Section>
              <SectionTitle variant="h3">
                📈 MERCADO
              </SectionTitle>
              <MarketData data={dashboardData.market} />
            </Section>
          </Grid>

          <Grid item xs={12} md={4}>
            <Section>
              <SectionTitle variant="h3">
                🤖 AGENTES
              </SectionTitle>
              <AgentsStatus data={dashboardData.agents} />
            </Section>
          </Grid>
        </Grid>

        {/* Gráfico de Performance */}
        <Section>
          <SectionTitle variant="h3">
            📊 PERFORMANCE
          </SectionTitle>
          <PerformanceChart data={dashboardData.performance} />
        </Section>

        {/* Tabelas de Dados */}
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <Section>
              <SectionTitle variant="h3">
                📝 POSIÇÕES ABERTAS
              </SectionTitle>
              <PositionsTable positions={dashboardData.positions} />
            </Section>
          </Grid>

          <Grid item xs={12} lg={6}>
            <Section>
              <SectionTitle variant="h3">
                📋 ORDENS PENDENTES
              </SectionTitle>
              <OrdersTable orders={dashboardData.orders} />
            </Section>
          </Grid>
        </Grid>

        <Footer>
          <Typography variant="body2">
            Sistema de Agentes EzOptions - Dashboard em Tempo Real
          </Typography>
          <Typography variant="caption">
            Última atualização: {new Date().toLocaleString('pt-BR')}
          </Typography>
        </Footer>
      </DashboardContainer>
    </ThemeProvider>
  );
}

export default App;