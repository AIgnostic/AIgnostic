import { useEffect, useState, useRef } from 'react';
import {
  checkBatchConfig,
  fetchMetricInfo,
  fetchLegislationInfo,
} from './utils';
import {
  steps,
  BACKEND_EVALUATE_URL,
  activeStepToInputConditions,
  WEBSOCKET_URL,
  AGGREGATOR_UPLOAD_URL,
} from './constants';
import Title from './components/title';
import { styles } from './home.styles';
import ErrorMessage from './components/ErrorMessage';
import {
  Box,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Typography,
  CircularProgress,
  Chip,
} from '@mui/material';
import { HomepageState } from './types';
import Dashboard from './dashboard';
import theme from './theme';
import { v4 as uuidv4 } from 'uuid';
import ApiAndBatchConfig from './components/ApiAndBatchConfig';
import SelectModelType from './components/SelectModelType';
import MetricsSelector from './components/MetricsSelector';
import { useUser } from './context/userid.context';

function Homepage() {
  // const [socket, setSocket] = useState<WebSocket | null>(null);
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
    legislationChips: [],
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

  // const disconnectRef = useRef(false); // Track whether disconnect is intentional
  // let modelTypesToMetrics: { [key: string]: string[] } = {};

  const setStateWrapper = <K extends keyof typeof state>(
    key: K,
    value: (typeof state)[K]
  ) => {
    setState((prevState) => ({
      ...prevState,
      [key]: value,
    }));
  };

  const [modelTypesToMetrics, setModelTypesToMetrics] = useState<{
    [key: string]: string[];
  }>({});

  const { socket, userId } = useUser();

  useEffect(() => {
    const initModelTypesToMetrics = () => {
      fetchMetricInfo()
        .then((metrics) => {
          setModelTypesToMetrics(metrics);
          console.log('Fetched metrics successfully');
        })
        .catch((error) => {
          console.error('Failed to fetch metric info:', error);
          // Call the function again after 10 seconds
          setTimeout(initModelTypesToMetrics, 10000);
        });
    };

    const initLegislationLabels = () => {
      fetchLegislationInfo()
        .then((legislation) => {
          const legislationChips = legislation.legislation.map(
            (item: string) => {
              return {
                id: item,
                label: item,
                selected: true,
              };
            }
          );
          console.log('legislation info: ', legislationChips);
          setStateWrapper('legislationChips', legislationChips);
          console.log('legislation info2: ', legislationChips);
        })
        .catch((error) => {
          console.error('Failed to fetch legislation info:', error);
          // Call the function after 10 seconds
          setTimeout(initLegislationLabels, 10000);
        });
    };
    initModelTypesToMetrics();
    initLegislationLabels();
  }, []);

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
        .map((legislationChip) => legislationChip.label),
    };
    console.log('Data:', frontend_info);
    try {
      // Send POST request to backend server
      const postFrontend = await fetch(AGGREGATOR_UPLOAD_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(frontend_info),
      });
      console.log('Status: ', postFrontend.status);
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
      console.log('Legislation Error status code:', error);
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

  if (!socket || Object.keys(modelTypesToMetrics).length === 0) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
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
                <ApiAndBatchConfig
                  getValues={getValues}
                  state={state}
                  setStateWrapper={setStateWrapper}
                  checkBatchConfig={checkBatchConfig}
                  getErrorProps={getErrorProps}
                  styles={styles}
                />
              )}
              {/* 2. SELECT MODEL TYPE */}
              {index === 1 && (
                <SelectModelType
                  state={state}
                  metricsHelperText={state.metricsHelperText}
                  modelTypesToMetrics={modelTypesToMetrics}
                  handleModelTypeChange={handleModelTypeChange}
                  setStateWrapper={setStateWrapper}
                />
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
                <MetricsSelector
                  metricsHelperText={state.metricsHelperText}
                  metricChips={state.metricChips}
                  onToggleMetric={(index) => {
                    const newMetricChips = [...state.metricChips];
                    newMetricChips[index].selected =
                      !newMetricChips[index].selected;
                    setStateWrapper('metricChips', newMetricChips);
                  }}
                  state={state}
                  setStateWrapper={setStateWrapper}
                />
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
