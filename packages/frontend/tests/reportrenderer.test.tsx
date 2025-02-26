import React from 'react';
import { render } from '@testing-library/react';
import ReportRenderer from '../src/app/components/ReportRenderer'; // Adjust path as needed
import { Report } from '../src/app/types';


jest.mock('@react-pdf/renderer', () => ({
    Document: ({ children }: any) => <div>{children}</div>,
    Page: ({ children }: any) => <div>{children}</div>,
    Text: ({ children }: any) => <span>{children}</span>,
    View: ({ children }: any) => <div>{children}</div>,
    StyleSheet: { create: (styles: any) => styles },
  }));

  
describe('ReportRenderer', () => {
    const sampleReport: Report = {
        info: {
            model_name: 'Test Model',
            evaluation_date: '2025-02-24',
            dataset: 'Sample Dataset',
        },
        properties: [
            {
                property: 'Fairness',
                computed_metrics: [
                    {
                        metric: 'Bias Score',
                        value: '0.12',
                        ideal_value: '0.0',
                        range: ['0.0', '1.0']
                    },
                    {
                        metric: 'Demographic Parity',
                        value: '0.87',
                        ideal_value: '1.0',
                        range: ['0.0', '1.0']
                    }
                ],
                legislation_extracts: [
                    { article_number: 5, 
                     article_title: 'Fair AI Act', 
                     description: 'AI systems must be unbiased.', 
                     suitable_recitals: ['Recital 1', 'Recital 2']}
                ],
                llm_insights: ['This model demonstrates low bias but needs further evaluation.']
            }
        ]
    };

    it("renders without crashing", () => {
        render(<ReportRenderer report={sampleReport} />);
    });

    it('renders the report title', () => {
        const { getByText } = render(<ReportRenderer report={sampleReport} />);
        expect(getByText('AIgnostic | Final Report')).toBeTruthy();
    });

    it('renders general info', () => {
        const { getByText } = render(<ReportRenderer report={sampleReport} />);
        expect(getByText('Model Name: Test Model')).toBeTruthy();
        expect(getByText('Evaluation Date: 2025-02-24')).toBeTruthy();
        expect(getByText('Dataset: Sample Dataset')).toBeTruthy();
    });

    it('renders property sections correctly', () => {
        const { getByText, getAllByText } = render(<ReportRenderer report={sampleReport} />);
        expect(getByText('Fairness')).toBeTruthy();
        expect(getByText('Computed Metrics')).toBeTruthy();

        expect(getByText('• Bias Score: 0.12')).toBeTruthy();
        expect(getByText('• Ideal Value: 0.0')).toBeTruthy();

        expect(getByText('• Demographic Parity: 0.87')).toBeTruthy();
        expect(getByText('• Ideal Value: 1.0')).toBeTruthy();

        const rangeElements = getAllByText('• Range: 0.0 - 1.0');
        expect(rangeElements.length).toBe(2);

        expect(getByText('Relevant Legislation Extracts')).toBeTruthy();
        expect(getByText('• Article 5 [Fair AI Act]: AI systems must be unbiased.')).toBeTruthy();
        expect(getByText('LLM Insights')).toBeTruthy();
        expect(getByText('This model demonstrates low bias but needs further evaluation.')).toBeTruthy();
        // Check if suitable recitals are rendered
        // TODO: Render rectals if needed
        // expect(getByText('Recital 1')).toBeTruthy();
        // expect(getByText('Recital 2')).toBeTruthy();
    });
});
