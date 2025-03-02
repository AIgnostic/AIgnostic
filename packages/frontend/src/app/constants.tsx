import { ConditionAlertFailure, HomepageState } from './types';

const AIGNOSTIC = 'AIgnostic';
const HOME = '/AIgnostic';

const MOCK_SCIKIT_API_URL = 'http://scikit-mock-model-api:5001/predict';
const MOCK_FINBERT_API_URL = 'http://finbert-mock-model-api:5001/predict';
const MOCK_FOLKTABLES_DATASET_API_URL = 'http://folktables-dataset-api:5000/fetch-datapoints';
const MOCK_FINANCIAL_DATASET_API_URL = 'http://financial-dataset-api:5050/fetch-datapoints';

const steps = [
  {
    label: 'Enter model and dataset API URLs',
    description: `Enter the URLs for your model and dataset APIs to get started.
                    For more information about creating the APIs, see the documentation - click 'Getting Started'.`,
  },
  {
    label: 'Select Model Type',
    description: `Select the type of model you are using.`,
  },
  {
    label: 'Select Legislation',
    description: `Select the legislations that you want to comply with.`,
  },
  {
    label: 'Select Metrics',
    description: `Select the metrics you want to analyze your model with. 
         These will be used to quantify your compliance score with your selected metrics.`,
  },
  {
    label: 'Summary and Generate Report',
    description: `Check that you are happy with your selections and generate your compliance report.
                    Report generation may take some time.`,
  },
];

const BACKEND_URL = 'http://localhost:8000/evaluate';
const RESULTS_URL = 'http://localhost:5002/results';

const generalMetrics = ['Accuracy', 'Precision', 'Recall'];

const binaryClassifierMetrics = ["accuracy",
"precision",
"recall",
"f1 score",
// "roc auc",
"statistical parity difference",
"equal opportunity difference",
"equalized odds difference",
"disparate impact",
"false negative rate difference",
"negative predictive value",
"positive predictive value",
"true positive rate difference",
// "explanation stability score",
// "explanation sparsity score",
// "explanation fidelity score",
// "ood auroc"
]

const multiClassClassifierMetrics = [
  "accuracy",
  "precision",
  "recall",
  "f1 score",
  // "roc auc",
  // "explanation stability score",
  // "explanation sparsity score",
  // "explanation fidelity score",
  // "ood auroc",
]

const regressionMetrics = [
  "mean absolute error",
  "mean squared error",
  "r squared",
]

const nextTokenGenerationMetrics: string[] = []

const modelTypesToMetrics: { [key: string]: string[] } = {
  "Binary Classification": binaryClassifierMetrics,
  "Multi Class Classification": multiClassClassifierMetrics,
  "Regression": regressionMetrics,
  "Next Token Generation" : nextTokenGenerationMetrics,
  // 'General (Accuracy, Precision, Recall)': generalMetrics,
};

/*
  These conditions indicate the requirements for the user to proceed the next step
  i.e. we can only proceed to the next step if the given conditions are met
  
  This is a map from the step number to the requirements at that stage. If the number does not
  exist in the map, then proceeding to the next step is default behaviour.
  */
const activeStepToInputConditions: { [key: number]: ConditionAlertFailure } = {
  0: {
    pred: (state: HomepageState) =>
      state.isDatasetURLValid && state.isModelURLValid,
    error_msg: 'One or both URLs are invalid. Please provide valid URLs.',
  },
  1: {
    pred: (state: HomepageState) => state.selectedModelType !== '',
    error_msg: 'Please select a model type.',
  },
  3: {
    pred: (state: HomepageState) => state.metricChips.length > 0,
    error_msg: 'Please select at least one metric.',
  },
};

export {
  steps,
  BACKEND_URL,
  RESULTS_URL,
  MOCK_SCIKIT_API_URL,
  MOCK_FINBERT_API_URL,
  MOCK_FOLKTABLES_DATASET_API_URL,
  MOCK_FINANCIAL_DATASET_API_URL,
  AIGNOSTIC,
  HOME,
  modelTypesToMetrics,
  generalMetrics,
  activeStepToInputConditions,
};
