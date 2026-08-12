from openai import OpenAI
from app.config import settings


def get_llm_client() -> OpenAI:
    return OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key or "not-needed",
    )


def chat_completion(messages: list[dict], model: str = None) -> tuple[str, dict]:
    """Returns (content, stats) where stats carries token usage for metrics."""
    client = get_llm_client()
    response = client.chat.completions.create(
        model=model or settings.llm_model,
        messages=messages,
        temperature=0.1,
    )
    content = response.choices[0].message.content or ""
    usage = getattr(response, "usage", None)
    stats = {"tokens": usage.total_tokens if usage else 0}
    return content, stats