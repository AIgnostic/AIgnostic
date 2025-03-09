import React from 'react';
import { Box, Chip } from '@mui/material';
import FileUploadComponent from './FileUploadComponent';
import { IS_PROD } from '../env'; // Adjust the import path as needed
import { HomepageState } from '../types';

export interface MetricChip {
  id: string;
  label: string;
  selected: boolean;
}

interface MetricsSelectorProps {
  metricsHelperText: string;
  metricChips: MetricChip[];
  onToggleMetric: (index: number) => void;
  state: any; // Replace with your specific state type if available
  setStateWrapper: <K extends 'dashboardKey' | keyof HomepageState>(
    key: K,
    value: (HomepageState & { dashboardKey: number })[K]
  ) => void;
}

const MetricsSelector: React.FC<MetricsSelectorProps> = ({
  metricsHelperText,
  metricChips,
  onToggleMetric,
  state,
  setStateWrapper,
}) => {
  return (
    <Box style={{ padding: '15px' }}>
      <p style={{ color: 'red' }}>{metricsHelperText}</p>
      {metricChips.map((metricChip, index) => (
        <Chip
          key={metricChip.id || index}
          label={metricChip.label}
          variant="filled"
          onDelete={() => {
            metricChip.selected = !metricChip.selected;
            setStateWrapper('metricChips', [...metricChips]);
          }}
          onClick={() => {
            metricChip.selected = !metricChip.selected;
            setStateWrapper('metricChips', [...metricChips]);
          }}
          color={metricChip.selected ? 'secondary' : 'default'}
          style={{ margin: '5px' }}
        />
      ))}
      {!IS_PROD && (
        <FileUploadComponent state={state} setStateWrapper={setStateWrapper} />
      )}
    </Box>
  );
};

export default MetricsSelector;
