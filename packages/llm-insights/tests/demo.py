"""Example way to call the LLM insights API."""

import os
from aggregator.aggregator import get_api_key
from llm_insights.insights import init_llm, metric_insights
from report_generation.utils import extract_legislation_text, parse_legislation_text


async def main():
    article_content_13 = extract_legislation_text("13")
    parsed_data_13 = parse_legislation_text("13", article_content_13)

    article_content_14 = extract_legislation_text("14")
    parsed_data_14 = parse_legislation_text("14", article_content_14)
    print(f"Using key {get_api_key()}")

    mesg = metric_insights(
        property_name="explainability",
        metrics=[
            {"metric": "gradient explanations", "value": "0.8"},
            {"metric": "feature attribution", "value": "0.75"},
        ],
        article_extracts=[parsed_data_13, parsed_data_14],
        llm=init_llm(get_api_key()),
    )
    print(mesg)
    print(mesg.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
