import pydantic
from pydantic import BaseModel

legislation_type = ["GDPR", "EU"]
  
property_to_regulations = {
    "adversarial robustness": ["15"],
    "explainability": ["13",
                       "14"],
    "fairness": ["10",
                 "15"],
    "uncertainity": ["13"],
    "privacy": ["2"],
    "data minimality": ["10"],
}

property_to_metrics = {
    "adversarial robustness": ["fast gradient sign method",
                               "projected gradient descent"],
    "explainability": ["gradient explanations",
                       "LIME",
                       "SHAP",
                       "identified feature importance",
                       "explanation alignment",
                       "explanation stability score",
                       "explanation sparsity score",
                       "explanation fidelity score",],
    "fairness": ["equal opportunity difference",
                 "disparate impact",
                 "statistical parity difference",
                 "false negative rate difference",
                 "true positive rate difference",
                 "equalized odds difference",
                 "negative predictive value",
                 "positive predictive value"],
    "uncertainity": ["OOD",
                     "roc auc"],
    "privacy": ["prediction privacy scores"],
    "data minimality": ["from paper"],
}
