import { useEffect, useState, useRef } from 'react';
import { checkBatchConfig, checkURL } from './utils';
import {
  steps,
  legislation,
  BACKEND_EVALUATE_URL,
  RESULTS_URL,
  modelTypesToMetrics,
  activeStepToInputConditions,
  WEBSOCKET_URL,
  USER_METRICS_SERVER_URL,
  AGGREGATOR_UPLOAD_URL,
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
import Dashboard from './dashboard';
import theme from './theme';
import { v4 as uuidv4 } from 'uuid';
import FileUploadComponent from './components/FileUploadComponent';
import { IS_PROD } from './env';

function Homepage() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [state, setState] = useState<HomepageState & { dashboardKey: number }>({
    modelURL: '',
    datasetURL: '',
    modelAPIKey: '',
    datasetAPIKey: '',
    isModelURLValid: true,
    isDatasetURLValid: true,
    batchSize: 50,
    numberOfBatches: 20,
    isBatchConfigValid: true,
    maxConcurrentBatches: 3,
    isMaxConcurrentBatchesValid: true,
    activeStep: 0,
    selectedItem: '',
    metricChips: [],
    legislationChips: legislation,
    metricsHelperText: '',
    selectedModelType: '',
    error: false,
    errorMessage: { header: '', text: '' },
    showDashboard: false,
    dashboardKey: 0, // Added key to force Dashboard remount
    isGeneratingReport: false,
    userMetricsUploaded: false,
    userRequirementsUploaded: false,
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

  const disconnectRef = useRef(false); // Track whether disconnect is intentional

  useEffect(() => {
    let userId = sessionStorage.getItem('userId');
    if (!userId) {
      userId = uuidv4();
      console.log('Generated new user ID:', userId);
      sessionStorage.setItem('userId', userId);
    }

    const connectWebSocket = () => {
      const newSocket = new WebSocket(WEBSOCKET_URL);
      newSocket.onopen = () => {
        console.log('WebSocket connection established');
        newSocket.send(userId.toString());
      };
      newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
      };

      newSocket.onclose = () => {
        if (!disconnectRef.current) {
          // only attempt to reconnect if disconnect was not intentional
          console.log('WebSocket connection closed, attempting to reconnect...');
          setTimeout(connectWebSocket, 1000);
        }
      };

      setSocket(newSocket);
      console.log('Connection set');
    };

    connectWebSocket();

    return () => {
      disconnectRef.current = true; // Mark as intentionally disconnected
      if (socket) {
        socket.close();
      }
    };
  }, []);

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

  const generateUniqueUserID = () => {
    return Math.random().toString(36).substring(2, 15);
  };

  const handleReset = () => {
    setStateWrapper('activeStep', 0);
  };

  const handleSubmit = async () => {
    if (!state.modelURL || !state.datasetURL) {
      console.log('Please fill in both text inputs.');
      return;
    }

    if (state.isGeneratingReport) {
      setStateWrapper('error', true);
      setStateWrapper('errorMessage', {
        header: 'Report Being Generated',
        text: 'Please wait for the current report to finish generating.',
      });
      return;
    }

    let userId = sessionStorage.getItem('userId');

    if (!userId) {
      userId = uuidv4(); // Generate a new user ID if not found
      sessionStorage.setItem('userId', userId);
    }

    setStateWrapper('isGeneratingReport', true); // Prevent multiple clicks
    setStateWrapper('dashboardKey', state.dashboardKey + 1);
    setStateWrapper('showDashboard', true);

    const user_info = {
      dataset_url: state.datasetURL,
      dataset_api_key: state.datasetAPIKey,
      model_url: state.modelURL,
      model_api_key: state.modelAPIKey,
      metrics: state.metricChips
        .filter((metricChip) => metricChip.selected)
        .map((metricChip) => metricChip.label.toLowerCase()),
      model_type: state.selectedModelType.toLowerCase(),
      user_id: userId,
      batch_size: state.batchSize,
      num_batches: state.numberOfBatches,
      max_conc_batches: state.maxConcurrentBatches,
    };

    const frontend_info = {
      user_id: userId,
      legislation: state.legislationChips
        .filter((legislationChip) => legislationChip.selected)
        .map((legislationChip) => legislationChip.label)
    }
    console.log("Data:", frontend_info)
    try {
      // Send POST request to backend server
      const postFrontend = await fetch(AGGREGATOR_UPLOAD_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(frontend_info),
    });
      console.log("Status: ", postFrontend.status)
      if (postFrontend.status !== 200) {
        const errorData = await postFrontend.json();
        console.log('Error:', errorData.detail);
        console.error(`Error: ${postFrontend.status}`, errorData.detail);
        setStateWrapper('error', true);
        setStateWrapper('errorMessage', {
          header: `Error ${postFrontend.status}`,
          text: errorData.detail,
        });
      }

      console.log('Job accepted. Waiting for results');
    } catch (error: any) {
      console.log('Legislation Error status code:', error)
      console.error('Error while posting to aggregator:', error.message);
      setStateWrapper('error', true);
      setStateWrapper('errorMessage', {
        header: 'Submission Error',
        text: error.message,
      });
    }

    try {
      // Send POST request to backend server
      const postResponse = await fetch(BACKEND_EVALUATE_URL, {
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

  function handleModelTypeChange(value: string) {
    if (value in modelTypesToMetrics) {
      setStateWrapper(
        'metricChips',
        modelTypesToMetrics[value].map((metric) => ({
          id: metric,
          value: metric,
          label: metric
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (char) => char.toUpperCase()),
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
                        variant="filled"
                        InputProps={{
                          sx: {
                            color: '#fff',
                          },
                        }}
                      />
                    );
                  })}
                  <Box mt={2} display="flex" gap={2} flexWrap="wrap">
                    <Box flex={1}>
                      <TextField
                        label="Number of Batches"
                        type="number"
                        defaultValue={state.numberOfBatches}
                        error={!state.isBatchConfigValid}
                        helperText={
                          state.numberOfBatches < 1
                            ? "Number of batches must be greater than 0"
                            : !state.isBatchConfigValid 
                              ? "Invalid batch configuration" 
                              : ""
                        }
                        onChange={(e) => setStateWrapper(
                          'numberOfBatches' as keyof typeof state,
                          e.target.value
                        )}
                        onBlur={() => {
                          const isValid = checkBatchConfig(state.batchSize, state.numberOfBatches);
                          setStateWrapper('isBatchConfigValid', isValid);
                        }}
                        style={styles.input}
                      />
                    </Box>
                    <Box flex={1}>
                      <TextField
                        label="Batch Size"
                        type="number"
                        defaultValue={state.batchSize}
                        error={!state.isBatchConfigValid}
                        helperText={
                          state.batchSize < 1
                            ? "Batch size must be greater than 0"
                            : !state.isBatchConfigValid 
                              ? "Invalid batch configuration" 
                              : ""
                        }
                        onChange={(e) => setStateWrapper(
                          'batchSize' as keyof typeof state,
                          e.target.value
                        )}
                        onBlur={() => {
                          const isValid = checkBatchConfig(state.batchSize, state.numberOfBatches);
                          setStateWrapper('isBatchConfigValid', isValid);
                        }}
                        style={styles.input}
                      />
                    </Box>
                    <Box flex={1}>
                      <TextField
                        label="Maximum Concurrent Batches"
                        type="number"
                        defaultValue={state.maxConcurrentBatches}
                        error={!state.isMaxConcurrentBatchesValid}
                        helperText={!state.isMaxConcurrentBatchesValid ? "Value must be between 1 and 30" : ""}
                        onChange={(e) => setStateWrapper(
                          'maxConcurrentBatches' as keyof typeof state,
                          e.target.value
                        )}
                        onBlur={(e) => {
                          const value = Math.min(Math.max(parseInt(e.target.value), 1), 30);
                          const isValid = value === parseInt(e.target.value);
                          setStateWrapper('maxConcurrentBatches', value);
                          setStateWrapper('isMaxConcurrentBatchesValid', isValid);
                        }}
                        style={styles.input}
                      />
                    </Box>
                  </Box>
                  {!state.isBatchConfigValid && (
                    <Box>
                      <Typography color="error">
                        Total sample size must be between 1000 and 10000, not {state.batchSize * state.numberOfBatches}. 
                      </Typography>
                      {
                        (state.batchSize < 1 || state.numberOfBatches < 1) && (
                          <Typography color="error">
                            Batch size and number of batches must be positive. 
                          </Typography>
                        )
                      }
                      
                    </Box>
                  )}
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
                          control={<Radio color="secondary" />}
                          label={modelType
                            .replace(/_/g, ' ')
                            .replace(/\b\w/g, (char) => char.toUpperCase())}
                        />
                      ))}
                    </RadioGroup>
                  </FormControl>
                </Box>
              )}
              {/* 3. SELECT METRICS */}
              {index === 2 && (
                <Box style={{ padding: '15px' }}>
                  <p style={{ color: 'red' }}>{state.metricsHelperText}</p>
                  {state.legislationChips.map((legislationChip, index) => (
                    <Chip
                      key={legislationChip.id || index}
                      label={legislationChip.label}
                      variant="filled"
                      onDelete={() => {
                        legislationChip.selected = !legislationChip.selected;
                        setStateWrapper('metricChips', [...state.metricChips]);
                      }}
                      onClick={() => {
                        legislationChip.selected = !legislationChip.selected;
                        setStateWrapper('metricChips', [...state.metricChips]);
                      }}
                      color={legislationChip.selected ? 'secondary' : 'default'}
                      style={{ margin: '5px' }}
                    />
                  ))}
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
                      color={metricChip.selected ? 'secondary' : 'default'}
                      style={{ margin: '5px' }}
                    />
                  ))}
                  {!IS_PROD && (
                    <FileUploadComponent
                      state={state}
                      setStateWrapper={setStateWrapper}
                    />
                  )}
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
                  <br /> <br />
                  <strong>Batch Configuration:</strong>
                  <br />
                  Batch Size: {state.batchSize}
                  <br />
                  Number of Batches: {state.numberOfBatches}
                  <br />
                  Max Concurrent Batches: {state.maxConcurrentBatches}
                  </Typography>
                </Box>
              )}

              <Box sx={{ mb: 2 }}>
                {index === steps.length - 1 ? (
                  <div>
                    {!state.showDashboard && (
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
                            if (!state.isGeneratingReport) {
                              handleSubmit();
                            }
                          }

                          // open dashboard page in new tab
                          // window.open(`/${AIGNOSTIC}/dashboard`, '_blank');
                        }}
                        disabled={state.isGeneratingReport}
                        sx={{
                          mt: 1,
                          mr: 1,
                          backgroundColor: theme.palette.secondary.main,
                        }}
                      >
                        {' '}
                        Generate Report
                      </Button>
                    )}
                    {state.showDashboard && (
                      // Passing the dashboardKey forces remount when it changes.
                      <Dashboard
                        key={state.dashboardKey}
                        onComplete={() => {
                          setStateWrapper('isGeneratingReport', false);
                        }}
                        socket={socket}
                        disconnectRef={disconnectRef}
                        expectedItems={state.numberOfBatches}
                      />
                    )}
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
                    style={{
                      backgroundColor: theme.palette.secondary.main,
                    }}
                  >
                    {' '}
                    Next
                  </Button>
                )}

                <Button
                  variant="contained"
                  disabled={index === 0 || state.isGeneratingReport}
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
