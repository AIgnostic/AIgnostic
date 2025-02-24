from typing import List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages.base import BaseMessage
from llm_insights.prompt import construct_prompt


def init_llm(api_key: str) -> BaseChatModel:
    """Give an LLM client for sending messages for LLM Insights

    Args:
        api_key (str): API Key to use

    Returns:
    """

    try:
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-thinking-exp",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=api_key,
            google_api_key=api_key,
        )
    except Exception as e:
        print(f"Failed to initialize LLM: {e}")
        raise e


def metric_insights(
    property_name: str,
    metrics: List[Dict[str, str]],
    article_extracts: List[dict],
    llm: BaseChatModel,
) -> BaseMessage:
    """Obtain insights into multiple metrics using an LLM.

    Args:
        property_name (str): Name of the property in question
        metrics (List[Dict[str, str]]): List of dictionaries with 'metric' and 'value' keys
        article_extracts (List[dict]): Extracts of articles related to the metrics/property to use
        llm (BaseChatModel): LLM to use, likely created using init_llm but can be any LLM from LangChain

    Returns:
        BaseMessage: Insight output from LLM
    """
    messages = [
        (
            "human",
            construct_prompt(
                property_name=property_name,
                metrics=metrics,
                article_extracts=article_extracts,
            ),
        )
    ]
    return llm.invoke(messages)
