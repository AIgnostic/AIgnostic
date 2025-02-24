import { createTheme } from '@mui/material/styles';

//rgb(23, 28, 43)
//rgb(32, 39, 59)
const theme = createTheme({
  palette: {
    primary: {
      main: 'rgb(32, 39, 59)',
    },
    secondary: {
      main: '#29648A', // Teal-Blue
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
      default: 'rgb(23, 28, 43)', // Dark Blue-Purple
      paper: '#464866', // Grayish Blue
    },
    text: {
      primary: '#FFFFFF', // White text on dark backgrounds
      secondary: '#AAABB8', // Lighter text variant
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h1: {
      fontSize: '2rem',
      color: '#FFFFFF',
    },
    h2: {
      fontSize: '1.5rem',
      color: '#FFFFFF',
    },
    body1: {
      fontSize: '1rem',
      color: '#AAABB8',
    },
  },
});

export default theme;
