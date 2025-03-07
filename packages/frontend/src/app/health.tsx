import React, { useState, useEffect } from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { styles } from './home.styles';
import theme from './theme';

interface ServiceHealth {
  name: string;
  url: string;
  status: string;
}

const Health: React.FC = () => {
  const [services, setServices] = useState<ServiceHealth[]>([
    // TODO: Update URLs with prod versions
    { name: 'Dispatcher', url: '/dispatcher/health', status: 'Checking...' },
    { name: 'Job Queue', url: '/job-queue/health', status: 'Checking...' },
    { name: 'Aggregator', url: '/aggregator/health', status: 'Checking...' },
    { name: 'Results Queue', url: '/results-queue/health', status: 'Checking...' },
  ]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkHealth = async () => {
      const updatedServices = await Promise.all(
        services.map(async (service) => {
          try {
            const response = await fetch(service.url);
            if (response.ok) {
              return { ...service, status: 'Service is healthy' };
            } else {
              return { ...service, status: 'Service is not healthy' };
            }
          } catch (error) {
            return { ...service, status: 'Service is down' };
          }
        })
      );

      setServices(updatedServices);
      setLoading(false);
    };

    checkHealth();
  }, []);

  return (
    <Box
      sx={{
        ...styles.container,
        bgcolor: theme.palette.primary.main,
        borderRadius: '10px',
        boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.5)',
        padding: 3,
        textAlign: 'center',
      }}
    >
      {loading ? (
        <CircularProgress />
      ) : (
        services.map((service) => (
          <Box key={service.name} sx={{ marginBottom: 2 }}>
            <Typography
              variant="h6"
              style={{
                color: service.status === 'Service is healthy' ? 'green' : 'red',
              }}
            >
              {service.name}: {service.status}
            </Typography>
          </Box>
        ))
      )}
    </Box>
  );
};

export default Health;
