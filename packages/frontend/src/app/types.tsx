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
  legislation_extracts: LegislationExtract[][];
  llm_insights: string[];
}

// legislation_extracts: 
// {article_type: 'gdpr', article_number: '15', article_title: 'Right of access by the data subject', link: 'https://gdpr-info.eu/art-15-gdpr', description: 'The data subject shall have the right to obtain fr…versely affect the rights and freedoms of others.', …}
// length
// : 
// 1
// [[Prototype]]
// : 
// Array(0)
// 1
// : 
// Array(1)
// 0
// : 
// {article_type: 'eu_ai', article_number: '15', article_title: 'Accuracy, robustness and cybersecurity', link: 'https://ai-act-law.eu/article/15/', description: 'High-risk AI systems shall be designed and develop…evasion), confidentiality attacks or model flaws.', …}
// length
// : 
// 1
// [[Prototype]]
// : 
// Array(0)
// length
// : 
// 2
// [[Prototype]]
// : 
// Array(0)
// llm_insights
// : 
// Array(1)
// 0
// : 
// "The most relevant legislation extract is Article 15 of the EU AI Act, which mandates that high-risk AI systems achieve appropriate levels of robustness and cybersecurity throughout their lifecycle. This explicitly includes resilience against adversarial examples, data poisoning, and model poisoning. While GDPR Article 15 focuses on data subject rights to access information about processing and automated decision-making logic, it indirectly relates to robustness by emphasizing the need for meaningful information about the logic involved in processing personal data. A system vulnerable to adversarial attacks could be argued to have an unreliable or opaque logic, potentially hindering the data subject's understanding of processing.\n\nGiven the absence of computed metrics for adversarial robustness, a definitive assessment of the LLM's 'goodness' and legal compliance is not possible. However, the EU AI Act clearly necessitates a focus on adversarial robustness for high-risk AI systems.  Demonstrating and ensuring resilience against adversarial attacks is crucial for compliance with Article 15 of the EU AI Act.  Furthermore, while not a direct requirement of GDPR Article 15, ensuring robustness contributes to the overall transparency and reliability of the system's decision-making processes, which is implicitly important for upholding data subject rights related to understanding automated processing.  Therefore, evaluating and improving adversarial robustness is a key step towards legal compliance, particularly under the EU AI Act, and building trustworthy AI systems."
// length
// : 
// 1
// [[Prototype]]
// : 
// Array(0)
// property
// : 
// "adversarial robustness"
export interface Report {
  info: { [key: string]: any };
  properties: ReportPropertySection[];
}

export interface LegislationExtract {
  article_number: number;
  article_title: string;
  article_type: string;
  link: string;
  description: string;
  suitable_recitals: string[];
}

export interface LegislationExtracts {
  legislation: LegislationExtract[];
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
