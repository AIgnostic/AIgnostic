import React from 'react';
import { Box, Button } from '@mui/material';
import styles from '../home.styles';


const Title = () => (
  <Box style={styles.container}>
    <Box style={styles.logoContainer}>
      <h3 style={styles.logoText}>AIgnostic Frontend</h3>
    </Box>

    <Box style={styles.horizontalContainer}>
      New to AIgnostic? Read the docs to get started:
      <Button style={styles.button}>Getting Started</Button>
    </Box>
  </Box>
);

export default Title;