import { useState } from 'react';
import { checkURL, generateReportText } from './utils';
import Dropdown from './components/dropdown';
import { steps, BACKEND_URL, modelTypesToMetrics, generalMetrics, activeStepToInputConditions } from './constants';
import Title from './components/title';
import { styles } from './home.styles';
import ErrorMessage from './components/ErrorMessage';
import {
  Box, 
  Button, 
  Chip, 
  TextField,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Typography,
  FormControl,
  RadioGroup,
  FormLabel,
  FormControlLabel,
  Radio,
} from '@mui/material';
import { HomepageState } from './types';

function Homepage() {
  const [state, setState] = useState<HomepageState>({
    modelURL: '',
    datasetURL: '',
    modelAPIKey: '',
    datasetAPIKey: '',
    isModelURLValid: true,
    isDatasetURLValid: true,
    activeStep: 0,
    selectedItem: '',
    metricChips: generalMetrics.map((metric) => ({
      id: metric,
      label: metric,
      selected: true,
    })),
    metricsHelperText: '',
    selectedModelType: '',
    error: false,
    errorMessage: { header: '', text: '' },
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
  const getErrorProps = (isValid: boolean, errorMessage: string) => ({
    error: !isValid, 
    helperText: !isValid ? errorMessage : '',
  });

  const handleNext = () => { setStateWrapper("activeStep", state.activeStep + 1) };

  const handleBack = () => { setStateWrapper("activeStep", state.activeStep - 1) };

  const handleReset = () => { setStateWrapper("activeStep", 0); };

  const handleSubmit = () => {
    if (state.modelURL && state.datasetURL) {
      const user_info = {
        "model_url": state.modelURL,
        "data_url": state.datasetURL,
        "model_api_key": state.modelAPIKey,
        "data_api_key": state.datasetAPIKey,
        "metrics": state.metricChips.filter((metricChip) => metricChip.selected)
          .map((metricChip: { label: string; selected: boolean }) => (metricChip.label).toLowerCase())
      };
  
      // Send POST request to backend server
      fetch(BACKEND_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(user_info),
      })
        .then((response) => {
          if (!response.ok) {
            console.log(`HTTP error! status: ${response.status}`);
            setStateWrapper("error", true);
            response.json().then((data) => {
              setStateWrapper("errorMessage", { header: `Error ${response.status}`, text: `${data.detail}` });
            });
  
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          const results = data["results"];
          const doc = generateReportText(results);
          doc.save('AIgnostic_Report.pdf');
        })
        .catch((error) => {
          console.error("Error during fetch:", error.message);
        });
    } else {
      console.log('Please fill in both text inputs.');
    }
  };

  // Placeholder for the dropdown items
  const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];
  const [selectedItem, setSelectedItem] = useState('');

  function handleModelTypeChange(value: string) {
    if (value in modelTypesToMetrics) {
      setStateWrapper("metricChips", modelTypesToMetrics[value].map((metric) => ({
        id: metric,
        label: metric,
        selected: true,
      })));
    }
  }

  return (
    <Box sx={[styles.container]}>

      {/* Display error message if error received from backend response */}
      {state.error && (
        <ErrorMessage
          onClose={() => setStateWrapper("error", false)}
          errorHeader={state.errorMessage.header}
          errorMessage={state.errorMessage.text}
        />
      )}

      <Title />

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

              {/* 1. ENTER MODEL AND DATASET API  URLS CONTENT */}
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
              {/* 2. SELECT MODEL TYPE */}
              {index === 1 && (
                <Box style={{ padding: '15px' }}>
                <p style={{ color: 'red' }}>{state.metricsHelperText}</p>
              
                <FormControl component="fieldset">
                  <FormLabel component="legend">Select Model Type</FormLabel>
                  <RadioGroup
                    value={state.selectedModelType}
                    onChange={(event) => {
                      handleModelTypeChange(event.target.value);
                      setStateWrapper("selectedModelType", event.target.value);
                    }}
                  >
                    {Object.keys(modelTypesToMetrics).map((modelType) => (
                      <FormControlLabel
                        key={modelType}
                        value={modelType}
                        control={<Radio color="primary" />}
                        label={modelType}
                      />
                    ))}
                  </RadioGroup>
                </FormControl>
              </Box>
              )}

                
              {/* 3. SELECT METRICS */}
              {index === 3 && (
                <Box style={{ padding: '15px' }}>
                  <p style={{ color: 'red' }}>{state.metricsHelperText}</p>
                  {state.metricChips.map((metricChip, index) => (
                    <Chip
                      key={metricChip.id || index}
                      label={metricChip.label}
                      variant="filled"
                      onDelete={() => {
                        metricChip.selected = !metricChip.selected;
                        setStateWrapper("metricChips", [...state.metricChips]);
                      }}
                      onClick={() => {
                        metricChip.selected = !metricChip.selected;
                        setStateWrapper("metricChips", [...state.metricChips]);
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
                    label="Select other metrics"
                    value={selectedItem}
                    onChange={(value: string) => setSelectedItem(value)}
                  />
                </Box>
              )}
              {/* 4. SUMMARY AND GENERATE REPORT */}
              {index === steps.length - 1 && (
                  <Box style={{ padding: '15px' }}>
                    <h3>Summary</h3>
                    <Typography variant="body1">
                      <strong>Model URL:</strong>{' '}
                      {state.modelURL || 'You have not entered a model URL'}
                      <br /> <br />
                      <strong>Dataset URL:</strong>{' '}
                      {state.datasetURL || 'You have not entered a dataset URL'}
                      <br /> <br />
                      <strong>Metrics:</strong>{' '}
                      {state.metricChips.filter((metricChip) => metricChip.selected).length === 0
                      ? 'You have not selected any metrics'
                      : state.metricChips
                        .filter((metricChip) => metricChip.selected)
                        .map((metricChip) => metricChip.label)
                        .join(', ')}
                    </Typography>
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
                      // if not, jump to step 3
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
                      // TODO: For each index in activeStepToInputConditions check it holds
                      let raised = false
                      for (const [step, condition] of Object.entries(activeStepToInputConditions)) {
                        if (parseInt(step) === index && !condition.pred(state)) {
                          alert(condition.error_msg);
                          raised = true
                        }
                      }
                      if (!raised) {
                        handleNext();
                      }
                    }}
                    disabled = {
                      (index === 0 && !(state.isModelURLValid && state.isDatasetURLValid)) ||
                      (index === 1 && state.selectedModelType === '')
                    }
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
                  sx={[{ mt: 1, mr: 1}, styles.secondaryButton]}
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