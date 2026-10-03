from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.engine import Engine

from agentic_data_analyst.agent_db import (
    create_agent_engine,
)
from agentic_data_analyst.sql_validation import (
    validate_readonly_sql,
)


class ExecuteSqlArgs(BaseModel):
    sql: str = Field(
        min_length=1,
        max_length=10_000,
        description=(
            "One PostgreSQL read-only SELECT query "
            "to execute. Use only verified table "
            "and column names."
        ),
    )


def to_json_safe(
    value: Any,
) -> Any:
    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    if isinstance(
        value,
        Decimal,
    ):
        return str(value)

    if isinstance(
        value,
        (datetime, date, time),
    ):
        return value.isoformat()

    return str(value)


class SqlExecutionTool:
    def __init__(
    self,
    engine: Engine | None = None,
    max_rows: int = 100,
    statement_timeout_ms: int = 5_000,
) -> None:
        if max_rows <= 0:
            raise ValueError(
                "max_rows must be greater than zero."
            )

        if statement_timeout_ms <= 0:
            raise ValueError(
                "statement_timeout_ms must be "
                "greater than zero."
            )
        self.engine = (
            engine
            if engine is not None
            else create_agent_engine()
        )
        self.max_rows = max_rows
        self.statement_timeout_ms = (
            statement_timeout_ms
        )

    def execute(
        self,
        args: ExecuteSqlArgs,
    ) -> dict[str, Any]:
        try:
            validated_sql = (
                validate_readonly_sql(
                    args.sql
                )
            )
        except ValueError as exc:
            return {
                "is_error": True,
                "error": str(exc),
            }

        try:
            with self.engine.connect() as connection:
                with connection.begin():
                    connection.execute(
                        text(
                            "SET TRANSACTION "
                            "READ ONLY"
                        )
                    )

                    connection.exec_driver_sql(
                        "SET LOCAL "
                        "statement_timeout = "
                        f"{self.statement_timeout_ms}"
                    )

                    result = connection.execute(
                        text(validated_sql)
                    )

                    if not result.returns_rows:
                        return {
                            "is_error": True,
                            "error": (
                                "Query did not "
                                "return rows."
                            ),
                        }

                    columns = list(
                        result.keys()
                    )

                    rows = (
                        result
                        .mappings()
                        .fetchmany(
                            self.max_rows + 1
                        )
                    )

                    truncated = (
                        len(rows)
                        > self.max_rows
                    )

                    rows = rows[
                        :self.max_rows
                    ]

                    serialized_rows = [
                        {
                            key: to_json_safe(
                                value
                            )
                            for key, value
                            in row.items()
                        }
                        for row in rows
                    ]

                    return {
                        "is_error": False,
                        "sql": validated_sql,
                        "columns": columns,
                        "rows": serialized_rows,
                        "returned_row_count": len(
                            serialized_rows
                        ),
                        "truncated": truncated,
                    }

        except SQLAlchemyError as exc:
            return {
                "is_error": True,
                "error": (
                    "SQL execution failed."
                ),
                "details": str(exc),
            }