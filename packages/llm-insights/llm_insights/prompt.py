from typing import List, Dict

PROMPT = """
<goal>
We want to understand the meaning of various metrics evaluating AI Models in relation to various properties we want
our model to exhibit.
These properties are related to various pieces of legislation and we want to understand
the implications of these metrics in relation to these laws.

Below you are provided with:
- The name of the property in question
- A list of metrics linked to the property, each with a name and value
- Extracts of articles of the EU AI Act related to the metrics/property to use

We want to know how 'good' our LLM would be and if it is compliant with the law - it is your job based on the
information to provide a written response about this
</goal>

<return format>
A single string response containing the following:
    - a summary of the parts of the legislation extracts that are most relevant to the metrics and the property.
    - an explanation of the implications of the computed metric values in the context of the law and our model.
</return format>

<warnings>
- Your responses are targeted towards researchers with expertise in the area - please do not simplify your response
- Keep responses brief and to the point: they are going into a report and we don't want that to be too long
</warnings>

<information>
    <property_name>{property_name}</property_name>
    <metrics>
        {metrics}
    </metrics>
</information>
<articles>
    {article_extracts}
</articles>

Please provide your response in a maximum of 2 paragraphs.
"""


def construct_articles(article_extracts: List[dict]) -> str:
    finalStr = ""

    for extract in article_extracts:
        article_number = extract["article_number"]
        article_title = extract["article_title"]
        description = extract["description"]
        finalStr += f"""
<article>
    <article_number>{article_number}</article_number>
    <article_title>{article_title}</article_title>
    <description>{description}</description>
</article>
                """

    return finalStr


def construct_metrics(metrics: List[Dict[str, str]]) -> str:
    metrics_str = ""
    for metric in metrics:
        metric_name = metric["metric"]
        metric_value = metric["value"]
        metrics_str += f"""
<metric>
    <metric_name>{metric_name}</metric_name>
    <metric_value>{metric_value}</metric_value>
</metric>
        """
    return metrics_str


def construct_prompt(
    property_name: str,
    metrics: List[Dict[str, str]],
    article_extracts: List[dict],
) -> str:
    return PROMPT.format(
        property_name=property_name,
        metrics=construct_metrics(metrics),
        article_extracts=construct_articles(article_extracts),
    )
