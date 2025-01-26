import React, { useState } from 'react';
import checkURL from './utils';
import { Box, Button, Chip, TextField } from '@mui/material';
import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Typography,
} from '@mui/material';
import Dropdown from './dropdown';
import { AIGNOSTIC, HOME } from './constants';
import styles from './styles';
import theme from './theme';

const steps = [
  {
    label: 'Enter model and dataset API URLs',
    description: `Enter the URLs for your model and dataset APIs to get started.
                  For more information about creating the APIs, see the documentation - click 'Getting Started'.`,
  },
  {
    label: 'Select Legislation',
    description: `Select the legislations that you want to comply with.`,
  },
  {
    label: 'Select Metrics',
    description: `Select the metrics you want to analyze your model with. 
       These will be used to quantify your compliance score with your selected metrics.`,
  },
  {
    label: 'Summary and Generate Report',
    description: `Check that you are happy with your selections and generate your compliance report.
                  Report generation may take some time.`,
  },
];

const metrics = ['Accuracy', 'Precision', 'Recall'];
const BACKEND_URL = 'http://localhost:8000/evaluate';

function Homepage() {
  const [state, setState] = useState({
    modelURL: '',
    datasetURL: '',
    isModelURLValid: true,
    isDatasetURLValid: true,
    activeStep: 0,
    selectedItem: '',
    metricChips: metrics.map((metric) => ({
      label: metric,
      selected: true,
    })),
    metricsHelperText: '',
  });

  const setStateWrapper = <K extends keyof typeof state>(key: K, value: typeof state[K]) => {
    setState((prevState) => ({
      ...prevState,
      [key]: value,
    }));
  };

  const handleNext = () => {setStateWrapper("activeStep", state.activeStep + 1)};

  const handleBack = () => {setStateWrapper("activeStep", state.activeStep - 1)};

  const handleReset = () => {setStateWrapper("activeStep", 0);};

  const handleSubmit = () => {
    if (state.modelURL && state.datasetURL) {
      const user_info = {
        "modelURL": state.modelURL, 
        "datasetURL": state.datasetURL,
        "metrics": state.metricChips.filter((metricChip) => metricChip.selected)
                                    .map((metricChip: any) => (metricChip.label).toLowerCase())
      };

      // send POST request to backend server
      fetch(BACKEND_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(user_info),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          const results = data["results"]
          // Create the text content for the file
          const textContent = "AIgnostic Report" + "\n" +
                              "===================" + "\n" +
                              `Model API URL: ${user_info.modelURL}` + "\n" +
                              `Dataset API URL: ${user_info.datasetURL}` + "\n" + "\n" +

                              "Metrics Results:" + "\n" +
                              Object.entries(results).map(([metric, value]) => {
                                return `  - ${metric}: ${value}`;
                              }).join('\n') + "\n";                  
    
          // Create a Blob and download it as a text file
          const blob = new Blob([textContent], { type: "text/plain" });
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = "AIgnostic_Report.txt";
          link.click();
        })
        .catch((error) => {
          console.error("Error during fetch:", error.message);
        });




    } else { 
      // ERROR
    }
  };

  // Placeholder for the dropdown items
  const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];
  const [selectedItem, setSelectedItem] = useState('');

  return (
    <Box sx={[styles.container]}>
      <Box style={styles.container}>
        <Box style={styles.container}>
          <h3 style={styles.logoText}>{AIGNOSTIC}</h3>
        </Box>

        <Box style={styles.horizontalContainer}>
          New to {AIGNOSTIC}? Read the docs to get started:
          <Button 
            style={styles.button}
            variant="contained"
            onClick={() => {
              window.open(`${HOME}/api-docs`, '_blank', 'noopener,noreferrer');
            }}
          >Getting Started</Button>
        </Box>
      </Box>

      <Stepper
        activeStep={state.activeStep}
        style={{ width: '80%' }}
        orientation="vertical"
        >
        {steps.map((step, index) => (
          <Step key={step.label}>
            <StepLabel>
              <h1>{step.label}</h1>
            </StepLabel>
            <StepContent>
              <Typography>{step.description}</Typography>

              {index === 0 && (
                <Box style = {{
                  padding: '15px',
                }}>
                  <TextField
                    type="text"
                    label = "Model API URL"
                    value={state.modelURL}
                    onChange={(e) => {
                      setState((prevState) => ({
                        ...prevState, 
                        modelURL: e.target.value, 
                      }));
                    }} 
                    onBlur={() => {
                      setStateWrapper("isModelURLValid", checkURL(state.modelURL))
                    }} 
                    style={styles.input}
                    error={!state.isModelURLValid}
                    helperText={
                      !state.isModelURLValid
                        ? 'Invalid URL format - please enter a valid URL'
                        : ''
                    }
                 
                  />
                  <TextField
                    type="text"
                    label = "Dataset API URL"
                    value={state.datasetURL}
                    onChange={(e) => {
                      setStateWrapper("datasetURL", e.target.value)
                    }} 
                    onBlur={() => {
                      setStateWrapper("isDatasetURLValid", checkURL(state.datasetURL))
                    }}                    
                    style={styles.input}
                    error={!state.isDatasetURLValid}
                    helperText={
                      !state.isDatasetURLValid
                        ? 'Invalid URL format - please enter a valid URL'
                        : ''
                    }
                  />
                </Box>
              )}

              {index === 2 && (
                <Box style={{ padding: '15px' }}>
                  <p >{state.metricsHelperText}</p>
                  {state.metricChips.map((metricChip) => (
                    <Chip
                      label={metricChip.label}
                      variant="filled"
                      onDelete={() => {
                        metricChip.selected = !metricChip.selected;
                        setStateWrapper("metricChips", [...state.metricChips])
                      }}
                      onClick={() => {
                        metricChip.selected = !metricChip.selected;
                        setStateWrapper("metricChips", [...state.metricChips])
                      }}
                      color={metricChip.selected ? 'primary' : 'default'}
                      style={{ margin: '5px' }}
                    />
                  ))}

                  <Dropdown
                    style ={{
                      marginTop: '20px',
                    }}
                    items={items}
                    label="Select target label(s)"
                    value={selectedItem}
                    onChange={(value: string) => setSelectedItem(value)}
                  />
                </Box>
              )}

              {index === steps.length - 1 && (
                <Box style={{ padding: '15px' }}>
                  <h3>Summary</h3>
                  <p>
                    Model URL:{' '}
                    {state.modelURL ? state.modelURL : 'You have not entered a model URL'}
                    <br /> <br />
                    Dataset URL:{' '}
                    {state.datasetURL
                      ? state.datasetURL
                      : 'You have not entered a dataset URL'}
                    <br /> <br />
                    Metrics:{' '}
                    {state.metricChips.filter((metricChip) => metricChip.selected)
                      .length === 0
                      ? 'You have not selected any metrics'
                      : state.metricChips
                          .filter((metricChip) => metricChip.selected)
                          .map((metricChip) => metricChip.label)
                          .join(', ')}
                  </p>
                </Box>
              )}

              <Box sx={{ mb: 2 }}>
                {index === steps.length - 1 ? (
                  <Button
                    variant="contained"
                    onClick={() => {
                      // check that APIs are present and valid
                      // if not, jump to step 0
                      if (!state.modelURL || !state.datasetURL) {
                        if (!state.modelURL) {
                          setStateWrapper("isModelURLValid", false)
                        }
                        if (!state.datasetURL) {
                          setStateWrapper("isDatasetURLValid", false)
                        }
                        setStateWrapper("activeStep", 0)
                      }

                      // check that at least one metric is selected
                      // if not, jump to step 2
                      else if (
                        state.metricChips.filter((metricChip) => metricChip.selected)
                          .length === 0
                      ) {
                        setStateWrapper("metricsHelperText", 'Please select at least one metric')
                        setStateWrapper('activeStep', 2)
                      }
                      // if all checks pass, generate report
                      else {
                        handleSubmit();
                      }
                    }}
                    style={styles.button}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {' '}
                    Generate Report
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    onClick={() => {
                      if (index === 0 && !(state.isModelURLValid && state.isDatasetURLValid)) {
                        alert("One or both URLs are invalid. Please provide valid URLs.");
                        handleReset(); // Optionally reset if invalid
                      } else {
                        handleNext();
                      }}}
                    style={styles.button}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {' '}
                    Next
                  </Button>
                )}

                <Button
                  variant="contained"
                  disabled={index === 0}
                  onClick={handleBack}
                  style={styles.button}
                  sx={{ mt: 1, mr: 1, background: theme.palette.background.paper, color: "#333" }}
                >
                  Back
                </Button>
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
};

export default Homepage;
