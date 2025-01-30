import React from 'react';
import { render, screen } from '@testing-library/react';
import APIDocs from '../src/app/api_docs';
import '@testing-library/jest-dom'
import CodeBox from '../src/app/components/CodeBox';


// Mock the 

jest.mock('@mui/material/Accordion', () => (props) => <div data-testid="mock-accordion" {...props} />);
jest.mock('@mui/material/AccordionSummary', () => (props) => <div data-testid="mock-accordion-summary" {...props} />);
jest.mock('@mui/material/AccordionDetails', () => (props) => <div data-testid="mock-accordion-details" {...props} />);
jest.mock('@mui/icons-material/ExpandMore', () => () => <div data-testid="mock-expand-more-icon" />);
jest.mock('react-markdown', () => ({ children, components }: any) => (
  <div data-testid="mock-markdown">{children}</div>
));
// jest.mock('../src/app/components/CodeBox', () => 'mock-code-box');
jest.mock('../src/app/components/CodeBox', () => ({ language, codeSnippet }: any) => (
  <div data-testid="mock-code-box">{language} - {codeSnippet}</div>
));
jest.mock('../src/app/home.styles', () => ({
  container: {},
  accordion: {},
  logoText: {},
}));
jest.mock('../src/app/constants', () => ({
  AIGNOSTIC: 'MockAIGNOSTIC',
}));

describe('APIDocs', () => {

  const mockGetMarkdownFiles = (): Record<string, string> => ({
    'file1.md': '# Title 1\nContent 1',
    'file2.md': '# Title 2\nContent 2\n',
    'file3.md': 'No title\nJust content',
  });

  it('renders correctly with markdown files', () => {
    render(<APIDocs getMarkdownFiles={mockGetMarkdownFiles} />);

    expect(screen.getByText('MockAIGNOSTIC | API Documentation')).toBeInTheDocument();
    expect(screen.getByText('Title 1')).toBeInTheDocument();
    expect(screen.getByText('Title 2')).toBeInTheDocument();
    expect(screen.getByText('No title found')).toBeInTheDocument();
  });

  it('renders markdown content correctly', () => {
    render(<APIDocs getMarkdownFiles={mockGetMarkdownFiles} />);

    const markdowns = screen.getAllByTestId('mock-markdown');
    expect(markdowns).toHaveLength(3);
    expect(markdowns[0].textContent).toBe('Content 1');
    expect(markdowns[1].textContent).toBe('Content 2\n');
    expect(markdowns[2].textContent).toBe('No title\nJust content');
  });

  it('handles empty markdown files', () => {
    const emptyMockGetMarkdownFiles = () => ({});
    render(<APIDocs getMarkdownFiles={emptyMockGetMarkdownFiles} />);

    expect(screen.getByText('MockAIGNOSTIC | API Documentation')).toBeInTheDocument();
    expect(screen.queryByTestId('mock-markdown')).not.toBeInTheDocument();
  });

  it('renders the accordion components', () => {
    render(<APIDocs getMarkdownFiles={mockGetMarkdownFiles} />);

    expect(screen.getAllByTestId('mock-accordion')).toHaveLength(3);
    expect(screen.getAllByTestId('mock-accordion-summary')).toHaveLength(3);
    expect(screen.getAllByTestId('mock-accordion-details')[0]).toHaveTextContent('Content 1');
    expect(screen.getAllByTestId('mock-accordion-details')[1]).toHaveTextContent('Content 2');
    expect(screen.getAllByTestId('mock-accordion-details')[2]).toHaveTextContent(/No title\s+Just content/);
  });
});
