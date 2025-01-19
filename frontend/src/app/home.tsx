import React, { useState } from 'react';
import checkURL from './utils';
import { Box, Button, Chip, TextField } from '@mui/material';
import { Stepper, Step, StepLabel, StepContent, Typography } from '@mui/material';

const steps = [
  {
    label: 'Enter model and dataset API URLs',
    description: `Enter the URLs for your model and dataset APIs to get started.
                  For more information about creating the APIs, see the documentation - click 'Getting Started'.`,
  },
  {
    label: 'Select Legislation',
    description:
      `Select the legislations that you want to comply with.`,
  },
  {
    label: 'Select Metrics',
    description:
      `Select the metrics you want to analyze your model with. 
       These will be used to quantify your compliance score with your selected metrics.`,
  },
  {
    label: 'Summary and Generate Report',
    description: `Check that you are happy with your selections and generate your compliance report.
                  Report generation may take some time.`,
  },
];

const metrics = ["Accuracy", "Precision", "Recall"];


function Homepage() {
  const [modelURL, setModelURL] = useState('');
  const [datasetURL, setDatasetURL] = useState('');
  const [isModelURLValid, setIsModelURLValid] = useState(true);
  const [isDatasetURLValid, setIsDatasetURLValid] = useState(true);
  const [activeStep, setActiveStep] = React.useState(0);
  const [metricChips, setMetricChips] = useState(metrics.map((metric) => {return {"label": metric, "selected": true}}));


  const handleSubmit = () => {
    if (modelURL && datasetURL) {
      console.log(`Input 1: ${modelURL}, Input 2: ${datasetURL}`);
      console.log(`Selected Metrics: ${metricChips.filter((metricChip) => metricChip.selected).map((metricChip) => metricChip.label).join(", ")}`);
      console.log(checkURL(modelURL) && checkURL(datasetURL))
      
      const user_info = {"modelURL": modelURL, 
        "datasetURL": datasetURL,
        "metrics": metricChips.filter((metricChip) => metricChip.selected).map((metricChip) => metricChip.label)
      }
      
      // send user_info to controller 
    } else {
      console.log('Please fill in both text inputs.');
      // alert('Please fill in both text inputs.');
    }
  };

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
  };


  
  

  return (
    <Box sx={[styles.container ]}>
      <Box style={styles.container}>
        <Box style={styles.logoContainer}>
          
          <h1 style={styles.logoText}>AIgnostic</h1>
        </Box>

        <Box style={styles.horizontalContainer}>
          New to AIgnostic? Read the docs to get started: 
          <Button style={styles.button}>
            Getting Started
          </Button>
        </Box> 
      </Box>
      
      <Stepper activeStep={activeStep} style={{width: "80%"}} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.label}>
            <StepLabel
              optional={
                index === steps.length - 1 ? (
                  <Typography variant="caption">Last step</Typography>
                ) : null
              }
            >
              {step.label}
            </StepLabel>
            <StepContent>
              <Typography>{step.description}</Typography>

              {index === 0 && 
                  (<Box>
                      <TextField
                        type="text"
                        placeholder="Enter Model API URL"
                        value={modelURL}
                        onChange={(e) => setModelURL(e.target.value)}
                        onBlur={() => setIsModelURLValid(checkURL(modelURL))}
                        style={styles.input}
                        error={!!modelURL && !isModelURLValid}
                        helperText={(!!modelURL && !isModelURLValid) ? 'Invalid URL' : ''}
                      />
                      <TextField
                        type="text"
                        placeholder="Enter Dataset API URL"
                        value={datasetURL}
                        onChange={(e) => setDatasetURL(e.target.value)}
                        onBlur={() => setIsDatasetURLValid(checkURL(datasetURL))}
                        style={styles.input}
                        error={!!datasetURL && !isDatasetURLValid}
                        helperText={(!!datasetURL && !isDatasetURLValid) ? 'Invalid URL' : ''}
                      />
                      
                    </Box>)
              }

              {index === 2 && 
                  (<Box>
                    {metricChips.map((metricChip) => (
                      <Chip 
                        label={metricChip.label}
                        variant="filled"
                        onDelete={() => {metricChip.selected = !metricChip.selected; setMetricChips([...metricChips])}}
                        onClick={() => {metricChip.selected = !metricChip.selected; setMetricChips([...metricChips])}}
                        color={metricChip.selected ? "primary" : "default"}
                        style={{margin: '5px'}} 
                      />
                    ))}
                  </Box>)
              }

              {index === steps.length - 1 &&
                (<Box>
                  <h3>Summary</h3>
                  <p>
                    Model URL: {modelURL}
                    <br/> <br/>
                    Dataset URL: {datasetURL} 
                    <br/> <br/>
                    Metrics: {metricChips.filter((metricChip) => metricChip.selected).map((metricChip) => metricChip.label).join(", ")}
                  </p>
                </Box>)
                  }


              <Box sx={{ mb: 2 }}>
                <Button
                  variant="contained"
                  onClick={handleNext}
                  sx={{ mt: 1, mr: 1 }}
                >
                  {index === steps.length - 1 ? 'Generate Report' : 'Next'}
                </Button>
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

const styles : { [key: string]: React.CSSProperties} = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f5f5f5',
    width: '100%',
    paddingTop: '20px',
  },
  horizontalContainer: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logoText: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#333',
    fontFamily: 'serif',
  },
  formContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  input: {
    width: '100%',
    padding: '10px',
    marginBottom: '10px',
    fontSize: '16px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#007BFF',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    margin: '10px',
  },
};

export default Homepage;
