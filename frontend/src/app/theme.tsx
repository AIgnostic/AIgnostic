import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
      primary: {
        main: '#29438a',
      },
      secondary: {
        main: '#56a3a6',
      },
      error: {
        main: '#d32f2f',
      },
      warning: {
        main: '#ffa000',
      },
      info: {
        main: '#0288d1',
      },
      success: {
        main: '#388e3c',
      },
      background: {
        default: '#efe6dd',
        paper: '#efe6dd',
      },
      text: {
        primary: '#333',
        secondary: '#000',
      },
    },
    typography: {
      fontFamily: 'Roboto, Arial, sans-serif', // Set global font family
      h1: {
        fontSize: '2rem',
        color: '#333', // Customize color for h1
      },
      h2: {
        fontSize: '1.5rem',
        color: '#333', // Customize color for h2
      },
      body1: {
        fontSize: '1rem',
        color: '#333', // Customize color for body1
      },
    },
  });

export default theme;