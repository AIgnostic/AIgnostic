import React from 'react';
import { Box, Button } from '@mui/material';
import { styles } from '../home.styles';
import { HOME } from '../constants';


const Title = () => (
  <Box style={styles.container}>
    <Box style={styles.container}>
      <h3 style={styles.logoText}>AIgnostic Frontend</h3>
    </Box>

    <Box style={styles.horizontalContainer}>
      New to AIgnostic? Read the docs to get started:
      <Button 
        variant='contained' 
        sx={{ml:"10px"}}
        onClick={() => {
          window.location.href = `${HOME}/api-docs`;
        }}
        >Getting Started</Button>
    </Box>
  </Box>
);

export default Title;