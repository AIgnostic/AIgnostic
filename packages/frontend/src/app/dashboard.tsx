import React, { useEffect, useState } from 'react';
import ErrorMessage from './components/ErrorMessage';
import { generateReportText } from './utils';

interface AggregatorResponse {
  messageType: string;
  message: string;
  statusCode: number;
  content: string;
}

interface Report {
  metric: string;
  result: number;
  legislationResults: string[];
  llmModelSummary: string[];
}

const Dashboard: React.FC = (DashboardProps) => {
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);
  const [log, setLog] = useState<string>("");
  const [report, setReport] = useState<Report[] | null>(null);
  const [error, setError] = useState<{ header: string; text: string }>({ header: '', text: '' });
  const [showError, setShowError] = useState<boolean>(false);

  useEffect(() => {
    // Connect to the backend WebSocket server
    const socket = new WebSocket('ws://localhost:5005');

    // Check connection is open
    socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    // Listen for messages from the WebSocket server
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
            // Parse the JSON string back into an array of dictionaries (objects)
            console.log('Data content:', data.content);
            const parsedData: Record<string, number> = data.content.metrics_results;
            console.log('Parsed data:', parsedData);
            setMetrics(parsedData); // Store the parsed list of dictionaries in state
          } catch (e: any) {
            setShowError(true);
            setError({ header: 'Error parsing data:', text: e.message });
          } finally {
            break;
          }
        case 'REPORT':
          console.log("Results received:", data.content)
          setReport(data.content);
          console.log('Report:', data.content);
          const doc = generateReportText(data.content);
          doc.save('AIgnostic_Report.pdf');
          break;
        case 'ERROR':
          setShowError(true);
          setError({ header: 'Error 500:', text: data.message });
          break;
        default:
          console.log('Unknown response from server:', data, data.messageType);
          setShowError(true);
          setError({ header: 'Unknown response from server:', text: data.message });
      }
    };

    // // Handle WebSocket errors
    // socket.onerror = (err: any) => {
    //   setShowError(true);
    //   setError({ header: 'WebSocket Error:', text: err.message });
    // };

    // Clean up the connection when the component unmounts
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div>
      <h1>Messages from RabbitMQ</h1>
      {showError && (
        <ErrorMessage
          onClose={() => setShowError(false)}
          errorHeader={error.header}
          errorMessage={error.text}
        />
      )}
      <p>Log: {log}</p>
      {metrics !== null ? (
        <pre>{JSON.stringify(metrics, null, 2)}</pre>
      ) : (
        <p>Waiting for messages...</p>
      )}
    </div>
  );
};

export default Dashboard;
