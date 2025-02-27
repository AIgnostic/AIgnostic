import React from 'react';
import { Box, Button } from '@mui/material';
import { styles } from '../home.styles';
import { HOME } from '../constants';
import theme from '../theme';
import { pdf } from '@react-pdf/renderer';
import ReportRenderer from './ReportRenderer';


// const mockReport = {
//   "info" : {
//     calls_to_model: 10,
//     date: "2021-10-10",
//   },

//   "properties": [
//     {
//     "property": "property1",
//     "computed_metrics": [
//       {
//         "metric": "metric1",
//         "value": "0.5",
//         "ideal_value": "0.8",
//         "range": ["0", "1"],
//       },
//       {
//         "metric": "metric2",
//         "value": "0.7",
//         "ideal_value": "0.3",
//         "range": ["-1", "1"],
//       }],
//     "legislation_extracts": [
//       {
//         "article_number": 1,
//         "article_title": "title1",
//         "description": "description1",
//         "suitable_recitals": ["recital1", "recital2"],
//       },
//       {
//         "article_number": 2,
//         "article_title": "title2",
//         "description": "description2",
//         "suitable_recitals": ["recital3", "recital4"],
//       }],
//     "llm_insights": [
//       "insight1",
//       "insight2",
//     ],
//     },
//   ]
// } 


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
      {/* <Button
        variant="contained"
        sx={{
          ml: '10px',
          bgcolor: theme.palette.secondary.main,
          color: '#fff',
        }}
        onClick={async () => {
          const blob = await pdf(<ReportRenderer report={mockReport} />).toBlob();
          const url = URL.createObjectURL(blob);
          window.open(url, '_blank');
        }}
      >
        Generate Report
      </Button> */}
        
    </Box>
  </Box>
);

export default Title;
