import os
from llm_insights.insights import init_llm, metric_insights
from report_generation.utils import extract_legislation_text, parse_legislation_text


async def main():
    article_content_13 = extract_legislation_text("13")
    parsed_data_13 = parse_legislation_text("13", article_content_13)

    article_content_14 = extract_legislation_text("14")
    parsed_data_14 = parse_legislation_text("14", article_content_14)

    # print(parsed_data_13)

    mesg = await metric_insights(
        property_name="explainability",
        metric_name="gradient explanations",
        metric_value="0.8",
        article_extracts=[parsed_data_13, parsed_data_14],
        llm=init_llm(os.getenv("GOOGLE_API_KEY")),
    )
    print(mesg)
    print(mesg.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
