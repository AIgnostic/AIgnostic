import jsPDF from 'jspdf';
import {
  BACKEND_FETCH_METRIC_INFO_URL,
  MOCK_WIKI_DATASET_API_URL,
  MOCK_GEMINI_API_URL,
  MOCK_SCIKIT_REGRESSOR_URL,
  MOCK_SCIKIT_REGRESSION_DATASET_URL,
  MOCK_SCIKIT_REGRESSOR_URL_PROD,
  MOCK_SCIKIT_REGRESSION_DATASET_URL_PROD,
} from './constants';

const MIN_SAMPLE_SIZE = 1000;
const MAX_SAMPLE_SIZE = 10000;

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

function checkValidURL(str: string): boolean {
  const regex = /^(https?:\/\/)?(([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*)(\.[a-zA-Z]{2,})?|([0-9]{1,3}\.){3}[0-9]{1,3})(:\d+)?(\/[^\s]*)?$/;
  if (!regex.test(str)) {
    return false;
  }

  let url;
  try {
    url = new URL(str);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (_) {
    return false;
  }

  return url.protocol === "http:" || url.protocol === "https:";
}
function checkBatchConfig(batchSize: number, numberOfBatches: number): boolean {
  if (batchSize < 1 || numberOfBatches < 1) {
    return false;
  }
  const totalSampleSize = batchSize * numberOfBatches;
  return MIN_SAMPLE_SIZE <= totalSampleSize && totalSampleSize <= MAX_SAMPLE_SIZE;
}
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

export { checkValidURL as checkURL, checkBatchConfig, applyStyle, fetchMetricInfo };
