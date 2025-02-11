import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Homepage from './home';

// Mock the import.meta.glob function
jest.mock('import.meta', () => ({
  glob: () => ({
    './docs/*.md': {
      './docs/example.md': () => Promise.resolve({ default: '# Example' }),
    },
  }),
}), { virtual: true });


describe('Homepage', () => {
  it('should render successfully', () => {
    const { baseElement } = render(
      <BrowserRouter>
        <Homepage />
      </BrowserRouter>
    );
    expect(baseElement).toBeTruthy();
  });
});
