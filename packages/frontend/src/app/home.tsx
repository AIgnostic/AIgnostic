import { useState } from 'react';
import { checkURL, generateReportText } from './utils';
import {
  steps,
  BACKEND_URL,
  RESULTS_URL,
  modelTypesToMetrics,
  generalMetrics,
  activeStepToInputConditions,
} from './constants';
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
import { AIGNOSTIC } from './constants';
import Dashboard from './dashboard';

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
    showDashboard: false,
  });

  const getValues = {
    modelURL: {
      label: 'Model API URL',
      value: state.modelURL,
      isValid: state.isModelURLValid,
      validKey: 'isModelURLValid',
    },
    datasetURL: {
      label: 'Dataset API URL',
      value: state.datasetURL,
      isValid: state.isDatasetURLValid,
      validKey: 'isDatasetURLValid',
    },
    modelAPIKey: {
      label: 'Model API Key',
      value: state.modelAPIKey,
      isValid: undefined,
      validKey: undefined,
    },
    datasetAPIKey: {
      label: 'Dataset API Key',
      value: state.datasetAPIKey,
      isValid: undefined,
      validKey: undefined,
    },
  };

  const setStateWrapper = <K extends keyof typeof state>(
    key: K,
    value: (typeof state)[K]
  ) => {
    setState((prevState) => ({
      ...prevState,
      [key]: value,
    }));
  };
  const getErrorProps = (isValid: boolean, errorMessage: string) => ({
    error: !isValid,
    helperText: !isValid ? errorMessage : '',
  });

  const handleNext = () => {
    setStateWrapper('activeStep', state.activeStep + 1);
  };

  const handleBack = () => {
    setStateWrapper('activeStep', state.activeStep - 1);
    if (state.activeStep === 4) {
      setStateWrapper('showDashboard', false);
    }
  };

  const handleReset = () => {
    setStateWrapper('activeStep', 0);
  };

  const handleSubmit = async () => {
    if (!state.modelURL || !state.datasetURL) {
      console.log('Please fill in both text inputs.');
      return;
    }

    setStateWrapper('showDashboard', true);

    const user_info = {
      dataset_url: state.datasetURL,
      dataset_api_key: state.datasetAPIKey,
      model_url: state.modelURL,
      model_api_key: state.modelAPIKey,
      metrics: state.metricChips
        .filter((metricChip) => metricChip.selected)
        .map((metricChip) => metricChip.label.toLowerCase()),
    };

    try {
      // Send POST request to backend server
      const postResponse = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user_info),
      });

      if (postResponse.status !== 202) {
        const errorData = await postResponse.json();
        console.error(`Error: ${postResponse.status}`, errorData.detail);
        setStateWrapper('error', true);
        setStateWrapper('errorMessage', {
          header: `Error ${postResponse.status}`,
          text: errorData.detail,
        });
        return;
      }

      console.log('Job accepted. Waiting for results');

    } catch (error: any) {
      console.error('Error while posting to backend:', error.message);
      setStateWrapper('error', true);
      setStateWrapper('errorMessage', {
        header: 'Submission Error',
        text: error.message,
      });
    }
  };

  // Placeholder for the dropdown items
  const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];
  const [selectedItem, setSelectedItem] = useState('');

  function handleModelTypeChange(value: string) {
    if (value in modelTypesToMetrics) {
      setStateWrapper(
        'metricChips',
        modelTypesToMetrics[value].map((metric) => ({
          id: metric,
          label: metric,
          selected: true,
        }))
      );
    }
  }

  return (
    <Box sx={[styles.container]}>
      {/* Display error message if error received from backend response */}
      {state.error && (
        <ErrorMessage
          onClose={() => setStateWrapper('error', false)}
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
                  {(
                    [
                      'modelURL',
                      'datasetURL',
                      'modelAPIKey',
                      'datasetAPIKey',
                    ] as (keyof typeof getValues)[]
                  ).map((key) => {
                    const field = getValues[key];
                    const handleOnBlur =
                      field.validKey && field.isValid !== undefined
                        ? () => {
                          setStateWrapper(
                            field.validKey as keyof typeof state,
                            checkURL(field.value)
                          );
                        }
                        : undefined; // Don't do anything for fields that don't need validation onBlur

                    const errorProps =
                      field.isValid !== undefined
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
                        helperText={
                          field.isValid !== undefined
                            ? errorProps?.helperText
                            : ''
                        }
                        error={
                          field.isValid !== undefined
                            ? errorProps?.error
                            : false
                        }
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
                        setStateWrapper(
                          'metricChips',
                          modelTypesToMetrics[event.target.value].map(
                            (metric) => ({
                              id: metric,
                              label: metric,
                              selected: true,
                            })
                          )
                        );
                        setStateWrapper(
                          'selectedModelType',
                          event.target.value
                        );
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
                        setStateWrapper('metricChips', [...state.metricChips]);
                      }}
                      onClick={() => {
                        metricChip.selected = !metricChip.selected;
                        setStateWrapper('metricChips', [...state.metricChips]);
                      }}
                      color={metricChip.selected ? 'primary' : 'default'}
                      style={{ margin: '5px' }}
                    />
                  ))}
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
                    {state.metricChips.filter(
                      (metricChip) => metricChip.selected
                    ).length === 0
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
                  <div>
                    <Button
                      variant="contained"
                      onClick={() => {
                        // check that APIs are present and valid
                        // if not, jump to step 0
                        if (!state.modelURL || !state.datasetURL) {
                          if (!state.modelURL) {
                            setStateWrapper('isModelURLValid', false);
                          }
                          if (!state.datasetURL) {
                            setStateWrapper('isDatasetURLValid', false);
                          }
                          setStateWrapper('activeStep', 0);
                        }

                        // check that at least one metric is selected
                        // if not, jump to step 3
                        else if (
                          state.metricChips.filter(
                            (metricChip) => metricChip.selected
                          ).length === 0
                        ) {
                          setStateWrapper(
                            'metricsHelperText',
                            'Please select at least one metric'
                          );
                          setStateWrapper('activeStep', 2);
                        }
                        // if all checks pass, generate report
                        else {
                          handleSubmit();
                        }

                        // open dashboard page in new tab
                        // window.open(`/${AIGNOSTIC}/dashboard`, '_blank');
                      }}
                      sx={{ mt: 1, mr: 1 }}
                    >
                      {' '}
                      Generate Report
                    </Button>
                    {state.showDashboard && <Dashboard />}
                  </div>
                ) : (
                  <Button
                    variant="contained"
                    onClick={() => {
                      // TODO: For each index in activeStepToInputConditions check it holds
                      let raised = false;
                      for (const [step, condition] of Object.entries(
                        activeStepToInputConditions
                      )) {
                        if (
                          parseInt(step) === index &&
                          !condition.pred(state)
                        ) {
                          alert(condition.error_msg);
                          raised = true;
                        }
                      }
                      if (!raised) {
                        handleNext();
                      }
                    }}
                    disabled={
                      (index === 0 &&
                        (!(state.isModelURLValid && state.isDatasetURLValid) ||
                          state.modelURL === '' ||
                          state.datasetURL === '')) ||
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
                  sx={[{ mt: 1, mr: 1 }, styles.secondaryButton]}
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
