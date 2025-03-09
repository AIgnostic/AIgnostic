import { useState } from 'react';
import { Button, Box, Typography, Chip } from '@mui/material';
import theme from '../theme';
import { USER_METRICS_SERVER_URL } from '../constants';
import { HomepageState } from '../types';
import { useUser } from '../context/userid.context';

interface FileUploadComponentProps {
  state: HomepageState & { dashboardKey: number }; // Replace 'any' with the appropriate type
  setStateWrapper: <K extends keyof (HomepageState & { dashboardKey: number })>(
    key: K,
    value: (HomepageState & { dashboardKey: number })[K]
  ) => void;
}
function FileUploadComponent({
  state,
  setStateWrapper,
}: FileUploadComponentProps) {
  const [pythonFile, setPythonFile] = useState<File | null>(null);
  const [requirementsFile, setRequirementsFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [functions, setFunctions] = useState<string[] | null>(null);

  const { userId } = useUser();

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    fileType: 'python' | 'requirements'
  ) => {
    const file = event.target.files?.[0] || null;
    if (fileType === 'python' && file?.name.endsWith('.py')) {
      setPythonFile(file);
    } else if (fileType === 'requirements' && file?.name.endsWith('.txt')) {
      setRequirementsFile(file);
    } else {
      setError('Invalid file type. Please upload a .py or .txt file.');
    }
    setError(null);
  };

  const handleSubmitFiles = async () => {
    if (!userId) {
      setError('User ID not found. Please log in.');
      return;
    }
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
        `${USER_METRICS_SERVER_URL}/upload-metrics-and-dependencies?user_id=${userId}`,
        { method: 'POST', body: formData }
      );

      if (!response.ok)
        throw new Error(
          (await response.json()).detail || `Error ${response.status}`
        );

      setFunctions([]);
      console.log('Files uploaded successfully:', await response.json());
    } catch (error) {
      setError(`Upload failed: ${(error as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleClearUserData = async () => {
    if (!userId) {
      setError('User ID not found. Please log in.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await fetch(
        `${USER_METRICS_SERVER_URL}/clear-user-data/${userId}`,
        { method: 'DELETE' }
      );
      if (!response.ok)
        throw new Error(
          (await response.json()).detail || `Error ${response.status}`
        );
      setPythonFile(null);
      setRequirementsFile(null);
      setFunctions(null);
    } catch (error) {
      setError(`Clearing user data failed: ${(error as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleInspectFunctions = async () => {
    if (!userId) {
      setError('User ID not found. Please log in.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await fetch(
        `${USER_METRICS_SERVER_URL}/inspect-uploaded-functions/${userId}`,
        { method: 'GET' }
      );
      if (!response.ok)
        throw new Error(
          (await response.json()).detail || `Error ${response.status}`
        );
      const data = await response.json();
      setFunctions(data.functions);
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
        backgroundColor: theme.palette.background.default,
        border: `1px solid ${theme.palette.background.paper}`,
        borderRadius: 2,
        margin: 2,
        boxShadow: theme.shadows[3],
      }}
    >
      <Typography variant="h6">Upload Your Metrics</Typography>
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
        }}
      >
        <Button variant="contained" component="label" sx={{ margin: 1 }}>
          Upload Python File
          <input
            type="file"
            hidden
            onChange={(e) => handleFileChange(e, 'python')}
          />
        </Button>
        {pythonFile && (
          <Typography variant="body2">
            Python File: {pythonFile.name}
          </Typography>
        )}
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
        }}
      >
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
      </div>
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

      {functions && (
        <>
          <Button
            variant="contained"
            color="error"
            onClick={handleClearUserData}
            disabled={uploading}
            sx={{ margin: 1 }}
          >
            {uploading ? 'Clearing...' : 'Clear Data'}
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
          {functions && functions.length > 0 && (
            <Box
              sx={{
                marginTop: 2,
                bgcolor: theme.palette.background.default,
                padding: 2,
                p: 2,
                border: `1px solid ${theme.palette.background.paper}`,
                shadow: 3,
                elevation: 4,
                boxShadow: theme.shadows[3],
                borderRadius: 2,
              }}
            >
              <Typography variant="h6">Functions in Uploaded File:</Typography>
              {functions.map((func, index) => (
                <Chip
                  key={index}
                  label={func}
                  variant="filled"
                  color={'secondary'}
                  style={{ margin: '5px' }}
                />
              ))}
            </Box>
          )}
        </>
      )}
    </Box>
  );
}

export default FileUploadComponent;
