import React, { useEffect, useState } from 'react';

interface Metric {
    metric: string;
    result: number;
    legislationResults: string[];
    llmModelSummary: string[];

}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<Metric[]>([]);

  useEffect(() => {
    // Connect to the backend WebSocket server
    const socket = new WebSocket('ws://localhost:5005');

    // Check connection is open
    socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    // Listen for messages from the WebSocket server
    socket.onmessage = (event) => {
      const data = event.data;
      console.log('Received message:', data);

      try {
        // Parse the JSON string back into an array of dictionaries (objects)
        const parsedData: Metric[] = JSON.parse(data);
        console.log('Parsed data:', parsedData);
        setData(parsedData); // Store the parsed list of dictionaries in state
      } catch (e) {
        console.error('Error parsing JSON:', e);
      }
    };

    // Handle WebSocket errors
    socket.onerror = (err) => {
      console.log("WebSocket Error: ", err);
    };

    // Clean up the connection when the component unmounts
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div>
      <h1>Messages from RabbitMQ</h1>
      {data.length > 0 ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Waiting for messages...</p>
      )}
    </div>
  );
};

export default Dashboard;
