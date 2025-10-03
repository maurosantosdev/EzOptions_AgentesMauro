/**
 * SERVIDOR WEBSOCKET PARA DASHBOARD EM TEMPO REAL
 * ===================================================
 * 
 * Este servidor se conecta ao sistema MT5 e transmite dados em tempo real
 * para o dashboard React através de WebSocket.
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
require('dotenv').config();

// Configuração do Express
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// Estado do sistema
let systemState = {
  clientsConnected: 0,
  lastUpdate: new Date().toISOString(),
  dataCache: {
    account: null,
    positions: [],
    orders: [],
    market: null,
    agents: null,
    performance: null
  }
};

console.log('🚀 [DASHBOARD SERVER] Iniciando servidor de dashboard em tempo real...');

// Gerar dados mock realistas
function generateMockAccountData() {
  const baseBalance = 9772.16; // Saldo atual da conta
  const profitVariation = (Math.random() * 200 - 100); // Variação aleatória
  
  return {
    login: 103486755,
    trade_mode: 4,
    leverage: 100,
    limit_orders: 200,
    margin_so_mode: 0,
    trade_allowed: true,
    trade_expert: true,
    margin_mode: 2,
    balance: baseBalance,
    equity: baseBalance + profitVariation,
    profit: profitVariation,
    credit: 0,
    margin: 0,
    margin_free: baseBalance + profitVariation,
    margin_level: 0,
    margin_so_call: 0,
    margin_so_so: 0,
    margin_initial: 0,
    margin_maintenance: 0,
    assets: 0,
    liabilities: 0,
    commission_blocked: 0,
    balance_prev: baseBalance,
    margin_prev: 0,
    assets_prev: 0,
    liabilities_prev: 0,
    margin_initial_prev: 0,
    margin_maintenance_prev: 0,
    name: "FBS Demo",
    server: "FBS-Demo",
    currency: "USD",
    company: "FBS",
    name_server: "FBS-Demo"
  };
}

function generateMockPositionsData() {
  // Simular algumas posições (ou nenhuma se não houver dados reais)
  if (Math.random() > 0.7) { // 30% chance de ter posições
    const numPositions = Math.floor(Math.random() * 3) + 1; // 1-3 posições
    const positions = [];
    
    for (let i = 0; i < numPositions; i++) {
      const isBuy = Math.random() > 0.5;
      const profit = (Math.random() * 100 - 50);
      const openPrice = 24500 + (Math.random() * 200 - 100);
      
      positions.push({
        ticket: 1000000 + Math.floor(Math.random() * 9000000),
        symbol: "US100",
        type: isBuy ? 0 : 1, // 0 = BUY, 1 = SELL
        type_desc: isBuy ? "BUY" : "SELL",
        volume: parseFloat((0.01 + Math.random() * 0.09).toFixed(2)),
        price_open: parseFloat(openPrice.toFixed(2)),
        sl: 0,
        tp: 0,
        price_current: parseFloat((openPrice + (isBuy ? profit : -profit)).toFixed(2)),
        profit: parseFloat(profit.toFixed(2)),
        swap: 0,
        commission: 0,
        time_open: new Date().toISOString(),
        time_type: 0,
        state: 0,
        magic: 234001,
        comment: "Auto Trade",
        external_id: "",
        deviation: 0,
        deviation_entry: 0,
        deviation_profit: 0,
        deviation_so: 0,
        storage_currency: "USD"
      });
    }
    
    return positions;
  }
  
  return [];
}

function generateMockOrdersData() {
  // Simular algumas ordens pendentes (ou nenhuma)
  if (Math.random() > 0.8) { // 20% chance de ter ordens
    const numOrders = Math.floor(Math.random() * 2) + 1; // 1-2 ordens
    const orders = [];
    
    for (let i = 0; i < numOrders; i++) {
      const orderTypes = ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP'];
      const orderType = orderTypes[Math.floor(Math.random() * orderTypes.length)];
      
      orders.push({
        ticket: 2000000 + Math.floor(Math.random() * 8000000),
        symbol: "US100",
        type: orderType,
        volume_initial: parseFloat((0.01 + Math.random() * 0.04).toFixed(2)),
        price_open: parseFloat((24500 + Math.random() * 100 - 50).toFixed(2)),
        sl: 0,
        tp: 0,
        deviation: 0,
        type_time: 0,
        time_setup: new Date().toISOString(),
        type_fill: 0,
        state: 0,
        magic: 234001,
        comment: "Pending Order",
        external_id: ""
      });
    }
    
    return orders;
  }
  
  return [];
}

function generateMockMarketData() {
  const basePrice = 24578.37; // Preço atual aproximado
  const variation = Math.random() * 50 - 25; // Variação aleatória
  
  return {
    symbol: "US100",
    bid: parseFloat((basePrice + variation - 1).toFixed(2)),
    ask: parseFloat((basePrice + variation + 1).toFixed(2)),
    last: parseFloat((basePrice + variation).toFixed(2)),
    volume: Math.floor(1000 + Math.random() * 9000),
    time: new Date().toISOString(),
    type: 1,
    volume_real: 0,
    digits: 2,
    spread: 2,
    spread_real: 0,
    tick_value: 0,
    tick_size: 0,
    contract_size: 1,
    point: 0.01
  };
}

function generateMockAgentsData() {
  return {
    active: Math.floor(6 + Math.random() * 4), // 6-10 agentes
    total: 10,
    communicating: Math.floor(4 + Math.random() * 6), // 4-10 comunicando
    decisions: {
      buy: Math.floor(Math.random() * 5),
      sell: Math.floor(Math.random() * 3),
      hold: Math.floor(Math.random() * 4)
    },
    systemHealth: Math.floor(70 + Math.random() * 30), // 70-100%
    averageConfidence: Math.floor(60 + Math.random() * 40), // 60-100%
    status: Math.random() > 0.8 ? 'Alerta' : 'Operacional',
    lastUpdate: new Date().toISOString()
  };
}

function generateMockPerformanceData() {
  return {
    dailyPnL: parseFloat((Math.random() * 100 - 50).toFixed(2)),
    winRate: parseFloat((60 + Math.random() * 30).toFixed(1)), // 60-90%
    profitFactor: parseFloat((1.2 + Math.random() * 1.8).toFixed(2)), // 1.2-3.0
    sharpeRatio: parseFloat((0.5 + Math.random() * 1.5).toFixed(2)), // 0.5-2.0
    maxDrawdown: parseFloat((-5 - Math.random() * 15).toFixed(2)), // -5% a -20%
    recoveryFactor: parseFloat((1.0 + Math.random() * 2.0).toFixed(2)) // 1.0-3.0
  };
}

// Atualizar dados em tempo real
async function updateRealTimeData() {
  try {
    console.log('🔄 [UPDATE] Atualizando dados em tempo real...');
    
    // Gerar todos os dados mock
    const accountData = generateMockAccountData();
    const positionsData = generateMockPositionsData();
    const ordersData = generateMockOrdersData();
    const marketData = generateMockMarketData();
    const agentsData = generateMockAgentsData();
    const performanceData = generateMockPerformanceData();
    
    // Atualizar cache
    systemState.dataCache = {
      account: accountData,
      positions: positionsData,
      orders: ordersData,
      market: marketData,
      agents: agentsData,
      performance: performanceData
    };
    
    systemState.lastUpdate = new Date().toISOString();
    
    // Enviar atualização para todos os clientes conectados
    if (systemState.clientsConnected > 0) {
      io.emit('realtime_update', {
        data: systemState.dataCache,
        timestamp: systemState.lastUpdate
      });
      
      console.log(`📤 [UPDATE] Dados transmitidos para ${systemState.clientsConnected} clientes`);
    }
    
  } catch (error) {
    console.error('❌ [UPDATE] Erro na atualização de dados:', error.message);
  }
}

// WebSocket event handlers
io.on('connection', (socket) => {
  console.log(`👥 [CLIENT] Novo cliente conectado: ${socket.id}`);
  systemState.clientsConnected++;
  
  // Enviar dados iniciais
  socket.emit('initial_data', {
    clientsConnected: systemState.clientsConnected,
    lastUpdate: systemState.lastUpdate,
    data: systemState.dataCache
  });
  
  // Handler para solicitações específicas
  socket.on('request_data', async (requestData) => {
    console.log(`📥 [REQUEST] Dados solicitados de ${socket.id}:`, requestData.type);
    
    // Enviar dados específicos
    const response = {
      requestId: requestData.id,
      type: requestData.type,
      data: systemState.dataCache[requestData.type] || systemState.dataCache,
      timestamp: new Date().toISOString()
    };
    
    socket.emit('data_response', response);
  });
  
  // Handler para desconexão
  socket.on('disconnect', () => {
    console.log(`👋 [CLIENT] Cliente desconectado: ${socket.id}`);
    systemState.clientsConnected--;
  });
  
  // Handler para erros
  socket.on('error', (error) => {
    console.error(`⚠️  [CLIENT] Erro no socket ${socket.id}:`, error.message);
  });
});

// Rotas HTTP REST
app.get('/', (req, res) => {
  res.json({
    message: 'Dashboard Server API',
    status: 'online',
    clientsConnected: systemState.clientsConnected,
    lastUpdate: systemState.lastUpdate
  });
});

app.get('/api/status', (req, res) => {
  res.json({
    status: 'online',
    clientsConnected: systemState.clientsConnected,
    lastUpdate: systemState.lastUpdate,
    uptime: process.uptime()
  });
});

app.get('/api/data', (req, res) => {
  res.json({
    data: systemState.dataCache,
    timestamp: systemState.lastUpdate
  });
});

app.get('/api/account', (req, res) => {
  res.json({
    account: systemState.dataCache.account,
    timestamp: systemState.lastUpdate
  });
});

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 [SERVER] Recebido SIGTERM. Encerrando...');
  server.close(() => {
    console.log('✅ [SERVER] Servidor encerrado.');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('🛑 [SERVER] Recebido SIGINT. Encerrando...');
  server.close(() => {
    console.log('✅ [SERVER] Servidor encerrado.');
    process.exit(0);
  });
});

// Iniciar servidor
const PORT = process.env.WS_PORT || 3002;
const HTTP_PORT = process.env.HTTP_PORT || 3001;

server.listen(PORT, () => {
  console.log(`📡 [SERVER] Servidor WebSocket rodando na porta ${PORT}`);
  console.log(`🌐 [SERVER] Servidor HTTP rodando na porta ${HTTP_PORT}`);
  console.log(`🔗 [SERVER] Dashboard disponível em http://localhost:${HTTP_PORT}`);
});

// Iniciar atualizações periódicas
console.log('⏰ [INIT] Iniciando atualizações periódicas a cada 2 segundos...');
setInterval(updateRealTimeData, 2000);

// Primeira atualização imediata
setTimeout(updateRealTimeData, 1000);