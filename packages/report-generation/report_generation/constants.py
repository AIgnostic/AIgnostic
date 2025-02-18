property_to_regulations = {
    "adversarial robustness": ["article 15"],
    "explainability": ["article 13",
                       "article 14 (4c)"],
    "fairness": ["article 10",
                 "article 15"],
    "uncertainity": ["article 13"],
    "privacy": ["article 2"],
    "data minimality": ["article 10"],
}

property_to_metrics = {
    "adversarial robustness": ["fast gradient sign method",
                               "projected gradient descent"],
    "explainability": ["gradient explanations",
                       "LIME",
                       "SHAP",
                       "identified feature importance",
                       "explanation alignment"],
    "fairness": ["equality of opportunity",
                 "demographic parity"],
    "uncertainity": ["OOD",
                     "AUROC"],
    "privacy": ["prediction privacy scores"],
    "data minimality": ["from paper"],
}
