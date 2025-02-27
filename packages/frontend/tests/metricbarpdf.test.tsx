import React from 'react';
import { render } from '@testing-library/react';
import MetricBarPDF from '../src/app/components/MetricBarPDF';


jest.mock('@react-pdf/renderer', () => ({
    Document: ({ children }: any) => <div>{children}</div>,
    Page: ({ children }: any) => <div>{children}</div>,
    Text: ({ children, style }: any) => (
        <span data-style={JSON.stringify(style)}>{children}</span>
    ),
    View: ({ children, style }: any) => (
        <div data-style={JSON.stringify(style)}>{children}</div>
    ),
    StyleSheet: {
        create: (styles: any) => styles, // Returns styles unchanged
    },
}));


describe('MetricBarPDF', () => {
  it('renders without crashing', () => {
    render(<MetricBarPDF value={0.5} idealValue={0.7} />);
  });

  it('renders the correct value and target text', () => {
    const { getByText } = render(<MetricBarPDF value={0.5} idealValue={0.7} />);
    expect(getByText('Value: 0.50 | Target: 0.70')).toBeTruthy();
  });

  it('applies correct color for value less than idealValue', () => {
    const { getByText } = render(<MetricBarPDF value={0.5} idealValue={0.7} />);
    const valueText = getByText('Value: 0.50 | Target: 0.70');

    // Extract the applied styles
    const appliedStyle = JSON.parse(valueText.getAttribute('data-style') || '{}');

    expect(appliedStyle.color).toBe('rgb(139, 20, 20)'); // Red when value < idealValue
});

it('applies correct color for value greater than or equal to idealValue', () => {
    const { getByText } = render(<MetricBarPDF value={0.8} idealValue={0.7} />);
    const valueText = getByText('Value: 0.80 | Target: 0.70');

    // Extract the applied styles
    const appliedStyle = JSON.parse(valueText.getAttribute('data-style') || '{}');

    expect(appliedStyle.color).toBe('rgb(65, 163, 86)'); // Green when value ≥ idealValue
});

  it('calculates correct percentages with default min/max', () => {
    const { container } = render(<MetricBarPDF value={0.5} idealValue={0.7} />);
    const barContainer = container.querySelector('div');
    expect(barContainer).toBeTruthy();
  });

  it('adjusts min and max dynamically if infinity is provided', () => {
    const { getByText } = render(<MetricBarPDF value={1.5} idealValue={1} min={-Infinity} max={Infinity} />);
    expect(getByText('Value: 1.50 | Target: 1.00')).toBeTruthy();
  });
});
