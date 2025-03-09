import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Homepage from '../src/app/home';
import { steps } from '../src/app/constants';
import '@testing-library/jest-dom';
import { checkBatchConfig, checkURL } from '../src/app/utils';
import { MemoryRouter } from 'react-router-dom';

// mock modelTypesToMetrics
jest.mock('../src/app/constants', () => ({
  __esModule: true,
  modelTypesToMetrics: {
    'Binary Classification': ['Metric1', 'Metric2'],
  },
  steps: jest.requireActual('../src/app/constants').steps,
  activeStepToInputConditions: jest.requireActual('../src/app/constants')
    .activeStepToInputConditions,
  initializeModelTypesToMetrics: jest.fn(),
  WEBSOCKET_URL: 'ws://localhost:8000/ws',
}));

jest.mock('@react-pdf/renderer', () => ({
  Document: ({ children }: any) => <div>{children}</div>,
  Page: ({ children }: any) => <div>{children}</div>,
  Text: ({ children }: any) => <span>{children}</span>,
  View: ({ children }: any) => <div>{children}</div>,
  StyleSheet: { create: (styles: any) => styles },
}));

jest.mock('../src/app/utils', () => ({
  __esModule: true,
  checkURL: jest.fn(),
  checkBatchConfig: jest.fn(),
  generateReportText: jest.fn(),
  fetchMetricInfo: jest.fn().mockResolvedValue({
    'Binary Classification': ['Binary Text Classification'],
  }),
  fetchLegislationInfo: jest.fn().mockResolvedValue(['GDPR', 'EU AI Act']),
}));

const mockNavigate = jest.fn();

// Mock useNavigate to return our fake navigate function
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock API Docs component
jest.mock('../src/app/api_docs', () => () => <div>API Documentation</div>);

// Mock useUser to return a fake user ID & mock socket
jest.mock('../src/app/context/userid.context', () => ({
  __esModule: true,
  useUser: () => ({ userId: 'fake-user-id', socket: { onopen: jest.fn() } }),
}));

describe('Title', () => {
  it('should render the title correctly', async () => {
    render(
      <MemoryRouter>
        <Homepage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    expect(screen.getByText('AIgnostic')).toBeInTheDocument();
    expect(
      screen.getByText('New to AIgnostic? Read the docs to get started:')
    ).toBeInTheDocument();
    expect(screen.getByText('Getting Started')).toBeInTheDocument();
  });

  it('should navigate to /api-docs when "Getting Started" is clicked', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Homepage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Getting Started'));

    // Verify that navigate was called with the expected path
    expect(mockNavigate).toHaveBeenCalledWith('/api-docs');
  });
});

describe('Stepper Navigation', () => {
  it('should disable Next state if no API URLs inputted', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const nextButton = screen.getAllByRole('button', { name: /Next/i })[0];
    expect(nextButton).toBeDisabled();
  });

  it('should disable Next state if one of the API URLs are not inputted', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Model API URL/i), {
      target: { value: 'http://valid-model-url.com' },
    });
    const nextButton = screen.getAllByRole('button', { name: /Next/i })[0];
    expect(nextButton).toBeDisabled();
  });
  it('should go to the next step when "Next" button is clicked', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Model API URL/i), {
      target: { value: 'http://valid-model-url.com' },
    });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), {
      target: { value: 'http://valid-dataset-url.com' },
    });
    expect(screen.getByText(steps[0].label)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    expect(screen.getByText(steps[1].description)).toBeInTheDocument();
  });

  it('should go to the previous step when "Back" button is clicked', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    const backButton = screen.getAllByRole('button', { name: /Back/i })[0];
    fireEvent.click(backButton);

    expect(screen.getByText(steps[0].label)).toBeInTheDocument();
  });
});

describe('Form Validation', () => {
  it('should navigate to the next step when URLs are valid', async () => {
    (checkURL as jest.Mock).mockReturnValue(true);

    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Model API URL/i), {
      target: { value: 'http://valid-model-url.com' },
    });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), {
      target: { value: 'http://valid-dataset-url.com' },
    });

    fireEvent.click(screen.getByText('Next'));

    await screen.findByText(/Select the type of model you are using./i);
    expect(
      screen.getByText(/Select the type of model you are using./i)
    ).toBeInTheDocument();
  });
});

