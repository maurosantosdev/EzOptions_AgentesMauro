import React from 'react';
import styled from 'styled-components';
import { 
  Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, Chip, Avatar 
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, AccountBalance, 
  Schedule, EuroSymbol, AttachMoney 
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
    background: rgba(52, 152, 219, 0.2) !important;
    font-weight: bold !important;
  }
`;

const PositionChip = styled(Chip)`
  background: ${props => {
    if (props.type === 'BUY') return 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important';
    if (props.type === 'SELL') return 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important';
    return 'linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important';
  }};
  color: white !important;
  font-weight: bold !important;
  font-size: 0.75rem !important;
`;

const ProfitCell = styled(TableCell)`
  font-weight: bold !important;
  color: ${props => {
    if (props.profit > 0) return '#2ecc71 !important';
    if (props.profit < 0) return '#e74c3c !important';
    return 'white !important';
  }};
`;

function PositionsTable({ positions }) {
  if (!positions || positions.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '20px', color: '#aaa' }}>
        <Schedule style={{ fontSize: '3rem', marginBottom: '10px' }} />
        <p>Nenhuma posição aberta</p>
      </div>
    );
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    const date = new Date(timeString);
    return date.toLocaleTimeString('pt-BR');
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value || 0);
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
            <StyledTableCell align="right">Lucro</StyledTableCell>
            <StyledTableCell align="right">Tempo</StyledTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {positions.map((position) => (
            <TableRow key={position.ticket} hover>
              <StyledTableCell>
                <strong>#{position.ticket}</strong>
              </StyledTableCell>
              <StyledTableCell>
                <Avatar 
                  sx={{ 
                    width: 24, 
                    height: 24, 
                    fontSize: '0.7rem',
                    bgcolor: 'rgba(52, 152, 219, 0.3)'
                  }}
                >
                  {position.symbol?.substring(0, 3) || 'SYM'}
                </Avatar>
                {position.symbol}
              </StyledTableCell>
              <StyledTableCell>
                <PositionChip 
                  icon={position.type === 'BUY' ? <TrendingUp /> : <TrendingDown />}
                  label={position.type}
                  type={position.type}
                  size="small"
                />
              </StyledTableCell>
              <StyledTableCell align="right">
                {formatNumber(position.volume)}
              </StyledTableCell>
              <StyledTableCell align="right">
                {formatNumber(position.priceOpen)}
              </StyledTableCell>
              <ProfitCell align="right" profit={position.profit}>
                {formatCurrency(position.profit)}
              </ProfitCell>
              <StyledTableCell align="right">
                {formatTime(position.timeOpen)}
              </StyledTableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </StyledTableContainer>
  );
}

export default PositionsTable;