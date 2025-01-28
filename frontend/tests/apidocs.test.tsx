import React from 'react';
import { render, screen } from '@testing-library/react';
import APIDocs from '../src/app/api_docs';
import '@testing-library/jest-dom'

// Mock the dependencies
jest.mock('@mui/material/Accordion', () => 'mock-accordion');
jest.mock('@mui/material/AccordionSummary', () => 'mock-accordion-summary');
jest.mock('@mui/material/AccordionDetails', () => 'mock-accordion-details');
jest.mock('@mui/icons-material/ExpandMore', () => 'mock-expand-more-icon');
jest.mock('react-markdown', () => ({ children, components }: any) => (
  <div data-testid="mock-markdown">{children}</div>
));
jest.mock('../src/app/components/CodeBox', () => 'mock-code-box');
jest.mock('../src/app/home.styles', () => ({
  container: {},
  accordion: {},
  logoText: {},
}));
jest.mock('../src/app/constants', () => ({
  AIGNOSTIC: 'MockAIGNOSTIC',
}));

describe('APIDocs', () => {
  const mockGetMarkdownFiles = () => ({
    'file1.md': { content: '# Title 1\nContent 1' },
    'file2.md': { content: '# Title 2\nContent 2\n``````' },
    'file3.md': { content: 'No title\nJust content' },
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
    expect(markdowns[1].textContent).toBe('Content 2\nprint("Hello")\n');
    expect(markdowns[2].textContent).toBe('No title\nJust content');
  });

  it('handles empty markdown files', () => {
    const emptyMockGetMarkdownFiles = () => ({});
    render(<APIDocs getMarkdownFiles={emptyMockGetMarkdownFiles} />);

    expect(screen.getByText('MockAIGNOSTIC | API Documentation')).toBeInTheDocument();
    expect(screen.queryByTestId('mock-markdown')).not.toBeInTheDocument();
  });
});
