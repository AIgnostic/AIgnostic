import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApiAndBatchConfig from '../src/app/components/ApiAndBatchConfig';

describe('ApiAndBatchConfig Component', () => {
  const mockSetStateWrapper = jest.fn();
  const mockCheckBatchConfig = jest.fn(
    (batchSize, numberOfBatches) =>
      batchSize * numberOfBatches >= 1000 &&
      batchSize * numberOfBatches <= 10000
  );
  const mockGetErrorProps = jest.fn((isValid: boolean, msg: string) => ({
    error: !isValid,
    helperText: !isValid ? msg : '',
  }));
  const styles = {
    input: { margin: '8px' },
  };

  const getValues = {
    modelURL: {
      label: 'Model URL',
      value: 'http://testmodel.com',
      isValid: true,
      validKey: 'modelURLValid',
    },
    datasetURL: { label: 'Dataset URL', value: 'http://testdataset.com' },
    modelAPIKey: {
      label: 'Model API Key',
      value: 'abc123',
      isValid: false,
      validKey: 'modelAPIKeyValid',
    },
    datasetAPIKey: {
      label: 'Dataset API Key',
      value: 'def456',
      isValid: true,
      validKey: 'datasetAPIKeyValid',
    },
  };

  const state = {
    numberOfBatches: 5,
    batchSize: 10,
    maxConcurrentBatches: 3,
    isBatchConfigValid: true,
    isMaxConcurrentBatchesValid: true,
  };

  const defaultProps = {
    getValues,
    state,
    setStateWrapper: mockSetStateWrapper,
    checkBatchConfig: mockCheckBatchConfig,
    getErrorProps: mockGetErrorProps,
    styles,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all API related TextFields with correct labels and values', () => {
    render(<ApiAndBatchConfig {...defaultProps} />);

    // Check API key fields
    Object.keys(getValues).forEach((key) => {
      const { label, value } = getValues[key as keyof typeof getValues];
      const input = screen.getByDisplayValue(value);
      expect(screen.getByLabelText(label)).toBe(input);
    });
  });

  test('calls setStateWrapper on change of API field input', () => {
    render(<ApiAndBatchConfig {...defaultProps} />);
    const modelURLInput = screen.getByDisplayValue(getValues.modelURL.value);
    fireEvent.change(modelURLInput, {
      target: { value: 'http://newmodel.com' },
    });
    // setStateWrapper should be called with key (as HomepageState) and new value.
    expect(mockSetStateWrapper).toHaveBeenCalledWith(
      'modelURL',
      'http://newmodel.com'
    );
  });

  test('calls setStateWrapper onBlur for fields with validation', () => {
    render(<ApiAndBatchConfig {...defaultProps} />);
    // Only fields that have both isValid and validKey should have an onBlur handler.
    // For modelAPIKey field, isValid and validKey exist.
    const modelAPIKeyInput = screen.getByDisplayValue(
      getValues.modelAPIKey.value
    );
    fireEvent.blur(modelAPIKeyInput);
    expect(mockSetStateWrapper).toHaveBeenCalledWith('modelAPIKeyValid', true);
    // For datasetURL field, onBlur should not trigger setStateWrapper since no validation props available.
    const datasetURLInput = screen.getByDisplayValue(
      getValues.datasetURL.value
    );
    fireEvent.blur(datasetURLInput);
    // No additional call expected (aside from previous ones)
    expect(mockSetStateWrapper).toHaveBeenCalledTimes(1);
  });

  test('renders batch config fields with correct default values', () => {
    render(<ApiAndBatchConfig {...defaultProps} />);
    expect(
      screen.getByDisplayValue(state.numberOfBatches.toString())
    ).toBeInTheDocument();
    expect(
      screen.getByDisplayValue(state.batchSize.toString())
    ).toBeInTheDocument();
    expect(
      screen.getByDisplayValue(state.maxConcurrentBatches.toString())
    ).toBeInTheDocument();
  });

  test('updates batch config valid state on onBlur for Number of Batches and Batch Size', () => {
    render(<ApiAndBatchConfig {...defaultProps} />);
    const numBatchesField = screen.getByLabelText('Number of Batches');
    const batchSizeField = screen.getByLabelText('Batch Size');

    // Simulate changing values
    fireEvent.change(numBatchesField, { target: { value: '6' } });
    fireEvent.change(batchSizeField, { target: { value: '200' } });

    // Simulate blur which triggers validation
    fireEvent.blur(numBatchesField);
    fireEvent.blur(batchSizeField);

    // Expect checkBatchConfig to be called twice with current state (initial state remains unchanged in test)
    expect(mockCheckBatchConfig).toHaveBeenCalledWith(
      state.batchSize,
      state.numberOfBatches
    );
    // And setStateWrapper should have been used to update isBatchConfigValid.
    expect(mockSetStateWrapper).toHaveBeenCalledWith(
      'isBatchConfigValid',
      expect.any(Boolean)
    );
  });

  test('displays error Typography when batch configuration is invalid', () => {
    const invalidState = {
      ...state,
      isBatchConfigValid: false,
      numberOfBatches: 2,
      batchSize: 3,
    };

    render(<ApiAndBatchConfig {...defaultProps} state={invalidState} />);
    expect(
      screen.getByText(/Total sample size must be between 1000 and 10000/)
    ).toBeInTheDocument();
    // Also check if error message appears when batchSize or numberOfBatches are less than 1
    const changedState = { ...invalidState, numberOfBatches: 0 };
    render(<ApiAndBatchConfig {...defaultProps} state={changedState} />);
    expect(
      screen.getByText(/Batch size and number of batches must be positive./)
    ).toBeInTheDocument();
  });
});
