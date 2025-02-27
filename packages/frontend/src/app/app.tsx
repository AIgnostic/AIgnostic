// Uncomment this line to use CSS modules
// import styles from './app.module.css';
import { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AIGNOSTIC, HOME } from './constants';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme';
import Homepage from './home';
import APIDocs from './api_docs';
import Dashboard from './dashboard';
import { MarkdownFiles } from './types';

export function App() {

  const location = useLocation();

  // Set the tab name based on the current route
  useEffect(() => {
    switch (location.pathname) {
      case `/`:
        document.title = `Home | ${AIGNOSTIC}`;
        break;
      case `/api-docs`:
        document.title = `API Docs | ${AIGNOSTIC}`;
        break;
      default:
        document.title = `${AIGNOSTIC}`;
    }
  }, [location]);

  // Dependency injection-friendly function
  const defaultMarkdownLoader = () => {
    if (import.meta) {
      return import.meta.glob('./docs/*.md', { query: '?raw', import: 'default', eager: true }) as MarkdownFiles;
    }
    return {} as MarkdownFiles;
  };

  return (
    <div>
      <ThemeProvider theme={theme}>
        <Routes>
          <Route path={`/`} element={<Homepage />} />
          <Route path={`/api-docs`} element={<APIDocs getMarkdownFiles={defaultMarkdownLoader} />} />
        </Routes>
      </ThemeProvider>
    </div>
  );
}
export default App;
