// To add new API documentation, create a new markdown file in the docs folder
// the rest is handled automatically
// if some components in the md are not displaying correctly
// they may have not been added to the rendering
// so add them to the components object in the ReactMarkdown component
// e.g. where p and code are added in the code below

import React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Typography from '@mui/material/Typography';
import ReactMarkdown from 'react-markdown';
import CodeBox from './components/CodeBox'; // Import your CodeBox component
import { styles } from './home.styles';
import { Box } from '@mui/material';
import { AIGNOSTIC } from './constants';
import { MarkdownFiles } from './types';
import theme from './theme';

type APIDocsProps = {
  getMarkdownFiles: () => MarkdownFiles; // Injectable function to load markdown files
};

const APIDocs: React.FC<APIDocsProps> = ({ getMarkdownFiles }) => {
  // Split the markdown into title (h1) and content
  const splitMarkdown = (markdown: string) => {
    // Find the first h1 to use as the title
    const h1Match = markdown.match(/^# (.*?)\n/);
    const title = h1Match ? h1Match[1] : 'No title found';

    // Remove the title from the markdown content for the body
    const body = markdown.replace(/^# (.*?)\n/, '');

    return { title, body };
  };

  const markdownFiles = getMarkdownFiles();
  const mds = Object.values(markdownFiles).map(splitMarkdown);

  return (
    <div style={styles.container}>
      <Box
        sx={{
          ...styles.container,
          bgcolor: theme.palette.primary.main,
          borderRadius: '10px',
          elevation: 4,
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.5)',
          width: '80%',
          height: 20,
          marginBottom: 5,
        }}
      >
        <h3 style={styles.logoText}>{AIGNOSTIC} | API Documentation</h3>
      </Box>

      {mds.map((md, index) => (
        <Accordion key={index} sx={styles.accordion}>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls={`panel${index}-content`}
            id={`panel${index}-header`}
          >
            <h1 style={{ fontSize: '20px' }}>{md.title}</h1>
          </AccordionSummary>
          <AccordionDetails
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <Box style={{ width: '80%', overflowWrap: 'anywhere' }}>
              <ReactMarkdown
                children={md.body}
                components={{
                  p: ({
                    node,
                    inline,
                    className,
                    children,
                  }: {
                    node?: unknown;
                    inline?: boolean;
                    className?: string;
                    children?: React.ReactNode;
                  }) => <Typography variant="body1">{children}</Typography>, // Map p to Typography component

                  code: ({
                    node,
                    inline,
                    className,
                    children,
                  }: {
                    node?: unknown;
                    inline?: boolean;
                    className?: string;
                    children?: React.ReactNode;
                  }) => (
                    <CodeBox language="python" codeSnippet={String(children)} />
                  ), // Map code to CodeBox component
                }}
              />
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </div>
  );
};

export default APIDocs;
