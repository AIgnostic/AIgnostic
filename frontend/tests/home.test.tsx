import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Homepage from '../src/app/home';
import { steps } from '../src/app/constants';
import '@testing-library/jest-dom';
import checkURL from '../src/app/utils';



describe('Stepper Navigation', () => {
  it('should go to the next step when "Next" button is clicked', () => {
    render(<Homepage />);
    
    expect(screen.getByText(steps[0].label)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    expect(screen.getByText(steps[1].label)).toBeInTheDocument();
  });

  it('should go to the previous step when "Back" button is clicked', () => {
    render(<Homepage />);
    
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    const backButton = screen.getAllByRole('button', { name: /Back/i })[0];  
    fireEvent.click(backButton);

    expect(screen.getByText(steps[0].label)).toBeInTheDocument();
  });
});
  

jest.mock('../src/app/utils', () => ({
    __esModule: true,
    default: jest.fn(), 
  }));
  

describe('Form Validation', () => {
  it('should show an error if the model URL is invalid', () => {
    (checkURL as jest.Mock).mockReturnValue(false);

    render(<Homepage />);

    fireEvent.change(screen.getByLabelText(/Model API URL/i), { target: { value: 'invalid-url' } });

    fireEvent.blur(screen.getByLabelText(/Model API URL/i));

    expect(screen.getByText('Invalid URL')).toBeInTheDocument();
  });

  it('should show an error if the dataset URL is invalid', () => {
    (checkURL as jest.Mock).mockReturnValue(false);
  
    render(<Homepage />);
  
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), { target: { value: 'invalid-dataset-url' } });
  
    fireEvent.blur(screen.getByLabelText(/Dataset API URL/i));
  
    expect(screen.getByText('Invalid URL')).toBeInTheDocument();
  });

  it('should navigate to the next step when URLs are valid', async () => {
    (checkURL as jest.Mock).mockReturnValue(true);
  
    render(<Homepage />);
  
    fireEvent.change(screen.getByLabelText(/Model API URL/i), { target: { value: 'http://valid-model-url.com' } });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), { target: { value: 'http://valid-dataset-url.com' } });
  
    fireEvent.click(screen.getByText('Next'));
  
    await screen.findByText(/Select the legislations that you want to comply with./i); // This ensures that the step is rendered
  
    expect(screen.getByText(/Select the legislations that you want to comply with./i)).toBeInTheDocument();
  });
});


describe('UI Components', () => {
  it('should render the homepage correctly', () => {
    render(<Homepage />);
    
    expect(screen.getByText(/AIgnostic Frontend/i)).toBeInTheDocument();
    
    expect(screen.getByText(/'GETTING STARTED'/i)).toBeInTheDocument();
    
    expect(screen.getByText('Back')).toBeInTheDocument();
  });

  it('should enable "Next" button when valid URLs are entered', () => {
    render(<Homepage />);

    fireEvent.change(screen.getByLabelText(/Model API URL/i), { target: { value: 'http://valid-model-url.com' } });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), { target: { value: 'http://valid-dataset-url.com' } });

    expect(screen.getByText('Next')).toBeEnabled();
  });
});  

describe('API Calls', () => {
  beforeEach(() => {
    // Mock fetch globally
    global.fetch = jest.fn();
  
    // Mock createObjectURL to avoid test errors
    global.URL.createObjectURL = jest.fn();

  });
  
  afterEach(() => {
    jest.resetAllMocks();
  });
  

  it('downloads a report on successful response from handleSubmit', async () => {
    // Mock a successful response from the API
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({ results: { metric1: 0.8, metric2: 0.9 } }),
    });
  
    // Spy on the click method for anchor elements
    const clickSpy = jest.spyOn(HTMLAnchorElement.prototype, 'click');
    
    render(<Homepage />);

  
    // Simulate entering valid URLs and navigating to the report generation step
    fireEvent.change(screen.getByLabelText(/Model API URL/i), { target: { value: 'http://valid-model-url.com' } });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), { target: { value: 'http://valid-dataset-url.com' } });
    fireEvent.click(screen.getAllByText('Next')[0]);
    fireEvent.click(screen.getAllByText('Next')[1]);
    fireEvent.click(screen.getAllByText('Next')[2]);
    fireEvent.click(screen.getByText('Generate Report'));
  
    // Check that API call was made
    // That a clickable link was created (creates a download link)
    // And that the link was clicked (i.e. the report was downloaded)
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(expect.any(String), expect.any(Object));
      expect(global.URL.createObjectURL).toHaveBeenCalled();
      expect(clickSpy).toHaveBeenCalled();
    });
  });

  it('displays an error message upon failure response from API call', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
      json: jest.fn().mockResolvedValue({ detail: 'Internal server error' }),
    });
  
    // Spy on ErrorMessage component
    // const errorMessageSpy = jest.spyOn(ErrorMessage, 'default');
    
    render(<Homepage />);

  
    // Simulate entering valid URLs and navigating to the report generation step
    fireEvent.change(screen.getByLabelText(/Model API URL/i), { target: { value: 'http://valid-model-url.com' } });
    fireEvent.change(screen.getByLabelText(/Dataset API URL/i), { target: { value: 'http://valid-dataset-url.com' } });
    fireEvent.click(screen.getAllByText('Next')[0]);
    fireEvent.click(screen.getAllByText('Next')[1]);
    fireEvent.click(screen.getAllByText('Next')[2]);
    fireEvent.click(screen.getByText('Generate Report'));
  
    
    // check that error message is displayed
    // with the correct error message
    await waitFor(() => {
      expect(screen.getByText('Error 500')).toBeInTheDocument();
      expect(screen.getByText('Internal server error')).toBeInTheDocument();
    });
    
  });
});