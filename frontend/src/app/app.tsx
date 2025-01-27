// Uncomment this line to use CSS modules
// import styles from './app.module.css';
import React, { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Homepage from './home';
import APIDocs from './api_docs';
import {AIGNOSTIC, HOME} from './constants';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme';

export function App() {

  const location = useLocation();

  // Set the tab name based on the current route
  useEffect(() => {
    switch (location.pathname) {
      case `${HOME}/`:
        document.title = `Home | ${AIGNOSTIC}`;
        break;
      case `${HOME}/api-docs`:
        document.title = `API Docs | ${AIGNOSTIC}`;
        break;
      default:
        document.title = `${AIGNOSTIC}`;
    }
  }, [location]);

  
  return (
    <div>
      <ThemeProvider theme={theme}>
        <Routes>
          <Route path={`${HOME}/`} element={<Homepage />} />
          <Route path={`${HOME}/api-docs`} element={<APIDocs />} />
        </Routes>
      </ThemeProvider>
    </div>
  );
}
export default App;
