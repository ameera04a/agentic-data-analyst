from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from agentic_data_analyst.agent_prompt import (
    SYSTEM_PROMPT,
)
from agentic_data_analyst.config import settings
from agentic_data_analyst.langchain_tools import (
    build_langchain_tools,
)


def create_langchain_model() -> ChatOpenAI:
    if settings.groq_api_key is None:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    return ChatOpenAI(
        model=settings.groq_model,
        api_key=(
            settings.groq_api_key.get_secret_value()
        ),
        base_url="https://api.groq.com/openai/v1",
        temperature=0.1,
        max_retries=2,
    )


def create_data_analyst_agent():
    model = create_langchain_model()
    tools = build_langchain_tools()

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )