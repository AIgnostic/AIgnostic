import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button } from '@mui/material';
import { ContentCopy } from '@mui/icons-material';
import styles from '../styles';

interface CodeBoxProps {
    language: string;
    codeSnippet: string;
}

const CodeBox: React.FC<CodeBoxProps> = ({ language, codeSnippet }) => {
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
        <div style={{ position: 'relative', width: "60%" }}>

            {/* Code Block with Syntax Highlighting */}
            <div style={{ position: 'relative' }}>
                <SyntaxHighlighter language={language} style={solarizedlight}>
                    {codeSnippet}
                </SyntaxHighlighter>

                {/* Copy Button */}
                <Button
                    onClick={handleCopy}
                    startIcon={<ContentCopy />}
                    style={styles.button}
                    sx={{ position: 'absolute', top: 0, right: 0 }}
                >
                    {copySuccess ? 'Copied!' : 'Copy'}
                </Button>
            </div>
        </div>
    );
};

export default CodeBox;
