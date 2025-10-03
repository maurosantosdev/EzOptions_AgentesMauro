import React from 'react';
import styled from 'styled-components';
import { Card, CardContent, Typography, LinearProgress, Chip, Avatar } from '@mui/material';
import { 
  SmartToy, Psychology, Group, CheckCircle, 
  Warning, Error, PlayArrow, Pause, Stop 
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

const AgentRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  &:last-child {
    border-bottom: none;
  }
`;

const AgentIcon = styled(Avatar)`
  background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%) !important;
  width: 32px !important;
  height: 32px !important;
  font-size: 16px !important;
`;

const StatusChip = styled(Chip)`
  background: ${props => {
    switch(props.status) {
      case 'active': return 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important';
      case 'inactive': return 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important';
      case 'paused': return 'linear-gradient(135deg, #f39c12 0%, #d35400 100%) !important';
      case 'warning': return 'linear-gradient(135deg, #f1c40f 0%, #f39c12 100%) !important';
      default: return 'linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important';
    }
  }};
  color: white !important;
  font-weight: bold !important;
  font-size: 0.75rem !important;
`;

const ProgressContainer = styled.div`
  margin-top: 15px;
`;

const ProgressBar = styled(LinearProgress)`
  height: 6px !important;
  border-radius: 3px !important;
  background: rgba(255, 255, 255, 0.1) !important;

  .MuiLinearProgress-bar {
    background: ${props => {
      const value = props.value || 0;
      if (value >= 80) return '#2ecc71'; // Verde para alto desempenho
      if (value >= 60) return '#f1c40f'; // Amarelo para médio desempenho
      return '#e74c3c'; // Vermelho para baixo desempenho
    }} !important;
  }
`;

function AgentsStatus({ data }) {
  if (!data) {
    return <div>Carregando status dos agentes...</div>;
  }

  const getStatusColor = (value) => {
    if (value >= 80) return '#2ecc71';
    if (value >= 60) return '#f1c40f';
    return '#e74c3c';
  };

  const getAgentStatus = (activeCount, totalCount) => {
    const ratio = totalCount > 0 ? (activeCount / totalCount) : 0;
    if (ratio >= 0.8) return 'active';
    if (ratio >= 0.5) return 'warning';
    return 'inactive';
  };

  return (
    <StyledCard>
      <CardContent>
        <AgentRow>
          <Typography variant="h6" component="h3">
            <SmartToy /> Agentes Ativos
          </Typography>
          <Typography variant="h6" component="span">
            {data.active || 0}/{data.total || 10}
          </Typography>
        </AgentRow>

        <AgentRow>
          <Typography variant="body2">
            <Group /> Comunicando
          </Typography>
          <Typography variant="body2" style={{ fontWeight: 'bold' }}>
            {data.communicating || 0}/{data.active || 0}
          </Typography>
        </AgentRow>

        <AgentRow>
          <Typography variant="body2">
            <CheckCircle style={{ color: '#2ecc71' }} /> Decisões BUY
          </Typography>
          <Typography variant="body2" style={{ fontWeight: 'bold', color: '#2ecc71' }}>
            {data.decisions?.buy || 0}
          </Typography>
        </AgentRow>

        <AgentRow>
          <Typography variant="body2">
            <Warning style={{ color: '#f1c40f' }} /> Decisões SELL
          </Typography>
          <Typography variant="body2" style={{ fontWeight: 'bold', color: '#f1c40f' }}>
            {data.decisions?.sell || 0}
          </Typography>
        </AgentRow>

        <AgentRow>
          <Typography variant="body2">
            <Pause style={{ color: '#3498db' }} /> Decisões HOLD
          </Typography>
          <Typography variant="body2" style={{ fontWeight: 'bold', color: '#3498db' }}>
            {data.decisions?.hold || 0}
          </Typography>
        </AgentRow>

        <ProgressContainer>
          <Typography variant="caption" style={{ marginBottom: '5px' }}>
            Saúde do Sistema: {(data.systemHealth || 0).toFixed(1)}%
          </Typography>
          <ProgressBar 
            variant="determinate" 
            value={data.systemHealth || 0} 
          />
        </ProgressContainer>

        <ProgressContainer>
          <Typography variant="caption" style={{ marginBottom: '5px' }}>
            Confiança Média: {(data.averageConfidence || 0).toFixed(1)}%
          </Typography>
          <ProgressBar 
            variant="determinate" 
            value={data.averageConfidence || 0} 
          />
        </ProgressContainer>

        <AgentRow style={{ marginTop: '15px' }}>
          <StatusChip 
            icon={<Psychology />}
            label={`Status: ${data.status || 'Desconhecido'}`}
            status={getAgentStatus(data.active, data.total)}
            size="small"
          />
        </AgentRow>
      </CardContent>
    </StyledCard>
  );
}

export default AgentsStatus;