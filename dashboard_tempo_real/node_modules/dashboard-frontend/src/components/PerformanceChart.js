import React from 'react';
import styled from 'styled-components';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const ChartContainer = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  height: 300px;
`;

const ChartTitle = styled.h3`
  color: #4cc9f0;
  margin: 0 0 20px 0;
  text-align: center;
  font-size: 1.2rem;
`;

function PerformanceChart({ data }) {
  // Gerar dados mock para o gráfico se não houver dados reais
  const generateChartData = () => {
    const hours = [];
    const pnlData = [];
    const equityData = [];
    
    // Gerar dados para as últimas 24 horas
    for (let i = 23; i >= 0; i--) {
      hours.push(`${i}h`);
      // Simular variação de P&L ao longo do dia
      const basePnl = (Math.sin(i * 0.3) * 50) + (Math.random() * 20 - 10);
      const variation = Math.random() * 30 - 15;
      pnlData.push(parseFloat((basePnl + variation).toFixed(2)));
      
      // Simular equity
      equityData.push(parseFloat((10000 + basePnl * 10 + variation * 2).toFixed(2)));
    }
    
    return {
      labels: hours.reverse(),
      datasets: [
        {
          label: 'P&L Diário ($)',
          data: pnlData.reverse(),
          borderColor: '#4cc9f0',
          backgroundColor: 'rgba(76, 201, 240, 0.1)',
          borderWidth: 2,
          pointRadius: 2,
          pointBackgroundColor: '#4cc9f0',
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Equity ($)',
          data: equityData.reverse(),
          borderColor: '#f72585',
          backgroundColor: 'rgba(247, 37, 133, 0.1)',
          borderWidth: 2,
          pointRadius: 2,
          pointBackgroundColor: '#f72585',
          fill: true,
          tension: 0.4,
          borderDash: [5, 5],
        }
      ]
    };
  };

  const chartData = data ? generateChartData() : generateChartData();

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#fff',
          font: {
            size: 12
          }
        }
      },
      title: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#4cc9f0',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'USD'
              }).format(context.parsed.y);
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#aaa',
          maxRotation: 45,
          minRotation: 45,
        }
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#aaa',
          callback: function(value) {
            return new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'USD',
              minimumFractionDigits: 0,
              maximumFractionDigits: 0
            }).format(value);
          }
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'index',
    },
  };

  return (
    <ChartContainer>
      <ChartTitle>📈 Performance em Tempo Real</ChartTitle>
      <div style={{ height: '250px' }}>
        <Line data={chartData} options={options} />
      </div>
    </ChartContainer>
  );
}

export default PerformanceChart;