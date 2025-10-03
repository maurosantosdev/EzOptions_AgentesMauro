import React from 'react';
import styled from 'styled-components';
import { Card, CardContent, Typography, Chip, Avatar } from '@mui/material';
import { 
  TrendingUp, TrendingDown, ShowChart, BarChart, 
  AccountBalance, SwapVert, EuroSymbol 
} from '@mui/icons-material';

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

const MarketRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  &:last-child {
    border-bottom: none;
  }
`;

const SymbolChip = styled(Chip)`
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
  color: white !important;
  font-weight: bold !important;
`;

const PriceValue = styled.span`
  font-weight: bold;
  color: ${props => props.color || '#3498db'};
`;

const SpreadValue = styled.span`
  background: rgba(52, 152, 219, 0.2);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
`;

function MarketData({ data }) {
  if (!data) {
    return <div>Carregando dados de mercado...</div>;
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price || 0);
  };

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
      return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toString();
  };

  return (
    <StyledCard>
      <CardContent>
        <MarketRow>
          <Typography variant="h6" component="h3">
            <ShowChart /> {data.symbol || 'US100'}
          </Typography>
          <SymbolChip label={data.symbol || 'US100'} size="small" />
        </MarketRow>

        <MarketRow>
          <Typography variant="body2">
            <TrendingUp style={{ color: '#2ecc71' }} /> Bid
          </Typography>
          <PriceValue color="#2ecc71">
            {formatPrice(data.bid)}
          </PriceValue>
        </MarketRow>

        <MarketRow>
          <Typography variant="body2">
            <TrendingDown style={{ color: '#e74c3c' }} /> Ask
          </Typography>
          <PriceValue color="#e74c3c">
            {formatPrice(data.ask)}
          </PriceValue>
        </MarketRow>

        <MarketRow>
          <Typography variant="body2">
            <EuroSymbol /> Último
          </Typography>
          <PriceValue>
            {formatPrice(data.last)}
          </PriceValue>
        </MarketRow>

        <MarketRow>
          <Typography variant="body2">
            <SwapVert /> Spread
          </Typography>
          <SpreadValue>
            {formatPrice(data.spread || (data.ask - data.bid))}
          </SpreadValue>
        </MarketRow>

        <MarketRow>
          <Typography variant="body2">
            <BarChart /> Volume
          </Typography>
          <Typography variant="body2" style={{ fontWeight: 'bold' }}>
            {formatVolume(data.volume)}
          </Typography>
        </MarketRow>
      </CardContent>
    </StyledCard>
  );
}

export default MarketData;