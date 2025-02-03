const AIGNOSTIC = "AIgnostic";
const HOME = "/AIgnostic";

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

  const generalMetrics = ['Accuracy', 'Precision', 'Recall'];
  
  const modelTypesToMetrics: { [key: string]: string[] } = {
    'Classification': ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC'],
    'Regression': ['Mean Absolute Error', 'Mean Squared Error', 'R-squared', 'Root Mean Squared Error'],
    'Binary Classifier': ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC', 'Confusion Matrix'],
    'General (Accuracy, Precision, Recall)': generalMetrics,
  };

  export { steps, BACKEND_URL, AIGNOSTIC, HOME, modelTypesToMetrics, generalMetrics};