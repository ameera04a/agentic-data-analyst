from groq import Groq

from agentic_data_analyst.config import settings


def create_groq_client() -> Groq:
    if settings.groq_api_key is None:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    return Groq(
        api_key=settings.groq_api_key.get_secret_value()
    )