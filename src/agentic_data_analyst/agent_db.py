from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from agentic_data_analyst.config import settings


def create_agent_engine() -> Engine:
    if settings.agent_database_url is None:
        raise RuntimeError(
            "AGENT_DATABASE_URL is not configured."
        )

    return create_engine(
        settings.agent_database_url.get_secret_value(),
        pool_pre_ping=True,
    )