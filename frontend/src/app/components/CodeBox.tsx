import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button, Paper, Typography } from '@mui/material';
import { ContentCopy } from '@mui/icons-material';
import styles from '../styles';
import theme from '../theme';

interface CodeBoxProps {
  language: string;
  codeSnippet: string;
}

const CodeBox: React.FC<CodeBoxProps> = ({ language, codeSnippet }) => {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeSnippet);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <Paper elevation={3} style={{ width: '80%', margin: '20px auto', borderRadius: '10px' }}>
        {/* Header Bar */}
      <div style={styles.codeBoxTopBar}>
        <Typography variant="subtitle2" color='#ddd'>{language.toUpperCase()}</Typography>
        <Button
            onClick={handleCopy}
            startIcon={<ContentCopy />}
            size="small"
            style={styles.secondaryButton}
        >
            {copySuccess ? 'Copied!' : 'Copy'}
        </Button>
      </div>

      <SyntaxHighlighter 
        language={language} 
        style={solarizedlight}
        customStyle={{ margin: 0, borderRadius: '0 0 10px 10px' }}
      >
          {codeSnippet}
      </SyntaxHighlighter>
    </Paper>
  );
};

export default CodeBox;
