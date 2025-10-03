import React from 'react';
import styled from 'styled-components';
import { 
  Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, Chip, Avatar 
} from '@mui/material';
import { 
  ShoppingCart, ShoppingCartOutlined, Alarm, 
  EuroSymbol, AttachMoney, Schedule 
} from '@mui/icons-material';

const StyledTableContainer = styled(TableContainer)`
  background: rgba(255, 255, 255, 0.05) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white !important;
`;

const StyledTableCell = styled(TableCell)`
  color: white !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  
  &.MuiTableCell-head {
    background: rgba(155, 89, 182, 0.2) !important;
    font-weight: bold !important;
  }
`;

const OrderChip = styled(Chip)`
  background: ${props => {
    switch(props.type) {
      case 'BUY_LIMIT':
        return 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important';
      case 'SELL_LIMIT':
        return 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important';
      case 'BUY_STOP':
        return 'linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important';
      case 'SELL_STOP':
        return 'linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%) !important';
      default:
        return 'linear-gradient(135deg, #f39c12 0%, #d35400 100%) !important';
    }
  }};
  color: white !important;
  font-weight: bold !important;
  font-size: 0.7rem !important;
`;

const TimeCell = styled(TableCell)`
  font-size: 0.8rem !important;
  color: #aaa !important;
`;

function OrdersTable({ orders }) {
  if (!orders || orders.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '20px', color: '#aaa' }}>
        <Alarm style={{ fontSize: '3rem', marginBottom: '10px' }} />
        <p>Nenhuma ordem pendente</p>
      </div>
    );
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value || 0);
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    const date = new Date(timeString);
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const getOrderIcon = (type) => {
    switch(type) {
      case 'BUY_LIMIT':
      case 'BUY_STOP':
        return <ShoppingCart />;
      case 'SELL_LIMIT':
      case 'SELL_STOP':
        return <ShoppingCartOutlined />;
      default:
        return <Alarm />;
    }
  };

  return (
    <StyledTableContainer component={Paper}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <StyledTableCell>Ticket</StyledTableCell>
            <StyledTableCell>Símbolo</StyledTableCell>
            <StyledTableCell>Tipo</StyledTableCell>
            <StyledTableCell align="right">Volume</StyledTableCell>
            <StyledTableCell align="right">Preço</StyledTableCell>
            <StyledTableCell align="right">Hora</StyledTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {orders.map((order) => (
            <TableRow key={order.ticket} hover>
              <StyledTableCell>
                <strong>#{order.ticket}</strong>
              </StyledTableCell>
              <StyledTableCell>
                <Avatar 
                  sx={{ 
                    width: 24, 
                    height: 24, 
                    fontSize: '0.7rem',
                    bgcolor: 'rgba(155, 89, 182, 0.3)'
                  }}
                >
                  {order.symbol?.substring(0, 3) || 'SYM'}
                </Avatar>
                {order.symbol}
              </StyledTableCell>
              <StyledTableCell>
                <OrderChip 
                  icon={getOrderIcon(order.type)}
                  label={order.type?.replace('_', ' ') || 'UNKNOWN'}
                  type={order.type}
                  size="small"
                />
              </StyledTableCell>
              <StyledTableCell align="right">
                {formatCurrency(order.volumeInitial || order.volume)}
              </StyledTableCell>
              <StyledTableCell align="right">
                {formatCurrency(order.priceOpen || order.price)}
              </StyledTableCell>
              <TimeCell align="right">
                {formatTime(order.timeSetup || new Date())}
              </TimeCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </StyledTableContainer>
  );
}

export default OrdersTable;