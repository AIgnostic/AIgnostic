from llm_insights.insights import metric_insights


async def main():
    mesg = await metric_insights(
        property_name="property_name",
        metric_name="metric_name",
        metric_value="metric_value",
        article_extracts=["article_extracts"],
        llm=init_llm("api_key"),
    )
    print(mesg)
    print(mesg.contents)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
