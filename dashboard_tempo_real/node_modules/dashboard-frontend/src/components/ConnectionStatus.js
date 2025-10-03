import React from 'react';
import styled from 'styled-components';
import { Typography, Box, Chip } from '@mui/material';
import { CheckCircle, Error, Sync, Power } from '@mui/icons-material';

const StatusContainer = styled(Box)`
  background: rgba(255, 255, 255, 0.1) !important;
  border-radius: 12px !important;
  padding: 15px !important;
  backdrop-filter: blur(10px);
  border: 1px solid ${props => {
    switch(props.status) {
      case 'connected': return 'rgba(46, 204, 113, 0.5) !important';
      case 'disconnected': return 'rgba(231, 76, 60, 0.5) !important';
      case 'connecting': return 'rgba(241, 196, 15, 0.5) !important';
      default: return 'rgba(149, 165, 166, 0.5) !important';
    }
  }};
  margin-bottom: 20px !important;
  text-align: center !important;
`;

const StatusIcon = styled.span`
  font-size: 2rem !important;
  margin-right: 10px !important;
  vertical-align: middle !important;
  color: ${props => {
    switch(props.status) {
      case 'connected': return '#2ecc71 !important';
      case 'disconnected': return '#e74c3c !important';
      case 'connecting': return '#f1c40f !important';
      default: return '#95a5a6 !important';
    }
  }};
`;

function ConnectionStatus({ status }) {
  const getStatusText = () => {
    switch(status) {
      case 'connected': 
        return { 
          text: 'Conectado', 
          icon: <CheckCircle />, 
          color: '#2ecc71' 
        };
      case 'disconnected': 
        return { 
          text: 'Desconectado', 
          icon: <Error />, 
          color: '#e74c3c' 
        };
      case 'connecting': 
        return { 
          text: 'Conectando...', 
          icon: <Sync />, 
          color: '#f1c40f' 
        };
      default: 
        return { 
          text: 'Status desconhecido', 
          icon: <Power />, 
          color: '#95a5a6' 
        };
    }
  };

  const statusInfo = getStatusText();

  return (
    <StatusContainer status={status}>
      <Box display="flex" alignItems="center" justifyContent="center">
        <StatusIcon status={status}>
          {statusInfo.icon}
        </StatusIcon>
        <Typography variant="h5" component="h2" style={{ color: statusInfo.color }}>
          Status: {statusInfo.text}
        </Typography>
        <Chip 
          label={new Date().toLocaleTimeString('pt-BR')} 
          size="small"
          style={{ marginLeft: 20, backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
        />
      </Box>
    </StatusContainer>
  );
}

export default ConnectionStatus;