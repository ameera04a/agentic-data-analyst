from typing import Any

from pydantic import BaseModel, Field

from agentic_data_analyst.business_metadata import (
    BUSINESS_METADATA,
)
from agentic_data_analyst.schema_introspection import (
    introspect_schema,
)


class GetTableSchemaArgs(BaseModel):
    schema_name: str = Field(
        default="public",
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
        description=(
            "Exact PostgreSQL schema name. "
            "Defaults to public."
        ),
    )

    table_name: str = Field(
        min_length=1,
        max_length=63,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
        description=(
            "Exact table name to inspect. "
            "Use search_schema first if the "
            "table name is unknown."
        ),
    )


class TableSchemaTool:
    def execute(
        self,
        args: GetTableSchemaArgs,
    ) -> dict[str, Any]:
        tables = introspect_schema(
            schema_name=args.schema_name
        )

        table = next(
            (
                item
                for item in tables
                if item.table_name
                == args.table_name
            ),
            None,
        )

        if table is None:
            return {
                "found": False,
                "schema_name": args.schema_name,
                "table_name": args.table_name,
                "error": (
                    "Table not found. Use "
                    "search_schema to discover "
                    "valid tables."
                ),
            }

        key = (
            f"{table.schema_name}."
            f"{table.table_name}"
        )

        metadata = BUSINESS_METADATA.get(key)

        column_descriptions = (
            metadata.column_descriptions
            if metadata is not None
            else {}
        )

        return {
            "found": True,
            "schema_name": table.schema_name,
            "table_name": table.table_name,
            "business_purpose": (
                metadata.purpose
                if metadata is not None
                else None
            ),
            "common_analytical_uses": (
                list(metadata.use_cases)
                if metadata is not None
                else []
            ),
            "columns": [
                {
                    "name": column.name,
                    "data_type": column.data_type,
                    "nullable": column.nullable,
                    "description": (
                        column_descriptions.get(
                            column.name
                        )
                    ),
                }
                for column in table.columns
            ],
            "primary_key": list(
                table.primary_key
            ),
            "foreign_keys": [
                {
                    "columns": list(
                        foreign_key.constrained_columns
                    ),
                    "referred_schema": (
                        foreign_key.referred_schema
                        or args.schema_name
                    ),
                    "referred_table": (
                        foreign_key.referred_table
                    ),
                    "referred_columns": list(
                        foreign_key.referred_columns
                    ),
                }
                for foreign_key in table.foreign_keys
            ],
        }