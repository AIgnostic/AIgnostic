import isURL from 'validator/lib/isURL';
import jsPDF from 'jspdf';
import {
  MOCK_SCIKIT_API_URL,
  MOCK_FINBERT_API_URL,
  MOCK_FOLKTABLES_DATASET_API_URL,
  MOCK_FINANCIAL_DATASET_API_URL,
  MOCK_FINANCIAL_DATASET_API_URL_PROD,
  MOCK_FINBERT_API_URL_PROD,
  MOCK_FOLKTABLES_DATASET_API_URL_PROD,
  MOCK_SCIKIT_API_URL_PROD,
  BACKEND_FETCH_METRIC_INFO_URL,
  MOCK_WIKI_DATASET_API_URL,
  MOCK_GEMINI_API_URL,
  MOCK_SCIKIT_REGRESSOR_URL,
  MOCK_SCIKIT_REGRESSION_DATASET_URL,
  MOCK_SCIKIT_REGRESSOR_URL_PROD,
  MOCK_SCIKIT_REGRESSION_DATASET_URL_PROD,
} from './constants';

async function fetchMetricInfo(): Promise<TaskToMetricMap> {
  try {
    const response = await fetch(BACKEND_FETCH_METRIC_INFO_URL);
    const data: MetricInfo = await response.json();
    return data.task_to_metric_map;
  } catch (error) {
    console.error('Error:', error);
    throw error; // Rethrow the error so the caller can handle it
  }
}
function checkURL(url: string): boolean {
  const validURLS = [
    MOCK_SCIKIT_API_URL,
    MOCK_FINBERT_API_URL,
    MOCK_FOLKTABLES_DATASET_API_URL,
    MOCK_FINANCIAL_DATASET_API_URL,
    MOCK_SCIKIT_REGRESSOR_URL,
    MOCK_SCIKIT_REGRESSION_DATASET_URL,
    "http://localhost:5001/predict",
    "http://localhost:5024/fetch-datapoints",
    "http://localhost:9001/predict",
    "http://localhost:5025/fetch-datapoints",
    // localhost scikit regressor instances
    "http://localhost:5012/predict",
    "http://localhost:5013/fetch-datapoints",
    // Prod
    MOCK_SCIKIT_API_URL_PROD,
    MOCK_FINBERT_API_URL_PROD,
    MOCK_FOLKTABLES_DATASET_API_URL_PROD,
    MOCK_FINANCIAL_DATASET_API_URL_PROD,
    MOCK_GEMINI_API_URL,
    MOCK_WIKI_DATASET_API_URL,
    MOCK_SCIKIT_REGRESSOR_URL_PROD,
    MOCK_SCIKIT_REGRESSION_DATASET_URL_PROD,
  ];
  if (validURLS.includes(url)) {
    return true;
  }
  if (url === '') {
    return false;
  }
  // allow urls from
  try {
    if (!isURL(url) || url.includes('%20')) {
      throw new Error('Invalid URL ');
    }
    new URL(url); // If the URL is valid, this will not throw an error
    return true;
  } catch (e) {
    console.log(e + url);
    return false; // If an error is thrown, the URL is invalid
  }
}
function checkBatchConfig(batchSize: number, numberOfBatches: number): boolean {
  // Check batchSize and numberOfBatches greater than 1
  if (batchSize < 1 || numberOfBatches < 1) {
    return false;
  }
  const totalSampleSize = batchSize * numberOfBatches;
  return 1000 <= totalSampleSize && totalSampleSize <= 10000;
}
// retrieves a dictionary mapping task types to the metrics that can be computed for them
// returns a dictionary with the following structure:
// {
//     "binary_classification": ["metric_1", "metric_2", ...],
//     "multi_class_classification": ["metric_1", "metric_2", ...],
//     "regression": ["metric_1", "metric_2", ...],
//     ...
// }
export interface TaskToMetricMap {
  [taskType: string]: string[];
}
export interface MetricInfo {
  task_to_metric_map: TaskToMetricMap;
}
function applyStyle(doc: jsPDF, style: any) {
  doc.setFont(style.font, style.style);
  doc.setFontSize(style.size);
}
export { checkURL, checkBatchConfig, applyStyle, fetchMetricInfo };