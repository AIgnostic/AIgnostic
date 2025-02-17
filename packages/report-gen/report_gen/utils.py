import json
import requests
from bs4 import BeautifulSoup
import re

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
    url = f"https://gdpr-info.eu/art-{article}-gdpr/"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to fetch Article {article}."
    soup = BeautifulSoup(response.text, "html.parser")
    article_content = soup.find("article")
    if not article_content:
        return f"Could not parse content for Article {article}."

    return article_content.get_text(separator="\n").strip()

def parse_legislation_text(article: str, article_content: str) -> dict:
    """
    Parses the raw article content into structured data.
    """
    data = {
        "article_number": article,
        "article_title": "",
        "description": "",
        "suitable_recitals": []
    }

    # Normalize text and split into lines
    text_lines = [re.sub(r'\s+', ' ', line.strip()) for line in article_content.split("\n") if line.strip()]

    i = 0
    while i < len(text_lines):
        line = text_lines[i]

        # Extract Article Title (Line after "Art. {article} GDPR")
        if line.startswith(f"Art. {article} GDPR") and i + 1 < len(text_lines):
            data["article_title"] = text_lines[i + 1] 
            i += 1  

        # Extract Description (Main body of the article)
        elif "Suitable Recitals" not in line and not line.startswith("Art.") and "GDPR" not in line:
            # Ensure the numbering (1., 2., 3., etc.) stays intact
            data["description"] += line + " "  

        # Extract Suitable Recitals
        elif "Suitable Recitals" in line:
            i += 1  # Move to next line
            while i < len(text_lines) and not text_lines[i].startswith("Art."): 
                match = re.search(r'\b(\d+)\b', text_lines[i])  
                if match:
                    recital_number = match.group(1)
                    recital_link = f"https://gdpr-info.eu/recitals/no-{recital_number}/"  # Create link
                    data["suitable_recitals"].append(recital_link)
                i += 1
            break

        i += 1

    data["description"] = data["description"].strip()  # Final cleanup
    return data




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