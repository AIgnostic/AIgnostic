// Uncomment this line to use CSS modules
// import styles from './app.module.css';
import NxWelcome from './nx-welcome';
import { Route, Routes, Link } from 'react-router-dom';
import { useState } from 'react';
import Homepage from './home';
export function App() {
  return (
    <div>
      {/* <NxWelcome title="AIgnostic" /> */}
      <Homepage />
    </div>
  );
}
export default App;