describe('Batch Configuration Validation', () => {
  test('should set isBatchConfigValid to false for invalid total sample size', async () => {
    (checkBatchConfig as jest.Mock).mockReturnValue(false);

    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const batchSizeInput = screen.getByLabelText('Batch Size');
    const numberOfBatchesInput = screen.getByLabelText('Number of Batches');

    fireEvent.change(batchSizeInput, { target: { value: '50' } });
    fireEvent.change(numberOfBatchesInput, { target: { value: '15' } });

    fireEvent.blur(batchSizeInput);
    fireEvent.blur(numberOfBatchesInput);

    await waitFor(() => {
      expect(
        screen.getByText(
          'Total sample size must be between 1000 and 10000, not 750.'
        )
      ).toBeInTheDocument();
    });
  });

  test('should set isBatchConfigValid to false for negative batch size', async () => {
    (checkBatchConfig as jest.Mock).mockReturnValue(false);

    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const batchSizeInput = screen.getByLabelText('Batch Size');
    const numberOfBatchesInput = screen.getByLabelText('Number of Batches');

    fireEvent.change(batchSizeInput, { target: { value: '-50' } });
    fireEvent.change(numberOfBatchesInput, { target: { value: '15' } });

    fireEvent.blur(batchSizeInput);
    fireEvent.blur(numberOfBatchesInput);

    await waitFor(() => {
      expect(
        screen.getByText('Batch size and number of batches must be positive.')
      ).toBeInTheDocument();
    });
  });

  test('should set isBatchConfigValid to false for negative number of batches', async () => {
    (checkBatchConfig as jest.Mock).mockReturnValue(false);

    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const batchSizeInput = screen.getByLabelText('Batch Size');
    const numberOfBatchesInput = screen.getByLabelText('Number of Batches');

    fireEvent.change(batchSizeInput, { target: { value: '50' } });
    fireEvent.change(numberOfBatchesInput, { target: { value: '-15' } });

    fireEvent.blur(batchSizeInput);
    fireEvent.blur(numberOfBatchesInput);

    await waitFor(() => {
      expect(
        screen.getByText('Batch size and number of batches must be positive.')
      ).toBeInTheDocument();
    });
  });

  test('should set isBatchConfigValid to true for valid total sample size', async () => {
    (checkBatchConfig as jest.Mock).mockReturnValue(true);

    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const batchSizeInput = screen.getByLabelText('Batch Size');
    const numberOfBatchesInput = screen.getByLabelText('Number of Batches');

    fireEvent.change(batchSizeInput, { target: { value: '200' } });
    fireEvent.change(numberOfBatchesInput, { target: { value: '10' } });

    fireEvent.blur(batchSizeInput);
    fireEvent.blur(numberOfBatchesInput);

    await waitFor(() => {
      expect(
        screen.queryByText('Total sample size must be between 1000 and 10000')
      ).not.toBeInTheDocument();
    });
  });
});

// test('shoud set isBatchValidConfig  to send error for invalid number of batches', async () => {
//   (checkBatchConfig as jest.Mock).mockReturnValue(true);

//   render(<Homepage />);
//   const batchSizeInput = screen.getByLabelText('Batch Size');
//   const numberOfBatchesInput = screen.getByLabelText('Number of Batches');

//   // Set invalid values for batch size and number of batches
//   fireEvent.change(batchSizeInput, { target: { value: '50' } }); // Valid batch size
//   fireEvent.change(numberOfBatchesInput, { target: { value: '-15' } }); // Invalid number of batches (negative)

//   // Trigger onBlur event to validate the inputs
//   fireEvent.blur(batchSizeInput);
//   fireEvent.blur(numberOfBatchesInput);

//   // Wait for the state change and check if the error message appears
//   await waitFor(() => {
//     expect(
//       screen.getByText('Batch size and number of batches must be positive.')
//     ).toBeInTheDocument();
//   });
// })

