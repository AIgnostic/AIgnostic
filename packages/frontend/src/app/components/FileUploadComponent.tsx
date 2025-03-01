import { useState } from 'react';
import { Button, Box, Typography } from '@mui/material';
import theme from '../theme';
import { USER_METRICS_SERVER_URL } from '../constants';

function FileUploadComponent() {
  const [pythonFile, setPythonFile] = useState<File | null>(null);
  const [requirementsFile, setRequirementsFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    fileType: 'python' | 'requirements'
  ) => {
    const file = event.target.files?.[0] || null;

    if (fileType === 'python' && file && file.name.endsWith('.py')) {
      setPythonFile(file);
      setError(null);
    } else if (
      fileType === 'requirements' &&
      file &&
      file.name.endsWith('.txt')
    ) {
      setRequirementsFile(file);
      setError(null);
    } else {
      setError('Invalid file type. Please upload a .py or .txt file.');
    }
  };

  const handleSubmitFiles = async () => {
    if (!pythonFile) {
      setError('Please upload a Python file before submitting.');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('script', pythonFile);
    if (requirementsFile) {
      formData.append('requirements', requirementsFile);
    }

    try {
      const response = await fetch(
        `${USER_METRICS_SERVER_URL}/upload-metrics-and-dependencies`,
        {
          method: 'POST',
          body: formData,
        }
      );

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.detail || `Error ${response.status}`);
      }

      console.log('Files uploaded successfully:', responseData);
      setFileId(responseData.file_id);
    } catch (error) {
      setError(`Upload failed: ${(error as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleClearServer = async () => {
    setUploading(true);
    setError(null);

    try {
      const response = await fetch(`${USER_METRICS_SERVER_URL}/clear-server`, {
        method: 'DELETE',
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.detail || `Error ${response.status}`);
      }

      console.log('Server cleared successfully:', responseData);
      setPythonFile(null);
      setRequirementsFile(null);
      setFileId(null);
    } catch (error) {
      setError(`Clearing server failed: ${(error as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  const [functions, setFunctions] = useState<string[] | null>(null);

  const handleInspectFunctions = async () => {
    if (!fileId) {
      setError('No file ID found. Please upload files first.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await fetch(
        `${USER_METRICS_SERVER_URL}/inspect-uploaded-functions/${fileId}`,
        {
          method: 'GET',
        }
      );

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.detail || `Error ${response.status}`);
      }

      setFunctions(responseData.functions);

      console.log('Functions inspected successfully:', responseData);
      // Handle the inspected functions as needed
    } catch (error) {
      setError(`Inspection failed: ${(error as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box
      sx={{
        padding: 2,
        backgroundColor: theme.palette.background.paper,
        borderRadius: 2,
        margin: 2,
        boxShadow: theme.shadows[3],
        elevation: 3,
      }}
    >
      <Typography variant="h6">Upload Your Metrics</Typography>

      <Button variant="contained" component="label" sx={{ margin: 1 }}>
        Upload Python File
        <input
          type="file"
          hidden
          onChange={(e) => handleFileChange(e, 'python')}
        />
      </Button>
      {pythonFile && (
        <Typography variant="body2">Python File: {pythonFile.name}</Typography>
      )}

      <Button variant="contained" component="label" sx={{ margin: 1 }}>
        Upload Requirements (Optional)
        <input
          type="file"
          hidden
          onChange={(e) => handleFileChange(e, 'requirements')}
        />
      </Button>
      {requirementsFile && (
        <Typography variant="body2">
          Requirements: {requirementsFile.name}
        </Typography>
      )}

      {error && <Typography color="error">{error}</Typography>}

      <Button
        variant="contained"
        color="secondary"
        onClick={handleSubmitFiles}
        disabled={!pythonFile || uploading}
        sx={{ margin: 1 }}
      >
        {uploading ? 'Uploading...' : 'Submit Files'}
      </Button>

      {fileId && (
        <Typography color="success">
          Upload successful! File ID: {fileId}
        </Typography>
      )}
      {fileId && (
        <>
          <Button
            variant="contained"
            color="error"
            onClick={handleClearServer}
            disabled={uploading}
            sx={{ margin: 1 }}
          >
            {uploading ? 'Clearing...' : 'Clear Server'}
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleInspectFunctions}
            disabled={uploading}
            sx={{ margin: 1 }}
          >
            Inspect Uploaded Functions
          </Button>
          {functions && (
            <Box sx={{ marginTop: 2 }}>
              <Typography variant="h6">Functions in Uploaded File:</Typography>
              <ul>
                {functions.map((func, index) => (
                  <li key={index}>
                    <Typography variant="body2">{func}</Typography>
                  </li>
                ))}
              </ul>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}

export default FileUploadComponent;
