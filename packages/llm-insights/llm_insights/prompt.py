from typing import List


PROMPT = """
<goal>
We want to understand the meaning of various metrics evaluating AI Models in relation to various properties we want
our model to exhibit.
These proprties are related to various pieces of legislation and we want to understand the implications of these metrics
in relation to these laws.

Below you are provided with:
- The name of the property in question
- The name of the metric in question that is linked into the property
- The value evaluated for the metric (usually floating point number between 0 and 1)
- Extracts of articles of the EU AI Act related to the metric/property to use

We want to know how 'good' our LLM would be and if it is compliant with the law - it is your job based on the
information to provide a written response about this
</goal>

<return format>
A string response explaining the implications of the metric in relation to the law and our model.
</return format>

<warnings>
- Your responses are targeted towards researches with expertise in the area - please do not simplify your response
- Keep responses brief and to the point: they are going into a report and we don't want that to be too long
</warnings>

<information>
    <property_name>{property_name}</property_name>
    <metric_name>{metric_name}</metric_name>
    <metric_value>{metric_value}</metric_value>
</information>
<articles>
    {article_extracts}
</articles>

Please provide your response in a maximum of 2 paragraphs.
"""


def construct_articles(article_extracts: List[str]) -> str:
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


def construct_prompt(
    property_name: str,
    metric_name: str,
    metric_value: str,
    article_extracts: List[dict],
) -> str:
    return PROMPT.format(
        property_name=property_name,
        metric_name=metric_name,
        metric_value=metric_value,
        article_extracts=construct_articles(article_extracts),
    )
