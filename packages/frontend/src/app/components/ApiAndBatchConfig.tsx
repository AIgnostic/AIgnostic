import React from 'react';
import { Box, TextField, Typography } from '@mui/material';
import { HomepageState } from '../types';

interface FieldConfig {
  label: string;
  value: string;
  isValid?: boolean;
  validKey?: string;
}

interface ApiAndBatchConfigProps {
  getValues: {
    [key: string]: FieldConfig;
  };
  state: any; // Replace with your specific state type if available.
  setStateWrapper: <K extends 'dashboardKey' | keyof HomepageState>(
    key: K,
    value: (HomepageState & { dashboardKey: number })[K]
  ) => void;
  checkBatchConfig: (batchSize: number, numberOfBatches: number) => boolean;
  getErrorProps: (
    isValid: boolean,
    errorMessage: string
  ) => { error: boolean; helperText: string };
  styles: { [key: string]: any };
}

const ApiAndBatchConfig: React.FC<ApiAndBatchConfigProps> = ({
  getValues,
  state,
  setStateWrapper,
  checkBatchConfig,
  getErrorProps,
  styles,
}) => {
  return (
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
                  field.validKey as 'dashboardKey' | keyof HomepageState,
                  // checkURL(field.value)
                  true
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
              setStateWrapper(key as keyof HomepageState, e.target.value);
            }}
            onBlur={handleOnBlur}
            helperText={
              field.isValid !== undefined ? errorProps?.helperText : ''
            }
            error={field.isValid !== undefined ? errorProps?.error : false}
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
                ? 'Number of batches must be greater than 0'
                : !state.isBatchConfigValid
                ? 'Invalid batch configuration'
                : ''
            }
            onChange={(e) =>
              setStateWrapper(
                'numberOfBatches' as keyof HomepageState,
                e.target.value
              )
            }
            onBlur={() => {
              const isValid = checkBatchConfig(
                state.batchSize,
                state.numberOfBatches
              );
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
                ? 'Batch size must be greater than 0'
                : !state.isBatchConfigValid
                ? 'Invalid batch configuration'
                : ''
            }
            onChange={(e) =>
              setStateWrapper(
                'batchSize' as keyof HomepageState,
                e.target.value
              )
            }
            onBlur={() => {
              const isValid = checkBatchConfig(
                state.batchSize,
                state.numberOfBatches
              );
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
            helperText={
              !state.isMaxConcurrentBatchesValid
                ? 'Value must be between 1 and 30'
                : ''
            }
            onChange={(e) =>
              setStateWrapper(
                'maxConcurrentBatches' as keyof HomepageState,
                e.target.value
              )
            }
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
            Total sample size must be between 1000 and 10000, not{' '}
            {state.batchSize * state.numberOfBatches}.
          </Typography>
          {(state.batchSize < 1 || state.numberOfBatches < 1) && (
            <Typography color="error">
              Batch size and number of batches must be positive.
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default ApiAndBatchConfig;
