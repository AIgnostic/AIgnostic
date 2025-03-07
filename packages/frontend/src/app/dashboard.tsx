import React, { useEffect, useState } from 'react';
import ErrorMessage from './components/ErrorMessage';
import theme from './theme';
import { styled } from '@mui/material/styles';
import { Metric } from './types';
import ReportRenderer from './components/ReportRenderer';
import MetricBar from './components/MetricBar';

import LinearProgress, {
  linearProgressClasses,
} from '@mui/material/LinearProgress';
import { pdf } from '@react-pdf/renderer';
import { v4 as uuidv4 } from 'uuid';
import { BACKEND_STOP_JOB_URL } from './constants';
import { styles } from './home.styles';
import { Button } from '@mui/material';

interface DashboardProps {
  onComplete: () => void;
  socket: WebSocket | null;
  disconnectRef: React.MutableRefObject<boolean>;
  expectedItems: number;
}

// Each item from the websocket is an array of Metric objects.
const Dashboard: React.FC<DashboardProps> = ({ onComplete, socket, disconnectRef, expectedItems }) => {
  // 'items' holds each item (which is an array of Metric objects) received from the socket.
  const [items, setItems] = useState<Metric[]>([]);
  const [log, setLog] = useState<string>('Log: Processing metrics...');
  const [error, setError] = useState<{ header: string; text: string }>({
    header: '',
    text: '',
  });
  const [showError, setShowError] = useState<boolean>(false);
  const [retryButton, setRetryButton] = useState<JSX.Element | null>(null);


  const buttonRetry = (
    <button
      onClick={() => {
        window.location.reload();
      }}
      style={{ marginTop: '10px', padding: '10px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
    >
      Retry
    </button>
  );

  // const [report, setReport] = useState<Report | null>(null);

  const earlyStop = async () => {
    // close the socket so that you dont keep receiving errors
    console.log("Closing socket due to error");
    if (socket) {
      disconnectRef.current = true; // intentional disconnect, don't retry
      socket.close();
    }

    let id = sessionStorage.getItem('userId');
    console.log("Stopping job with id: ", id);
    // ping api to stop processing batches for this job
    await fetch(BACKEND_STOP_JOB_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ job_id: id }),
    });

    // clear userId in session storage
    // to avoid reconnecting with the same userId on reload
    sessionStorage.removeItem('userId');
  }

  useEffect(() => {
    if (socket) {
      socket.onmessage = (event) => {
        const sanitizedData = event.data.replace(/NaN/g, 'null');
        const data = JSON.parse(sanitizedData);
        console.log('Received message:', data);

        switch (data.messageType) {
          case 'LOG':
            setLog(`Log: ${data.message}`);
            break;
          case 'METRICS_COMPLETE':
            setLog(`Log: ${data.message}`);
            break;
          case 'METRICS_INTERMEDIATE':
            try {
              // Assume each intermediate message contains one item with multiple metrics.
              const newItem: Metric = data.content.metrics_results;

              console.log('New item:', newItem);
              // Append the new item to our list of items.
              setItems((prevItems) => {
                const updatedItems = [...prevItems, newItem];
                if (updatedItems.length >= expectedItems) {
                  setTimeout(onComplete, 0);
                  setShowError(true);
                  setError({
                    header: 'Report is being generated',
                    text: 'This may take a few seconds',
                  });
                }
                return updatedItems;
              });
            } catch (e: any) {
              setShowError(true);
              setError({ header: 'Error parsing data:', text: e.message });
            }

            break;
          case 'REPORT': {
            const generateReport = async () => {
              console.log('Results received:', data.content);
              // setReport(data.content);
              console.log('Report:', data.content);
              const blob = await pdf(
                <ReportRenderer report={data.content} />
              ).toBlob();
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'AIgnostic_Report.pdf'; // Set the file name
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
              if (error.header === 'Report is being generated') {
                setShowError(false);
              }
              setRetryButton(buttonRetry);
            };
            generateReport();
            break;
          }
          case 'ERROR': {
            const handleError = async () => {
              setShowError(true);
              setError({ header: 'Error 500:', text: `${data.message} : ${data.content}` });
              earlyStop()
              setLog("Log: An error occurred during the computation of the metrics. Please try again later.");
              setRetryButton(buttonRetry);
            }
            handleError();
            break;
          }
          default:
            console.log(
              'Unknown response from server:',
              data,
              data.messageType
            );
            setShowError(true);
            setError({
              header: 'Unknown response from server:',
              text: data.message,
            });
        }
      };

      return () => {
        socket?.close();
      };
    }
  }, [onComplete, socket]);

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

      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '10px',
        }}
      >

        <p>{log}</p>

        <Button onClick={async () => {
          await earlyStop();
          setItems([]);
          setLog("Log: Evaluation pipeline cancelled. Reload page?");
          setRetryButton(buttonRetry);
        }}
          style={styles.button}>
          
          Stop Early
        </Button>
      </div>

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
          items.slice(-1).map((item, itemIndex) => {
            return (
              <div
                key={itemIndex}
                style={{ ...metricCardStyle, flex: '1 1 calc(33.333% - 16px)' }}
              >
                {Object.entries(item).map(
                  ([metric_name, metric_info], metricIndex) => (
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
                        <h3>{metric_name.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())}</h3>
                      </div>
                      <div>
                        {(metric_info.error !== null) ?
                          <div>
                            <p style={{ color: 'red' }}>An error occurred during the computation of this metric.</p>
                          </div>
                          :
                          <MetricBar

                            min={metric_info.range[0]}
                            max={metric_info.range[1]}
                            actual={metric_info.value}
                            ideal={metric_info.ideal_value}
                            label=""
                          />
                        }
                      </div>
                    </div>
                  ))}
              </div>
            );
          })
        ) :
          (retryButton === null) ? <p></p> : retryButton
        }
      </div>
    </div>
  );
};

export default Dashboard;
