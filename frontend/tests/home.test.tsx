import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
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
  