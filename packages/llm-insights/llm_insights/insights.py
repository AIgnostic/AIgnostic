from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages.base import BaseMessage
from llm_insights.prompt import construct_prompt


def init_llm(api_key: str) -> BaseChatModel:
    """Give an LLM client for sending messages for LLM Insights

    Args:
                    api_key (str): API Key to use

    Returns:
                    BaseChatModel: Chatbot
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-thinking-exp",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=api_key,
        google_api_key=api_key,
    )


async def metric_insights(
    property_name: str,
    metric_name: str,
    metric_value: str,
    article_extracts: List[dict],
    llm: BaseChatModel,
) -> BaseMessage:
    """Obtain insights into a metric using an LLM, by asking the LLM "here's the score, the metric, the law, does this seem right?"

    Args:
                    property_name (str): Name of the property in question
                    metric_name (str): Name of metric in question that is linked into the property
                    metric_value (str): Value evaluated for the metric (string for flexibility)
                    article_extracts (List[str]): Extracts of articles related to the metric/property to use
                    llm (BaseChatModel): LLM to use, likely created using init_llm but can be any LLM from LangChain

    Returns:
                    str: Insight output from LLM

    See tests/demo.py for an example
    """
    messages = [
        (
            "human",
            construct_prompt(
                property_name=property_name,
                metric_name=metric_name,
                metric_value=metric_value,
                article_extracts=article_extracts,
            ),
        )
    ]
    return await llm.ainvoke(messages)
