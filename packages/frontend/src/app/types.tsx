import { useNavigate } from 'react-router-dom';
import { Button } from '@mui/material';

export type MarkdownFiles = Record<string, string>;

export interface ReportPropertySection {
  property: string;
  computed_metrics: {
    metric: string;
    ideal_value: string;
    range: (string | null)[]; // nulls represent infinities
    value: string;
  }[];
  legislation_extracts: LegislationExtract[];
  llm_insights: string[];
}

export interface Report {
  info: { [key: string]: any };
  properties: ReportPropertySection[];
}

export interface LegislationExtract {
  article_number: number;
  article_title: string;
  link: string;
  description: string;
  suitable_recitals: string[];
}

export interface Metric {
  [metricName: string]: {
    value: string;
    ideal_value: string;
    range: (string | null)[];
    error: string | null;
  };
}

export type ConditionAlertFailure = {
  pred: (state: HomepageState) => boolean;
  error_msg: string;
};

export interface HomepageState {
  modelURL: string;
  datasetURL: string;
  modelAPIKey: string;
  datasetAPIKey: string;
  isModelURLValid: boolean;
  isDatasetURLValid: boolean;
  batchSize: number;
  numberOfBatches: number;
  isBatchConfigValid: boolean;
  maxConcurrentBatches: number;
  isMaxConcurrentBatchesValid: boolean;
  activeStep: number;
  selectedItem: string;
  metricChips: { id: string; label: string; selected: boolean }[];
  legislationChips: { id: string; label: string; selected: boolean }[];
  metricsHelperText: string;
  selectedModelType: string;
  error: boolean;
  errorMessage: { header: string; text: string };
  showDashboard: boolean;
  isGeneratingReport: boolean;
  userMetricsUploaded: boolean;
  userRequirementsUploaded: boolean;
}

/*
BackButton component and props interface that navigates back to the previous page when clicked.
*/
interface BackButtonProps {
  onClick?: () => void;
  className?: string;
}

export const BackButton: React.FC<BackButtonProps> = ({
  onClick,
  className,
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    console.log('handleClick triggered');
    console.log('onClick exists:', !!onClick);
    onClick?.();
    navigate(-1);
  };

  return (
    <Button onClick={handleClick} className={className} variant="contained">
      Back
    </Button>
  );
};