test('should set isBatchConfigValid to true for valid total sample size', async () => {
  // Mock checkBatchConfig to return true for valid batch config
  (checkBatchConfig as jest.Mock).mockReturnValue(true);

  render(<Homepage />);

  const batchSizeInput = screen.getByLabelText('Batch Size');
  const numberOfBatchesInput = screen.getByLabelText('Number of Batches');

  // Set valid values for batch size and number of batches
  fireEvent.change(batchSizeInput, { target: { value: '200' } }); // Valid batch size
  fireEvent.change(numberOfBatchesInput, { target: { value: '10' } }); // Valid number of batches

  // Trigger onBlur event to validate the inputs
  fireEvent.blur(batchSizeInput);
  fireEvent.blur(numberOfBatchesInput);
  // Wait for the state change and check if the error message disappears
  await waitFor(() => {
    expect(
      screen.queryByText('Total sample size must be between 1000 and 10000')
    ).not.toBeInTheDocument();
  });

  // Optionally check if the validation state is set to true (if accessible)
});

describe('Maximum Concurrent Batches Validation', () => {
  it('should update maxConcurrentBatches state on change', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const input = screen.getByLabelText('Maximum Concurrent Batches');

    // Simulate onChange event (user typing a value)
    fireEvent.change(input, { target: { value: '10' } });

    // Check if the state was updated correctly
    expect(input).toHaveValue(10);
  });

  it('should show error if value is out of range onBlur', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const input = screen.getByLabelText('Maximum Concurrent Batches');

    // Simulate an invalid input (less than 1)
    fireEvent.change(input, { target: { value: '0' } });
    fireEvent.blur(input);

    // Check if the error message appears
    expect(
      screen.getByText('Value must be between 1 and 30')
    ).toBeInTheDocument();
  });

  it('should not show error if value is within range onBlur', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const input = screen.getByLabelText('Maximum Concurrent Batches');

    // Simulate a valid input (within the range of 1 to 30)
    fireEvent.change(input, { target: { value: '15' } });
    fireEvent.blur(input);

    // Check if the error message does not appear
    expect(
      screen.queryByText('Value must be between 1 and 30')
    ).not.toBeInTheDocument();
  });

  it('should show an error if input is greater than 30 onBlur', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const input = screen.getByLabelText('Maximum Concurrent Batches');

    // Simulate an invalid input (greater than 30)
    fireEvent.change(input, { target: { value: '35' } });
    fireEvent.blur(input);

    expect(
      screen.getByText('Value must be between 1 and 30')
    ).toBeInTheDocument();
  });

  it('should show an error if input is less than 1 onBlur', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    const input = screen.getByLabelText('Maximum Concurrent Batches');

    // Simulate an invalid input (less than 1)
    fireEvent.change(input, { target: { value: '0' } });
    fireEvent.blur(input);

    expect(
      screen.getByText('Value must be between 1 and 30')
    ).toBeInTheDocument();
  });
});

describe('UI Components', () => {
  it('should render the Homepage correctly', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    expect(screen.getAllByText(/AIgnostic/i).length).toBeGreaterThan(0);

    expect(screen.getByText(/'GETTING STARTED'/i)).toBeInTheDocument();

    expect(screen.getByText('Back')).toBeInTheDocument();
  });

  it('should enable "Next" button when valid URLs are entered', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Model API URL/i), {
      target: { value: 'http://valid-model-url.com' },
    });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), {
      target: { value: 'http://valid-dataset-url.com' },
    });

    expect(screen.getByText('Next')).toBeEnabled();
  });
});

describe('Model Type Selection', () => {
  it('should disable Next state on radio button if not selected', async () => {
    render(<Homepage />);
    await waitFor(() => {
      expect(screen.queryByTestId('circular-progress')).not.toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Model API URL/i), {
      target: { value: 'http://valid-model-url.com' },
    });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), {
      target: { value: 'http://valid-dataset-url.com' },
    });
    fireEvent.click(screen.getAllByText('Next')[0]);

    const nextButton = screen.getAllByRole('button', { name: /Next/i })[1];

    expect(nextButton).toBeDisabled();
  });
});
