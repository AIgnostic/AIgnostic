import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button } from '@mui/material';
import { ContentCopy } from '@mui/icons-material';

const APIDocs: React.FC = () => {
  const codeSnippet = `
@app.post("/predict")
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.ndarray = model.predict(dataset.rows)
    rows: list[list] = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return DataSet(column_names=dataset.column_names, rows=rows)
  `;

  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeSnippet); // Copy the code to clipboard
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000); // Reset the success message after 2 seconds
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <h1>API Documentation</h1>

      {/* Code Block with Syntax Highlighting */}
      <div style={{ position: 'relative' }}>
        <SyntaxHighlighter language="python" style={solarizedlight}>
          {codeSnippet}
        </SyntaxHighlighter>

        {/* Copy Button */}
        <Button
          onClick={handleCopy}
          startIcon={<ContentCopy />}
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            padding: '5px 10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer',
          }}
        >
          {copySuccess ? 'Copied!' : 'Copy'}
        </Button>
      </div>
    </div>
  );
};

export default APIDocs;
