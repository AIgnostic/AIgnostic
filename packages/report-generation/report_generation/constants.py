"""This file contains the constants used in the report generation module."""

property_to_regulations = {
    "explainability": [
        "13",
        "14"
    ],
    "fairness": [
        "10",
        "15"
    ],
    "adversarial robustness": ["15"],
    "uncertainty": ["13"],
    "privacy": ["2"],
    "data minimality": ["10"],
}

property_to_metrics = {
    "fairness": [
        "accuracy",
        "precision",
        "recall",
        "f1 score",
        "equal opportunity difference",
        "disparate impact",
        "statistical parity difference",
        "false negative rate difference",
        "true positive rate difference",
        "equalized odds difference",
        "negative predictive value",
        "positive predictive value",
        "roc auc",
        "mean absolute error",
        "mean squared error",
        "r squared",
    ],
    "explainability": [
        "explanation stability score",
        "explanation sparsity score",
        "explanation fidelity score",
    ],
    "uncertainty": [
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
