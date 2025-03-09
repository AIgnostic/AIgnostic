"""This file contains the constants used in the report generation module."""

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
    "explainability": [
        "gradient explanations",
        "LIME",
        "SHAP",
        "identified feature importance",
        "explanation alignment",
        "explanation stability score",
        "explanation sparsity score",
        "explanation fidelity score",],
    "fairness": [
        "equal opportunity difference",
        "disparate impact",
        "statistical parity difference",
        "false negative rate difference",
        "true positive rate difference",
        "equalized odds difference",
        "negative predictive value",
        "positive predictive value",
        "roc auc",
    ],
    "uncertainity": [
        "ood auroc",
    ],
    "adversarial robustness": [
        # TODO: Implement metrics for adversarial robustness
    ],
    "privacy": [
        # TODO: Implement metrics for privacy
    ],
    "data minimality": [
        # TODO: Implement metrics for data minimality
    ],
}
