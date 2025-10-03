import React from 'react';
import styled from 'styled-components';
import { Card, CardContent, Typography, Grid, Chip } from '@mui/material';
import { AttachMoney, AccountBalanceWallet, ShowChart, TrendingUp, TrendingDown } from '@mui/icons-material';

const StyledCard = styled(Card)`
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px !important;
  backdrop-filter: blur(10px);
  color: white !important;
  height: 100%;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  }
`;

const StatValue = styled(Typography)`
  font-size: 1.8rem !important;
  font-weight: bold !important;
  margin: 10px 0 !important;
  color: ${props => {
    if (props.positive) return '#2ecc71';
    if (props.negative) return '#e74c3c';
    return '#3498db';
  }} !important;
`;

const StatLabel = styled(Typography)`
  font-size: 0.9rem !important;
  opacity: 0.8 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
`;

function AccountInfo({ data }) {
  if (!data) {
    return <div>Carregando dados da conta...</div>;
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value || 0);
  };

  const isPositive = (value) => value > 0;
  const isNegative = (value) => value < 0;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={4}>
        <StyledCard>
          <CardContent>
            <StatLabel>
              <AccountBalance /> Saldo
            </StatLabel>
            <StatValue positive>
              {formatCurrency(data.balance)}
            </StatValue>
          </CardContent>
        </StyledCard>
      </Grid>

      <Grid item xs={12} sm={6} md={4}>
        <StyledCard>
          <CardContent>
            <StatLabel>
              <ShowChart /> Equity
            </StatLabel>
            <StatValue positive={isPositive(data.equity - data.balance)}>
              {formatCurrency(data.equity)}
            </StatValue>
          </CardContent>
        </StyledCard>
      </Grid>

      <Grid item xs={12} sm={6} md={4}>
        <StyledCard>
          <CardContent>
            <StatLabel>
              <TrendingUp /> Lucro Atual
            </StatLabel>
            <StatValue 
              positive={isPositive(data.profit)} 
              negative={isNegative(data.profit)}
            >
              {formatCurrency(data.profit)}
            </StatValue>
          </CardContent>
        </StyledCard>
      </Grid>

      <Grid item xs={12} sm={6} md={4}>
        <StyledCard>
          <CardContent>
            <StatLabel>
              <AttachMoney /> Margem Livre
            </StatLabel>
            <StatValue positive>
              {formatCurrency(data.freeMargin)}
            </StatValue>
          </CardContent>
        </StyledCard>
      </Grid>

      <Grid item xs={12} sm={6} md={4}>
        <StyledCard>
          <CardContent>
            <StatLabel>
              Margem Usada
            </StatLabel>
            <StatValue>
              {formatCurrency(data.margin)}
            </StatValue>
          </CardContent>
        </StyledCard>
      </Grid>

      <Grid item xs={12} sm={6} md={4}>
        <StyledCard>
          <CardContent>
            <StatLabel>
              Nível de Margem
            </StatLabel>
            <StatValue>
              {data.margin > 0 ? ((data.equity / data.margin) * 100).toFixed(1) : '0'}%
            </StatValue>
          </CardContent>
        </StyledCard>
      </Grid>
    </Grid>
  );
}

export default AccountInfo;