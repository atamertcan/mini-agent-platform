from langchain_openai import ChatOpenAI
from app.config import get_settings
from app.core.snapshots import AgentSnapshot

MAX_RESPONSE_TOKENS = 512


def get_llm(agent: AgentSnapshot) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=agent.model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=agent.temperature,
        max_tokens=MAX_RESPONSE_TOKENS,
    )
