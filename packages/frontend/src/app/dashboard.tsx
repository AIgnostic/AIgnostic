import React, { useEffect, useState } from 'react';
import ErrorMessage from './components/ErrorMessage';
import theme from './theme';
import Box from '@mui/material/Box';
import { styled } from '@mui/material/styles';

import LinearProgress, {
  linearProgressClasses,
} from '@mui/material/LinearProgress';

import Grid from '@mui/material/Grid';

interface Metric {
  metric: string;
  result: number;
  legislationResults: string[];
  llmModelSummary: string[];
}

interface DashboardProps {
  onComplete: () => void;
}

// Each item from the websocket is an array of Metric objects.
const Dashboard: React.FC<DashboardProps> = ({ onComplete }) => {
  // 'items' holds each item (which is an array of Metric objects) received from the socket.
  const [items, setItems] = useState<Metric[][]>([]);
  const [log, setLog] = useState<string>('');
  const [error, setError] = useState<{ header: string; text: string }>({
    header: '',
    text: '',
  });
  const [showError, setShowError] = useState<boolean>(false);

  // We expect to receive 20 items total.
  const expectedItems = 20 * 20;

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:5005');

    socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);

      switch (data.messageType) {
        case 'LOG':
          setLog(data.message);
          break;
        case 'METRICS_COMPLETE':
          setLog(data.message);
          break;
        case 'METRICS_INTERMEDIATE':
          try {
            // Assume each intermediate message contains one item with multiple metrics.
            const newItem: Metric[] = data.content.metrics_results;
            // Append the new item to our list of items.
            setItems((prevItems) => {
              const updatedItems = [...prevItems, newItem];
              if (updatedItems.length >= expectedItems) {
                onComplete();
              }
              return updatedItems;
            });
          } catch (e: any) {
            setShowError(true);
            setError({ header: 'Error parsing data:', text: e.message });
          }
          break;
        case 'REPORT':
          // Handle report data if needed.
          break;
        case 'ERROR':
          setShowError(true);
          setError({ header: 'Error 500:', text: data.message });
          break;
        default:
          console.log('Unknown response from server:', data, data.messageType);
          setShowError(true);
          setError({
            header: 'Unknown response from server:',
            text: data.message,
          });
      }
    };

    return () => {
      socket.close();
    };
  }, [onComplete]);

  // Calculate overall progress as the number of items received divided by the expected total.
  const overallProgress = Math.min(items.length / expectedItems, 1);

  // Styling (using CSS variables for theme colors, adjust as needed)
  const metricCardStyle: React.CSSProperties = {
    border: '1px solid var(--theme-background-default)',
    borderRadius: '8px',
    padding: '16px',
    margin: '8px 0',
    backgroundColor: 'var(--theme-background-paper)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  };

  const BorderLinearProgress = styled(LinearProgress)(({ theme }) => ({
    height: 10,
    borderRadius: 5,
    [`&.${linearProgressClasses.colorPrimary}`]: {
      backgroundColor: theme.palette.grey[200],
      ...theme.applyStyles('dark', {
        backgroundColor: theme.palette.grey[800],
      }),
    },
    [`& .${linearProgressClasses.bar}`]: {
      borderRadius: 5,
      backgroundColor: '#1a90ff',
      ...theme.applyStyles('dark', {
        backgroundColor: '#308fe8',
      }),
      transition: 'background-color 0.3s ease',
    },
    [`& .${linearProgressClasses.barColorPrimary}`]: {
      backgroundColor: '#1a90ff',
      ...(overallProgress === 1 && {
        backgroundColor: '#4caf50', // Change color to green when at 100%
      }),
    },
  }));

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {showError && (
        <ErrorMessage
          onClose={() => setShowError(false)}
          errorHeader={error.header}
          errorMessage={error.text}
        />
      )}
      <BorderLinearProgress
        variant="determinate"
        value={overallProgress * 100}
      />
      <p>
        {items.length} / {expectedItems} batches processed
      </p>

      {/* Render each item as a card */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', // Tiles adapt to screen size
          gap: '16px',
          width: '100%',
          marginTop: '16px',
        }}
      >
        {items.length > 0 ? (
          items.slice(-1).map((item, itemIndex) => (
            <div
              key={itemIndex}
              style={{ ...metricCardStyle, flex: '1 1 calc(33.333% - 16px)' }}
            >
              {item.map((metric, metricIndex) => (
                <div
                  key={metricIndex}
                  style={{
                    border: `3px solid ${theme.palette.background.paper}`,
                    marginBottom: '8px',
                    backgroundColor: theme.palette.background.default,
                    padding: '16px',
                    borderRadius: '8px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  }}
                >
                  <div
                    style={{
                      backgroundColor: theme.palette.background.paper,
                      border: `1px solid #fff`,
                      padding: '8px 16px',
                      borderRadius: '8px',
                      marginBottom: '8px',
                    }}
                  >
                    <h3>{metric.metric}</h3>
                  </div>
                  <p>Result: {metric.result}</p>
                  <p>Legislation Results: {metric.legislationResults}</p>
                  <p>LLM Model Summary: {metric.llmModelSummary}</p>
                </div>
              ))}
            </div>
          ))
        ) : (
          <p>Waiting for messages...</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
