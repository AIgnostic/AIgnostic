import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SelectModelType from '../src/app/components/SelectModelType';

describe('SelectModelType Component', () => {
    const defaultProps = {
        state: {
            metricsHelperText: 'Test helper text',
            selectedModelType: 'model_a',
        },
        metricsHelperText: 'Test helper text',
        modelTypesToMetrics: {
            model_a: ['metric1', 'metric2'],
            advanced_model_b: ['metric3'],
        },
        handleModelTypeChange: jest.fn(),
        setStateWrapper: jest.fn(),
    };

    beforeEach(() => {
        defaultProps.handleModelTypeChange.mockClear();
        defaultProps.setStateWrapper.mockClear();
    });

    test('renders helper text in red', () => {
        render(<SelectModelType {...defaultProps} />);
        const helperText = screen.getByText('Test helper text');
        expect(helperText).toBeInTheDocument();
        expect(helperText).toHaveStyle('color: red');
    });

    test("renders radio group with legend 'Select Model Type'", () => {
        render(<SelectModelType {...defaultProps} />);
        expect(screen.getByText('Select Model Type')).toBeInTheDocument();
    });

    test('renders radio buttons with correctly formatted labels', () => {
        render(<SelectModelType {...defaultProps} />);
        // "model_a" should become "Model A"
        const modelARadio = screen.getByLabelText('Model A');
        expect(modelARadio).toBeInTheDocument();

        // "advanced_model_b" should become "Advanced Model B"
        const advancedModelRadio = screen.getByLabelText('Advanced Model B');
        expect(advancedModelRadio).toBeInTheDocument();
    });

    test('the selected model radio is checked', () => {
        render(<SelectModelType {...defaultProps} />);
        const selectedRadio = screen.getByDisplayValue('model_a');
        expect(selectedRadio).toBeChecked();
    });

    test('calls handleModelTypeChange and setStateWrapper when a different radio is selected', () => {
        render(<SelectModelType {...defaultProps} />);
        const advancedModelRadio = screen.getByLabelText('Advanced Model B');
        fireEvent.click(advancedModelRadio);
        expect(defaultProps.handleModelTypeChange).toHaveBeenCalledWith('advanced_model_b');
        expect(defaultProps.setStateWrapper).toHaveBeenCalledWith('selectedModelType', 'advanced_model_b');
    });
});
