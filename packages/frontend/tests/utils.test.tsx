import { checkURL, checkBatchConfig } from '../src/app/utils';
import '@testing-library/jest-dom';
import {
  MOCK_SCIKIT_API_URL,
  MOCK_FINBERT_API_URL,
  MOCK_FOLKTABLES_DATASET_API_URL,
  MOCK_FINANCIAL_DATASET_API_URL,
  MOCK_WIKI_DATASET_API_URL,
  MOCK_GEMINI_API_URL,
  MOCK_SCIKIT_REGRESSION_DATASET_URL,
  MOCK_SCIKIT_REGRESSOR_URL,
} from '../src/app/constants';

describe('checkURL function', () => {
  it('should return true for valid URLs', () => {
    const validUrls = [
      'https://www.example.com',
      'http://example.com',
      'https://subdomain.example.com/path/to/resource',
      'https://www.example.com:8080/path/to/resource',
      'https://example.co.uk',
      'http://example.com/?search=test#anchor',
      'https://www.example.com/path?query=value#fragment',
      MOCK_SCIKIT_API_URL,
      MOCK_FINBERT_API_URL,
      MOCK_FOLKTABLES_DATASET_API_URL,
      MOCK_FINANCIAL_DATASET_API_URL,
      MOCK_GEMINI_API_URL,
      MOCK_WIKI_DATASET_API_URL,
      MOCK_SCIKIT_REGRESSOR_URL,
      MOCK_SCIKIT_REGRESSION_DATASET_URL,

      // Prod
      'http://206.189.119.159:5011/predict',
      'http://206.189.119.159:5001/predict',
      'http://206.189.119.159:5010/fetch-datapoints',
      'http://206.189.119.159:5024/fetch-datapoints',
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

describe('checkBatchConfig function', () => {
  it('should return true for valid batch configurations', () => {
    const validConfigs = [
      { batchSize: 10, numberOfBatches: 100 }, // 10 * 100 = 1000
      { batchSize: 50, numberOfBatches: 200 }, // 50 * 200 = 10000
      { batchSize: 25, numberOfBatches: 40 }, // 25 * 40 = 1000
      { batchSize: 100, numberOfBatches: 50 }, // 100 * 50 = 5000
    ];

    validConfigs.forEach(({ batchSize, numberOfBatches }) => {
      expect(checkBatchConfig(batchSize, numberOfBatches)).toBe(true);
    });
  });

  it('should return false for invalid batch configurations', () => {
    const invalidConfigs = [
      { batchSize: 0, numberOfBatches: 100 }, // batchSize < 1
      { batchSize: 10, numberOfBatches: 0 }, // numberOfBatches < 1
      { batchSize: 5, numberOfBatches: 50 }, // 5 * 50 = 250 (less than 1000)
      { batchSize: 100, numberOfBatches: 101 }, // 100 * 101 = 10100 (greater than 10000)
      { batchSize: -10, numberOfBatches: 50 }, // Negative batchSize
      { batchSize: 50, numberOfBatches: -20 }, // Negative numberOfBatches
    ];

    invalidConfigs.forEach(({ batchSize, numberOfBatches }) => {
      expect(checkBatchConfig(batchSize, numberOfBatches)).toBe(false);
    });
  });
});
