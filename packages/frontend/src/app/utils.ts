import jsPDF from 'jspdf';
import {
  BACKEND_FETCH_METRIC_INFO_URL,
  AGGREGATOR_SERVER_URL,
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

async function fetchLegislationInfo(): Promise<LegislationList> {
  try {
    console.log('fetching legislation info');
    const response = await fetch(AGGREGATOR_SERVER_URL);
    console.log('fetched legislation info');
    console.log("response", response);
    const data: LegislationList = await response.json();
    console.log("data", data);
    if (!data.legislation) {
      throw new Error('No legislation found');
    }
    console.log('acquired legislation info');
    return { legislation: data.legislation };
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

export interface LegislationList {
  legislation: string[];
}
function applyStyle(doc: jsPDF, style: any) {
  doc.setFont(style.font, style.style);
  doc.setFontSize(style.size);
}

export { checkValidURL as checkURL, checkBatchConfig, applyStyle, fetchMetricInfo, fetchLegislationInfo };
