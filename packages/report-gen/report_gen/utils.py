import json

property_to_regulations = {
    "adversarial robustness" : ["article 15"],
    "explainability" : ["article 13", 
                        "article 14 (4c)"],
    "fairness" : ["article 10", 
                  "article 15"], 
    "uncertainity": ["article 13"],
    "privacy": ["article 2"],
    "data minimality": ["article 10"],
}

property_to_metrics = {
    "adversarial robustness" : ["fast gradient sign method", 
                                "projected gradient descent"],
    "explainability" : ["gradient explanations", 
                        "LIME", 
                        "SHAP",
                        "identified feature importance",
                        "explanation alignment"],
    "fairness" : ["equality of opportunity",
                  "demographic parity"], 
    "uncertainity": ["OOD",
                     "AUROC"],
    "privacy": ["prediction privacy scores"],
    "data minimality": ["from paper"],
}

def search_legislation(metric: str) -> dict:
    """
    Searches for relevant legal sections based on a metric.
    Returns a dictionary with matching articles and descriptions.
    """
    result = {}
    for property, metrics in property_to_metrics.items():
        if metric in metrics:
            result.update({regulation: "Placeholder" for regulation in property_to_regulations[property]})
            break

    return result


def extract_legislation_text(article: str) -> str:
    """
    Extracts text from the specified article of GDPR or AI Act.
    """
    pass

def generate_report(metrics_data: dict) -> json:
    """
    Generates a structured JSON report mapping metrics to legal references.
    """
    pass

# INPUT:
#"send metric name and score"
# OUTPUT:
#returns "extracts" []
#"llm_insights": []