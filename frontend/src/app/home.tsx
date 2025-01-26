import React, { useState } from 'react';
import checkURL  from './utils';
// import handleSubmit from './utils';
// import handleNext from './utils';
// import handleBack from './utils';
// import handleReset from './utils';
import styles from './home.styles';
import { BACKEND_URL } from './constants';
import { Box, Button, Chip, TextField } from '@mui/material';
import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Typography,
} from '@mui/material';
import Dropdown from './dropdown';
import { steps, metrics } from './constants';


function Homepage() {

  const [state, setState] = useState({
    modelURL: '',
    datasetURL: '',
    modelAPIKey: '',
    datasetAPIKey: '',
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

  const getValues = {
    modelURL: {
      label: "Model API URL",
      value: state.modelURL,
      isValid: state.isModelURLValid,
      validKey: "isModelURLValid",
    },
    datasetURL: {
      label: "Dataset API URL",
      value: state.datasetURL,
      isValid: state.isDatasetURLValid,
      validKey: "isDatasetURLValid",
    },
    modelAPIKey: {
      label: "Model API Key",
      value: state.modelAPIKey,
      isValid: undefined,
      validKey: undefined,
    },
    datasetAPIKey: {
      label: "Dataset API Key",
      value: state.datasetAPIKey,
      isValid: undefined,
      validKey: undefined,
    },
  };
  

  const setStateWrapper = <K extends keyof typeof state>(key: K, value: typeof state[K]) => {
    setState((prevState) => ({
      ...prevState,
      [key]: value,
    }));
  };

  const handleNext = () => { setStateWrapper("activeStep", state.activeStep + 1) };

  const handleBack = () => { setStateWrapper("activeStep", state.activeStep - 1) };

  const handleReset = () => { setStateWrapper("activeStep", 0); };

  const handleSubmit = () => {
    if (state.modelURL && state.datasetURL) {
      const user_info = {
        "modelURL": state.modelURL,
        "datasetURL": state.datasetURL,
        "modelAPIKey": state.modelAPIKey,
        "datasetAPIKey": state.datasetAPIKey,
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
          console.log("FRONTEND", data["results"]);
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


          console.log("Response from backend:", data);
        })
        .catch((error) => {
          console.error("Error during fetch:", error.message);
        });
    } else {
      console.log('Please fill in both text inputs.');
    }
  };

  // Utility function for error handling
  const getErrorProps = (isValid: boolean, errorMessage: string) => ({
    error: !isValid, // If invalid, set the error state to true
    helperText: !isValid ? errorMessage : '', // Provide error message if invalid
  });

  // Placeholder for the dropdown items
  const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];
  const [selectedItem, setSelectedItem] = useState('');

  return (
    <Box sx={[styles.container]}>
      <Box style={styles.container}>
        <Box style={styles.logoContainer}>
          <h3 style={styles.logoText}>AIgnostic Frontend</h3>
        </Box>

        <Box style={styles.horizontalContainer}>
          New to AIgnostic? Read the docs to get started:
          <Button style={styles.button}>Getting Started</Button>
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
-
              {index === 0 && (
               <Box style={{ padding: '15px' }}>
               {(['modelURL', 'datasetURL', 'modelAPIKey', 'datasetAPIKey'] as (keyof typeof getValues)[])
               .map((key) => {
                 const field = getValues[key]; 
                 const handleOnBlur = field.validKey && field.isValid !== undefined
                   ? () => {
                       setStateWrapper(
                         field.validKey as keyof typeof state,
                         checkURL(field.value)
                       );
                     }
                   : undefined; // Don't do anything for fields that don't need validation onBlur
                 
                 const errorProps = field.isValid !== undefined
                   ? getErrorProps(field.isValid, 'Invalid URL') // Only set errorProps if the field has isValid
                   : undefined;
                 
                return ( 
                <TextField
                  style={styles.input}
                  key={key}
                  label={field.label}
                  value={field.value}
                  onChange={(e) => {
                  setStateWrapper(key, e.target.value);
                  }}
                onBlur={handleOnBlur}
                helperText={field.isValid !== undefined
                  ? errorProps?.helperText
                  : ''}
                error={field.isValid !== undefined
                  ? errorProps?.error
                  : false}
                />
              );
               })}
             </Box>
                     
              )}

              {index === 2 && (
                <Box style={{ padding: '15px' }}>
                  <p style={{ color: 'red' }}>{state.metricsHelperText}</p>
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
                    style={{
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
                      Model API Key:{' '}
                      {state.modelAPIKey ? state.modelAPIKey : 'You have not entered a model API Key'}
                      <br /> <br />
                      Dataset API Key:{' '}
                      {state.datasetAPIKey
                        ? state.datasetAPIKey
                        : 'You have not entered a dataset API Key'}
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
                      }
                    }}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {' '}
                    Next
                  </Button>
                )}

                <Button
                  disabled={index === 0}
                  onClick={handleBack}
                  sx={{ mt: 1, mr: 1 }}
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
}

export default Homepage;
