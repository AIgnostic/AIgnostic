// tests/fileupload.test.tsx

import React, { act } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FileUploadComponent from '../src/app/components/FileUploadComponent';
import '@testing-library/jest-dom';

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: async () => ({ task_to_metric_map: {} }),
  })
) as jest.Mock;

const dummyState = { dashboardKey: 0 };
const setStateWrapper = jest.fn();

//mock userid.contxt.tsx useUser hook
jest.mock('../src/app/context/userid.context', () => ({
  useUser: () => ({ userId: '123' }),
}));

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

    const uploadButton = screen.getByText(/Upload Python File/i);
    const pythonInput = uploadButton.querySelector('input[type="file"]');
    expect(pythonInput).toBeInTheDocument();

    const testFile = new File(['print("Hello World")'], 'test.py', {
      type: 'text/plain',
    });

    await act(async () => {
      fireEvent.change(pythonInput!, { target: { files: [testFile] } });
    });

    await waitFor(() =>
      expect(screen.getByText(/Python File: test\.py/i)).toBeInTheDocument()
    );
  });

  test('submits files successfully', async () => {
    sessionStorage.setItem('userId', '123');

    await act(async () => {
      render(
        <FileUploadComponent
          state={dummyState}
          setStateWrapper={setStateWrapper}
        />
      );
    });

    // Upload a Python file
    const uploadButton = screen.getByText(/Upload Python File/i);
    const pythonInput = uploadButton.querySelector('input[type="file"]');
    expect(pythonInput).toBeInTheDocument();

    const testFile = new File(['print("Hello World")'], 'test.py', {
      type: 'text/plain',
    });
    await act(async () => {
      fireEvent.change(pythonInput!, { target: { files: [testFile] } });
    });

    // Mock fetch for successful file submission
    const fetchMock = jest.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    // Click "Submit Files"
    const submitButton = screen.getByText(/Submit Files/i);
    await act(async () => {
      fireEvent.click(submitButton);
    });

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/upload-metrics-and-dependencies?user_id=123'),
      expect.objectContaining({ method: 'POST' })
    );
  });

  //
  // Additional tests to cover handleClearUserData and handleInspectFunctions
  //

  test('clears user data successfully', async () => {
    // Set a dummy userId so the userId check passes
    sessionStorage.setItem('userId', '123');

    // Mock fetch calls for file upload (success) and clearing user data (success)
    const fetchMock = jest
      .spyOn(global, 'fetch')
      .mockImplementation((url: RequestInfo) => {
        // Upload endpoint
        if (
          typeof url === 'string' &&
          url.includes('/upload-metrics-and-dependencies')
        ) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true }),
          } as Response);
        }
        // Clear user data endpoint
        if (typeof url === 'string' && url.includes('/clear-user-data/')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({}),
          } as Response);
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

    // Render and upload a Python file so that "functions" becomes []
    await act(async () => {
      render(
        <FileUploadComponent
          state={dummyState}
          setStateWrapper={setStateWrapper}
        />
      );
    });

    const uploadButton = screen.getByText(/Upload Python File/i);
    const pythonInput = uploadButton.querySelector('input[type="file"]')!;
    const testFile = new File(['print("Hello World")'], 'test.py', {
      type: 'text/plain',
    });
    await act(async () => {
      fireEvent.change(pythonInput, { target: { files: [testFile] } });
    });

    // Submit files (makes functions = [])
    const submitButton = screen.getByText(/Submit Files/i);
    await act(async () => {
      fireEvent.click(submitButton);
    });
    // Wait for submission to finish
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/upload-metrics-and-dependencies?user_id=123'),
        expect.objectContaining({ method: 'POST' })
      )
    );

    // Now "Clear Data" button should appear because functions = []
    const clearButton = screen.getByText(/Clear Data/i);
    expect(clearButton).toBeInTheDocument();

    // Click "Clear Data"
    await act(async () => {
      fireEvent.click(clearButton);
    });

    // Wait for the clear call
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/clear-user-data/123'),
        expect.objectContaining({ method: 'DELETE' })
      )
    );

    // After clearing, the python file name and the functions chips should disappear
    // Because setPythonFile(null), setRequirementsFile(null), setFunctions(null)
    expect(screen.queryByText(/test\.py/i)).not.toBeInTheDocument();
  });

  test('handles error when clearing user data fails', async () => {
    sessionStorage.setItem('userId', '123');

    // Mock fetch for upload success, but clearing fails
    const fetchMock = jest
      .spyOn(global, 'fetch')
      .mockImplementation((url: RequestInfo) => {
        if (
          typeof url === 'string' &&
          url.includes('/upload-metrics-and-dependencies')
        ) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true }),
          } as Response);
        }
        if (typeof url === 'string' && url.includes('/clear-user-data/')) {
          return Promise.resolve({
            ok: false, // <--- force error
            json: async () => ({
              detail: 'Something went wrong clearing data',
            }),
          } as Response);
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

    render(
      <FileUploadComponent
        state={dummyState}
        setStateWrapper={setStateWrapper}
      />
    );

    // Upload and submit a Python file to reveal the "Clear Data" button
    const uploadButton = screen.getByText(/Upload Python File/i);
    const pythonInput = uploadButton.querySelector('input[type="file"]')!;
    const testFile = new File(['print("Hello World")'], 'test.py', {
      type: 'text/plain',
    });

    await act(async () => {
      fireEvent.change(pythonInput, { target: { files: [testFile] } });
    });

    const submitButton = screen.getByText(/Submit Files/i);
    await act(async () => {
      fireEvent.click(submitButton);
    });

    // Click "Clear Data" after successful upload
    const clearButton = await screen.findByText(/Clear Data/i);
    await act(async () => {
      fireEvent.click(clearButton);
    });

    // Expect an error message
    await waitFor(() =>
      expect(
        screen.getByText(/Clearing user data failed:/i)
      ).toBeInTheDocument()
    );
  });

  test('handles error when inspecting functions fails', async () => {
    sessionStorage.setItem('userId', '123');

    // Mock fetch for file upload success, but inspection fails
    const fetchMock = jest
      .spyOn(global, 'fetch')
      .mockImplementation((url: RequestInfo) => {
        // Upload is successful
        if (
          typeof url === 'string' &&
          url.includes('/upload-metrics-and-dependencies')
        ) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true }),
          } as Response);
        }
        // Inspect fails
        if (
          typeof url === 'string' &&
          url.includes('/inspect-uploaded-functions/')
        ) {
          return Promise.resolve({
            ok: false,
            json: async () => ({ detail: 'Failed to inspect functions' }),
          } as Response);
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

    render(
      <FileUploadComponent
        state={dummyState}
        setStateWrapper={setStateWrapper}
      />
    );

    // Upload a Python file and submit to set functions = []
    const uploadButton = screen.getByText(/Upload Python File/i);
    const pythonInput = uploadButton.querySelector('input[type="file"]')!;
    const testFile = new File(['print("Hello World")'], 'test.py', {
      type: 'text/plain',
    });
    await act(async () => {
      fireEvent.change(pythonInput, { target: { files: [testFile] } });
    });

    const submitButton = screen.getByText(/Submit Files/i);
    await act(async () => {
      fireEvent.click(submitButton);
    });

    // The "Inspect Uploaded Functions" button should appear now
    const inspectButton = await screen.findByText(
      /Inspect Uploaded Functions/i
    );
    await act(async () => {
      fireEvent.click(inspectButton);
    });

    // Check that an error is displayed
    await waitFor(() =>
      expect(screen.getByText(/Inspection failed:/i)).toBeInTheDocument()
    );
  });
});
