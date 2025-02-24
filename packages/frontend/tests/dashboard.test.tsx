import React from 'react';
import { render, screen, act } from '@testing-library/react';
import Dashboard from '../src/app/dashboard';
import '@testing-library/jest-dom';
import { generateReportText } from '../src/app/utils';

// Mock `generateReportText` so we can track its calls
jest.mock('../src/app/utils', () => ({
  generateReportText: jest.fn(() => ({
    save: jest.fn(), // Mock `save()` method
  })),
}));
jest.mock('../src/app/components/ErrorMessage', () => () => <div data-testid="error-message">Error</div>);

describe('Dashboard Component', () => {
  let mockWebSocket: Partial<WebSocket>;
  let onCompleteMock: jest.Mock;

  beforeEach(() => {
    mockWebSocket = {
      send: jest.fn(),
      close: jest.fn(),
    };
    global.WebSocket = jest.fn(() => mockWebSocket as WebSocket) as any;
    onCompleteMock = jest.fn();
  });

  test('renders progress bar and waiting message initially', () => {
    render(<Dashboard onComplete={onCompleteMock} />);
    expect(screen.getByText('0 / 10 batches processed')).toBeInTheDocument();
    expect(screen.getByText('Waiting for messages...')).toBeInTheDocument();
  });

  test('updates log on LOG message', async () => {
    render(<Dashboard onComplete={onCompleteMock} />);

    act(() => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({ messageType: 'LOG', message: 'Processing started' }),
      });
    });

    expect(screen.getByText('Processing started')).toBeInTheDocument();
  });

  test('displays error message on ERROR event', async () => {
    render(<Dashboard onComplete={onCompleteMock} />);

    act(() => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({ messageType: 'ERROR', message: 'Server Error' }),
      });
    });

    expect(screen.getByTestId('error-message')).toBeInTheDocument();
  });

  test('processes METRICS_INTERMEDIATE messages and updates progress', async () => {
    render(<Dashboard onComplete={onCompleteMock} />);

    act(() => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({
          messageType: 'METRICS_INTERMEDIATE',
          content: { metrics_results: {"accuracy": 0.75, "precision": 0.5} },
        }),
      });
    });

    expect(screen.getByText('1 / 10 batches processed')).toBeInTheDocument();
  });

  test('processes REPORT messages and generates report', () => {
    const onCompleteMock = jest.fn();
    render(<Dashboard onComplete={onCompleteMock} />);

    const reportData = {
      property: 'Test Property',
      computedMetrics: [{ metric: 'accuracy', result: '0.9' }],
      legislationExtracts: ['Extract 1'],
      llmInsights: ['Insight 1'],
    };

    act(() => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({
          messageType: 'REPORT',
          content: reportData,
        }),
      });
    });

    // Ensure `generateReportText` was called with correct data
    expect(generateReportText).toHaveBeenCalledWith(reportData);

    // Ensure `save()` method was called on the generated document
    const generatedDoc = (generateReportText as jest.Mock).mock.results[0].value;
    expect(generatedDoc.save).toHaveBeenCalledWith('AIgnostic_Report.pdf');
  });

  test('closes WebSocket on unmount', () => {
    const { unmount } = render(<Dashboard onComplete={onCompleteMock} />);
    unmount();
    expect(mockWebSocket.close).toHaveBeenCalled();
  });
});
