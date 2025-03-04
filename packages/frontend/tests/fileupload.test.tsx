// tests/fileupload.test.tsx

// Define a global fetch before imports so that any module using it (e.g. in utils) won’t error.
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: async () => ({ task_to_metric_map: {} }),
  })
) as jest.Mock;

// eslint-disable-next-line import/first
import React, { act } from 'react';
// eslint-disable-next-line import/first
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
// eslint-disable-next-line import/first
import FileUploadComponent from '../src/app/components/FileUploadComponent';
// eslint-disable-next-line import/first
import '@testing-library/jest-dom';

// Dummy state and wrapper function for testing purposes.
const dummyState = { dashboardKey: 0 };
const setStateWrapper = jest.fn();

describe('FileUploadComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
  });

  test('renders initial UI correctly', async () => {
    await act(async () => {
      render(
        <FileUploadComponent
          state={dummyState}
          setStateWrapper={setStateWrapper}
        />
      );
    });

    // Check for title and buttons.
    expect(screen.getByText(/Upload Your Metrics/i)).toBeInTheDocument();
    expect(screen.getByText(/Upload Python File/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Upload Requirements \(Optional\)/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Submit Files/i)).toBeInTheDocument();
  });

  test('handles file input correctly', async () => {
    await act(async () => {
      render(
        <FileUploadComponent
          state={dummyState}
          setStateWrapper={setStateWrapper}
        />
      );
    });

    // Instead of querying all file inputs, find the button label and then its child input.
    const uploadButton = screen.getByText(/Upload Python File/i);
    const pythonInput = uploadButton.querySelector('input[type="file"]');
    expect(pythonInput).toBeInTheDocument();

    // Create a valid Python file.
    const testFile = new File(['print("Hello World")'], 'test.py', {
      type: 'text/plain',
    });

    // Fire the change event on the file input.
    await act(async () => {
      fireEvent.change(pythonInput!, { target: { files: [testFile] } });
    });

    // Check that the file name is displayed.
    await waitFor(() =>
      expect(screen.getByText(/Python File: test\.py/i)).toBeInTheDocument()
    );
  });

  test('submits files successfully', async () => {
    // Set a dummy userId in sessionStorage.
    sessionStorage.setItem('userId', '123');

    await act(async () => {
      render(
        <FileUploadComponent
          state={dummyState}
          setStateWrapper={setStateWrapper}
        />
      );
    });

    // Grab the file input from the Upload Python File button.
    const uploadButton = screen.getByText(/Upload Python File/i);
    const pythonInput = uploadButton.querySelector('input[type="file"]');
    expect(pythonInput).toBeInTheDocument();

    // Create and select a valid Python file.
    const testFile = new File(['print("Hello World")'], 'test.py', {
      type: 'text/plain',
    });
    await act(async () => {
      fireEvent.change(pythonInput!, { target: { files: [testFile] } });
    });

    // Mock fetch for the submit call.
    const fetchMock = jest.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    // Click the Submit Files button.
    const submitButton = screen.getByText(/Submit Files/i);
    await act(async () => {
      fireEvent.click(submitButton);
    });

    // Wait for the fetch call.
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());

    // Assert that fetch was called with the expected URL and method.
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/upload-metrics-and-dependencies?user_id=123'),
      expect.objectContaining({ method: 'POST' })
    );
  });
});
