import requests
from bs4 import BeautifulSoup
import re
from .constants import property_to_metrics, property_to_regulations
from llm_insights.insights import init_llm, metric_insights
import os
import dotenv


def search_legislation(metric: str) -> list:
    """
    Searches for relevant legal sections based on a metric.
    Returns a list of matching articles.
    """
    result = []
    for property, metrics in property_to_metrics.items():
        if metric in metrics:
            result.extend(property_to_regulations[property])
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
    text_lines = [re.sub(r'\s+', ' ', line.strip())
                  for line in article_content.split("\n") if line.strip()]

    i = 0
    while i < len(text_lines):
        line = text_lines[i]

        # Extract Article Title
        if line.startswith(f"Art. {article} GDPR") and i + 1 < len(text_lines):
            data["article_title"] = text_lines[i + 1]
            i += 1

        # Extract Description
        elif ("Suitable Recitals" not in line and
              not line.startswith("Art.") and
              "GDPR" not in line):
            data["description"] += line + " "

        # Extract Suitable Recitals
        elif "Suitable Recitals" in line:
            i += 1
            while i < len(text_lines) and not text_lines[i].startswith("Art."):
                match = re.search(r'\b(\d+)\b', text_lines[i])
                if match:
                    recital_number = match.group(1)
                    recital_link = (
                        f"https://gdpr-info.eu/recitals/no-{recital_number}/"
                    )
                    data["suitable_recitals"].append(recital_link)
                i += 1
            break

        i += 1

    data["description"] = data["description"].strip()
    return data


def generate_report(metrics_data: dict, api_key: str) -> list[dict]:
    """
    metrics_data:
    {
        "metric1": "value1",
        "metric2": "value2",
        ...
    }
    api_key: Google API key for LLM

    output:

    [
        "property": fairness
        "computed_metrics": [
            {"metric": "metric1", "value": "value1"},
            {"metric": "metric2", "value": "value2"},
            ...
        ],
        "legislation_extracts": [
            {
                "article_number": "10",
                "article_title": "Processing of personal data relating to criminal convictions and offences",
                "description": "blah blah",
                "suitable_recitals": [
                    "https://gdpr-info.eu/recitals/no-1/",
                    "https://gdpr-info.eu/recitals/no-2/",
                    ...
                ]
            },
            ...
        ]
        "llm_insights": "blah blah blah"
    ]
    """

    results = []
    computed_metrics = set(metrics_data.keys())

    for property in property_to_metrics.keys():
        property_result = {}
        # find the intersection of computed metrics and metrics for the property
        property_metrics = set([p.replace(" ", "_") for p in property_to_metrics[property]])
        common_metrics = computed_metrics.intersection(property_metrics)
        property_result["property"] = property
        if common_metrics:
            property_result["computed_metrics"] = [
                {"metric": metric.replace("_", " "), "value": metrics_data[metric]}
                for metric in common_metrics
            ]
        else:
            property_result["computed_metrics"] = []

        property_result["legislation_extracts"] = []
        for regulations in property_to_regulations[property]:
            article_content = extract_legislation_text(regulations)
            parsed_data = parse_legislation_text(regulations, article_content)
            property_result["legislation_extracts"].append(parsed_data)

        # TODO: Add LLM insights
        property_result["llm_insights"] = []

        try:
            llm = init_llm(api_key)
            mesg = metric_insights(
                property_name=property,
                metrics=[
                    {"metric": metric.replace("_", " "), "value": str(metrics_data[metric])}
                    for metric in common_metrics
                ],
                article_extracts=property_result["legislation_extracts"],
                llm=llm
            )
        except Exception:
            mesg = "Failed to initialize LLM"

        property_result["llm_insights"].append(mesg)

        results.append(property_result)

    print(results)
    return results


# def generate_report(metrics_data: dict) -> json:
#     """
#     Generates a structured JSON report mapping metrics to legal references.
#     """
#     results = {
#         "extracts": [],
#         "llm insights": []
#     }
#     for metric in metrics_data:
#         legislation = search_legislation(metric)
#         for article in legislation:
#             article_number = article.split()[-1]
#             article_content = extract_legislation_text(article_number)
#             parsed_data = parse_legislation_text(article_number,
#                                                  article_content)
#             results["extracts"].append(parsed_data)
#     return results
