import { useNavigate } from 'react-router-dom';
import { Button } from '@mui/material';

export type MarkdownFiles = Record<string, string>;

export interface ReportSection {
  property: string;
  computed_metrics: { metric: string; result: string }[];
  legislation_extracts: LegislationExtract[];
  llm_insights: any[]; // TODO: Define this type, refactor llm to only pass back content
}

export interface LegislationExtract {
  article_number: number;
  article_title: string;
  description: string;
  suitable_recitals: string[];
}

export interface Metric {
  [metricName: string]: number;
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
  activeStep: number;
  selectedItem: string;
  metricChips: { id: string; label: string; selected: boolean }[];
  metricsHelperText: string;
  selectedModelType: string;
  error: boolean;
  errorMessage: { header: string; text: string };
  showDashboard: boolean;
  isGeneratingReport: boolean;
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
