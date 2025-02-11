import { checkURL }from '../src/app/utils';
import '@testing-library/jest-dom';
import jsPDF from 'jspdf';
import { applyStyle } from '../src/app/utils';
import { reportStyles } from '../src/app/home.styles';
import { generateReportText } from '../src/app/utils';
describe('checkURL function', () => {
  it('should return true for valid URLs', () => {
    const validUrls = [
      'https://www.example.com',
      'http://example.com',
      'ftp://ftp.example.com',
      'https://subdomain.example.com/path/to/resource',
      'https://www.example.com:8080/path/to/resource',
      'https://example.co.uk',
      'http://example.com?search=test#anchor',
      'https://192.168.1.1',
      'https://www.example.com/path?query=value#fragment',
    ];

    validUrls.forEach((url) => {
      expect(checkURL(url)).toBe(true);
    });
  });

  it('should return false for invalid URLs', () => {
    const invalidUrls = [
      'htp://www.example.com', // Protocol typo
      '://www.example.com', // Missing protocol
      'http://', // Missing domain
      'http://256.256.256.256', // Invalid IP address format
      'www.example.com', // Missing protocol
      'http://example..com', // Double dots in domain
      'http://-example.com', // Domain starts with a hyphen
      'http://example#.com', // Invalid character in domain
      'ftp://.example.com', // Domain starts with a dot
      'http://%20example.com', // Invalid percent-encoded space
      '', // Empty string
    ];

    invalidUrls.forEach((url) => {
      expect(checkURL(url)).toBe(false);
    });
  });
});

describe('applyStyle', () => {
  it('should apply the correct font, style, and size to the jsPDF document', () => {
    const doc = new jsPDF();
    const style = reportStyles.title;

    const setFontSpy = jest.spyOn(doc, 'setFont');
    const setFontSizeSpy = jest.spyOn(doc, 'setFontSize');

    // Apply styles
    applyStyle(doc, style);

    // Check if setFont and setFontSize were called with the correct arguments
    expect(setFontSpy).toHaveBeenCalledWith(style.font, style.style);
    expect(setFontSizeSpy).toHaveBeenCalledWith(style.size);
  });
});

jest.mock('jspdf', () => {
  const mockJsPDF = jest.fn().mockImplementation(() => {
    return {
      save: jest.fn(),
      text: jest.fn(),
      setFontSize: jest.fn(),
      setFont: jest.fn(),
    };
  });
    return mockJsPDF;
});

describe('generateReportText', () => {
  it('check doc generateReport text calls the mocked methods', () => {
    const results = [
      {
        metric: 'Metric 1',
        result: 'Result 1',
        legislation_results: ['Legislation 1'],
        llm_model_summary: ['Summary 1'],
      },
      {
        metric: 'Metric 2',
        result: 'Result 2',
        legislation_results: ['Legislation 2'],
        llm_model_summary: ['Summary 2'],
      },
    ];

    const doc = generateReportText(results);
        
    // Optionally check that the doc is using the mocked methods
    expect(doc.text).toHaveBeenCalled();
    expect(doc.setFont).toHaveBeenCalled();
  });
});
