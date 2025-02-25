import React from 'react';
import { Box, Button } from '@mui/material';
import { styles } from '../home.styles';
import { HOME } from '../constants';
import theme from '../theme';
import { pdf } from '@react-pdf/renderer';
import ReportRenderer from './ReportRenderer';

// const testReport = {
//   info: {
//     'calls_to_model': 100,
//     'timestamp': '2021-10-01 12:00:00',
//   },
//   properties: [
//     {
//       property: 'Property 1',
//       computed_metrics: [
//         { metric: 'Metric 1', value: '0.8' },
//         { metric: 'Metric 2', value: '0.6' },
//       ],
//       legislation_extracts: [
//         {
//           article_number: 1,
//           article_title: 'Article 1',
//           description: `
//           Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur tincidunt, purus et volutpat laoreet, augue massa convallis dolor, aliquam aliquet nunc libero ac orci. Praesent vitae nibh vel sem efficitur faucibus. Sed quis leo vel lectus consequat tempus. Aliquam ultricies tristique orci, a scelerisque velit dapibus et. Duis in posuere mauris. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Duis sed turpis vel augue pretium venenatis a sit amet est. Donec auctor scelerisque commodo.

// Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu mauris id dolor facilisis venenatis. Aliquam mattis bibendum nulla vel maximus. Nunc sit amet metus ultricies odio semper placerat eu vel ex. Sed congue molestie nisi et bibendum. Mauris tincidunt diam vel euismod aliquet. Mauris sodales quam eget tellus pharetra, in aliquam erat blandit. Ut dolor dui, tristique ac fermentum vel, ullamcorper id lacus. Suspendisse potenti. Integer at orci placerat, consectetur nibh et, condimentum nisi. Maecenas sit amet efficitur libero. Suspendisse vestibulum eros vel ex condimentum pharetra. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
// `,
//           suitable_recitals: ['Recital 1', 'Recital 2'],
//         },
//       ],
//       llm_insights: ['Insight 1', 'Insight 2'],
//     },
//     {
//       property: 'Property 2',
//       computed_metrics: [
//         { metric: 'Metric 3', value: '0.5' },
//         { metric: 'Metric 4', value: '0.3' },
//       ],
//       legislation_extracts: [
//         {
//           article_number: 2,
//           article_title: 'Article 2',
//           description: `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur tincidunt, purus et volutpat laoreet, augue massa convallis dolor, aliquam aliquet nunc libero ac orci. Praesent vitae nibh vel sem efficitur faucibus. Sed quis leo vel lectus consequat tempus. Aliquam ultricies tristique orci, a scelerisque velit dapibus et. Duis in posuere mauris. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Duis sed turpis vel augue pretium venenatis a sit amet est. Donec auctor scelerisque commodo.

// Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu mauris id dolor facilisis venenatis. Aliquam mattis bibendum nulla vel maximus. Nunc sit amet metus ultricies odio semper placerat eu vel ex. Sed congue molestie nisi et bibendum. Mauris tincidunt diam vel euismod aliquet. Mauris sodales quam eget tellus pharetra, in aliquam erat blandit. Ut dolor dui, tristique ac fermentum vel, ullamcorper id lacus. Suspendisse potenti. Integer at orci placerat, consectetur nibh et, condimentum nisi. Maecenas sit amet efficitur libero. Suspendisse vestibulum eros vel ex condimentum pharetra. Lorem ipsum dolor sit amet, consectetur adipiscing elit.`,
//           suitable_recitals: ['Recital 3', 'Recital 4'],
//         },
//       ],
//       llm_insights: ['Insight 3', 'Insight 4'],
//     },
//   ],
// };

const Title = () => (
  <Box style={styles.container}>
    <Box
      sx={{
        ...styles.container,
        bgcolor: theme.palette.primary.main,
        borderRadius: '10px',
        elevation: 4,
        boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.5)',
        width: '50%',
        height: 20,
        marginBottom: 5,
      }}
    >
      <h3 style={styles.logoText}>AIgnostic</h3>
    </Box>

    <Box style={styles.horizontalContainer}>
      New to AIgnostic? Read the docs to get started:
      <Button
        variant="contained"
        sx={{
          ml: '10px',
          bgcolor: theme.palette.secondary.main,
          color: '#fff',
        }}
        onClick={() => {
          window.location.href = `${HOME}/api-docs`;
        }}
      >
        Getting Started
      </Button>

      {/* Temporary button for viewing report renderer output
      <Button
        variant="contained"
        sx={{
          ml: '10px',
          bgcolor: theme.palette.secondary.main,
          color: '#fff',
        }}
        onClick={async () => {
          window.open(URL.createObjectURL(await pdf(<ReportRenderer report={testReport} />).toBlob()), '_blank');

        }}
      >
        View Report
      </Button> */}
    </Box>
  </Box>
);

export default Title;
