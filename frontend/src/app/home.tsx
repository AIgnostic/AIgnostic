import React, { useState } from 'react';
import checkURL from './utils';
function Homepage() {
  const [modelURL, setModelURL] = useState('');
  const [datasetURL, setDatasetURL] = useState('');

  const handleSubmit = () => {
    if (modelURL && datasetURL) {
        //Enter into SanityCheckService
      alert(`Input 1: ${modelURL}, Input 2: ${datasetURL}`);
      alert(checkURL(modelURL) && checkURL(datasetURL))
    

    } else {
      alert('Please fill in both text inputs.');
    }
  };

  return (
    <div style={styles.container}>
      {/* Logo or Welcome Message */}
      <div style={styles.logoContainer}>
        <h1 style={styles.logoText}>Welcome to AIgnostic</h1>
      </div>

      {/* Text Inputs */}
      <div style={styles.formContainer}>
        <input
          type="text"
          placeholder="Enter Model API URL"
          value={modelURL}
          onChange={(e) => setModelURL(e.target.value)}
          style={styles.input}
        />
        <input
          type="text"
          placeholder="Enter Dataset API URL"
          value={datasetURL}
          onChange={(e) => setDatasetURL(e.target.value)}
          style={styles.input}
        />

        {/* Submit Button */}
        <button onClick={handleSubmit} style={styles.button}>
          Submit
        </button>
      </div>
    </div>
  );
}

const styles : { [key: string]: React.CSSProperties} = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f5f5f5',
  },
  logoContainer: {
    marginBottom: '20px',
  },
  logoText: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#333',
  },
  formContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '300px',
  },
  input: {
    width: '100%',
    padding: '10px',
    marginBottom: '10px',
    fontSize: '16px',
    borderRadius: '4px',
    border: '1px solid #ccc',
  },
  button: {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#007BFF',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};

export default Homepage;
