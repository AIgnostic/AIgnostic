import React from 'react';
import { render, screen, act } from '@testing-library/react';
import Dashboard from '../src/app/dashboard';
import '@testing-library/jest-dom';
import { pdf } from '@react-pdf/renderer';
import { error } from 'console';
import fs from 'fs';
import { useUser } from '../src/app/context/userid.context';

// Mock `ErrorMessage` and `ReportRenderer` components
jest.mock('../src/app/components/ErrorMessage', () => () => (
  <div data-testid="error-message">Error</div>
));
jest.mock('../src/app/components/ReportRenderer', () => () => (
  <div data-testid="report-renderer">Final Report</div>
));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}));

jest.mock('@react-pdf/renderer', () => ({
  pdf: jest.fn(() => ({
    toBlob: jest.fn(() => Promise.resolve(new Blob())),
  })),
}));

const mockWebSocket = {
  send: jest.fn(),
  close: jest.fn(),
  onopen: jest.fn(),
  onmessage: jest.fn(),
};

jest.mock('../src/app/context/userid.context', () => ({
  __esModule: true,
  useUser: () => ({
    userId: 'fake-user-id',
    socket: mockWebSocket,
    closeSocket: jest.fn(),
  }),
}));

global.fetch = jest.fn();
// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'blob:http://localhost/blob');
global.URL.revokeObjectURL = jest.fn();

describe('Dashboard Component', () => {
  let onCompleteMock: jest.Mock;

  beforeEach(() => {
    // Mock WebSocket
    // mockWebSocket = {
    //   send: jest.fn(),
    //   close: jest.fn(),
    // };
    // global.WebSocket = jest.fn(() => mockWebSocket as WebSocket) as any;
    onCompleteMock = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders progress bar and waiting message initially', () => {
    render(<Dashboard onComplete={onCompleteMock} expectedItems={10} />);
    expect(screen.getByText('0 / 10 batches processed')).toBeInTheDocument();
    expect(screen.getByText('Log: Processing metrics...')).toBeInTheDocument();
  });

  test('updates log on LOG message', async () => {
    render(<Dashboard onComplete={onCompleteMock} expectedItems={10} />);

    await act(async () => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({
          messageType: 'LOG',
          message: 'Processing started',
        }),
      });
    });

    expect(screen.getByText('Log: Processing started')).toBeInTheDocument();
  });

  test('displays error message on ERROR event', async () => {
    render(<Dashboard onComplete={onCompleteMock} expectedItems={10} />);

    await act(async () => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({ messageType: 'ERROR', message: 'Server Error' }),
      });
    });

    expect(screen.getByTestId('error-message')).toBeInTheDocument();
  });

  test('processes METRICS_INTERMEDIATE messages and updates progress', async () => {
    const { container } = render(
      <Dashboard onComplete={onCompleteMock} expectedItems={10} />
    );

    await act(async () => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({
          messageType: 'METRICS_INTERMEDIATE',
          content: {
            metrics_results: {
              accuracy: {
                value: 0.75,
                ideal_value: 0.85,
                range: [0, 1],
                error: null,
              },
              precision: {
                value: 0.75,
                ideal_value: 0.85,
                range: [0, 1],
                error: null,
              },
              error_metric: {
                value: 0,
                ideal_value: 0,
                range: [0, 1],
                error: 'Some error occured',
              },
              infty_metric: {
                value: 0.75,
                ideal_value: 0.85,
                range: [0, null],
                error: null,
              },
              neginfty_metric: {
                value: 0.75,
                ideal_value: 0.85,
                range: [null, 0],
                error: null,
              },
            },
          },
        }),
      });
    });

    expect(screen.getByText('1 / 10 batches processed')).toBeInTheDocument();

    // Ensure that the metrics are displayed
    expect(screen.getByText('Accuracy')).toBeInTheDocument();
    expect(screen.getByText('Precision')).toBeInTheDocument();
    expect(screen.getByText('Error Metric')).toBeInTheDocument();
    expect(screen.getByText('Infty Metric')).toBeInTheDocument();
    expect(screen.getByText('∞')).toBeInTheDocument(); // check nulls are converted to infty symbols
    expect(screen.getByText('Neginfty Metric')).toBeInTheDocument();
    expect(screen.getByText('-∞')).toBeInTheDocument(); // check nulls are converted to infty symbols

    // Ensure that the error message is displayed for erroring metrics
    expect(
      screen.getByText(
        'An error occurred during the computation of this metric.'
      )
    ).toBeInTheDocument();
  });

  test('generates and downloads the report on REPORT message', async () => {
    render(<Dashboard onComplete={onCompleteMock} expectedItems={10} />);

    const mockReportData = {
      /* Your mock report structure */
    };

    await act(async () => {
      (mockWebSocket as any).onmessage({
        data: JSON.stringify({
          messageType: 'REPORT',
          content: mockReportData,
        }),
      });
    });

    // Ensure pdf() was called with ReportRenderer
    expect(pdf).toHaveBeenCalled();
  });

  // test("closes WebSocket on unmount", () => {
  //   const { unmount } = render(<Dashboard
  //     onComplete={onCompleteMock}
  //     socket={mockWebSocket as WebSocket}
  //     disconnectRef={{ current: false }}
  //     expectedItems={10}/>);
  //   unmount();
  //   expect(mockWebSocket.close).toHaveBeenCalled();
  // });
});
