from typing import List


PROMPT = """
<goal>
We want to understand the meaning of various metrics evaluating AI Models in relation to various properties we want our model to exhibit.
These proprties are related to various pieces of legislation and we want to understand the implications of these metrics in relation to these laws.

Below you are provided with:
- The name of the property in question
- The name of the metric in question that is linked into the property
- The value evaluated for the metric (usually floating point number between 0 and 1)
- Extracts of articles of laws related to the metric/property to use

We want to know how 'good' our LLM would be and if it is compliant with the law - it is your job based on the information to provide a written response about this
</goal>

<return format>
A string response explaining the implications of the metric in relation to the law and our model.
</return format>

<information>
	<property_name>{property_name}</property_name>
	<metric_name>{metric_name}</metric_name>
	<metric_value>{metric_value}</metric_value>
</information>
<articles>
	{article_extracts}
</articles>

Please provide your response.
"""


def construct_articles(article_extracts: List[str]) -> str:
    return "\n\n----\n\n".join(article_extracts)


def construct_prompt(
		property_name: str, metric_name: str, metric_value: str, article_extracts: List[str]
) -> str:
		return PROMPT.format(
				property_name=property_name,
				metric_name=metric_name,
				metric_value=metric_value,
				article_extracts=construct_articles(article_extracts),
		)