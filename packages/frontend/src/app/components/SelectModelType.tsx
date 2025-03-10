import React from 'react';
import {
  Box,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';
import { HomepageState } from '../types';

interface SelectModelTypeProps {
  state: {
    metricsHelperText: string;
    selectedModelType: string;
  };
  metricsHelperText: string;
  modelTypesToMetrics: { [key: string]: string[] };
  handleModelTypeChange: (value: string) => void;
  setStateWrapper: <K extends 'dashboardKey' | keyof HomepageState>(
    key: K,
    value: (HomepageState & { dashboardKey: number })[K]
  ) => void;
}

const SelectModelType: React.FC<SelectModelTypeProps> = ({
  state,
  modelTypesToMetrics,
  handleModelTypeChange,
  setStateWrapper,
  metricsHelperText,
}) => {
  return (
    <Box style={{ padding: '15px' }}>
      <p style={{ color: 'red' }}>{metricsHelperText}</p>

      <FormControl component="fieldset">
        <FormLabel component="legend">Select Model Type</FormLabel>
        <RadioGroup
          value={state.selectedModelType}
          onChange={(event) => {
            handleModelTypeChange(event.target.value);
            setStateWrapper('selectedModelType', event.target.value);
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
  );
};

export default SelectModelType;
