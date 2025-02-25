import React from "react";
import { render, screen, act } from "@testing-library/react";
import Dashboard from "../src/app/dashboard";
import "@testing-library/jest-dom";


// Mock `ErrorMessage` and `ReportRenderer` components
jest.mock("../src/app/components/ErrorMessage", () => () => (
  <div data-testid="error-message">Error</div>
));
jest.mock("../src/app/components/ReportRenderer", () => () => (
  <div data-testid="report-renderer">Final Report</div>
));

// Mock `@react-pdf/renderer`
jest.mock("@react-pdf/renderer", () => ({
  pdf: jest.fn((component) => ({
    toBlob: jest.fn().mockResolvedValue(component),
  })),
}));

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => "blob:http://localhost/blob");
global.URL.revokeObjectURL = jest.fn();

describe("Dashboard Component", () => {
  let mockWebSocket: Partial<WebSocket>;
  let onCompleteMock: jest.Mock;

  beforeEach(() => {
    // Mock WebSocket
    mockWebSocket = {
      send: jest.fn(),
      close: jest.fn(),
    };
    global.WebSocket = jest.fn(() => mockWebSocket as WebSocket) as any;
    onCompleteMock = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test("renders progress bar and waiting message initially", () => {
    render(<Dashboard onComplete={onCompleteMock} />);
    expect(screen.getByText("0 / 10 batches processed")).toBeInTheDocument();
    expect(screen.getByText("Waiting for messages...")).toBeInTheDocument();
  });

  test("updates log on LOG message", async () => {
    render(<Dashboard onComplete={onCompleteMock} />);

    await act(async () => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({ messageType: "LOG", message: "Processing started" }),
      });
    });

    expect(screen.getByText("Processing started")).toBeInTheDocument();
  });

  test("displays error message on ERROR event", async () => {
    render(<Dashboard onComplete={onCompleteMock} />);

    await act(async () => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({ messageType: "ERROR", message: "Server Error" }),
      });
    });

    expect(screen.getByTestId("error-message")).toBeInTheDocument();
  });

  test("processes METRICS_INTERMEDIATE messages and updates progress", async () => {
    render(<Dashboard onComplete={onCompleteMock} />);

    await act(async () => {
      (mockWebSocket.onmessage as any)({
        data: JSON.stringify({
          messageType: "METRICS_INTERMEDIATE",
          content: { metrics_results: { accuracy: 0.75, precision: 0.5 } },
        }),
      });
    });

    expect(screen.getByText("1 / 10 batches processed")).toBeInTheDocument();
  });

  test("closes WebSocket on unmount", () => {
    const { unmount } = render(<Dashboard onComplete={onCompleteMock} />);
    unmount();
    expect(mockWebSocket.close).toHaveBeenCalled();
  });
});
