import React from 'react';
import { Box, Button } from '@mui/material';
import { styles } from '../home.styles';
import { HOME } from '../constants';
import theme from '../theme';


const Title = () => (
  <Box style={styles.container}>
    <Box
      sx={{
        ...styles.container,
        bgcolor: theme.palette.primary.main,
        borderRadius: '10px',
        elevation: 4,
        boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.5)',
        width: '50%',
        height: 20,
        marginBottom: 5,
      }}
    >
      <h3 style={styles.logoText}>AIgnostic</h3>
    </Box>

    <Box style={styles.horizontalContainer}>
      New to AIgnostic? Read the docs to get started:
      <Button
        variant="contained"
        sx={{
          ml: '10px',
          bgcolor: theme.palette.secondary.main,
          color: '#fff',
        }}
        onClick={() => {
          window.location.href = `/api-docs`;
        }}
      >
        Getting Started
      </Button>
    </Box>
  </Box>
);

export default Title;
