import json
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from agentic_data_analyst.tools.schema_search import (
    SchemaSearchTool,
    SearchSchemaArgs,
)
from agentic_data_analyst.tools.table_schema import (
    GetTableSchemaArgs,
    TableSchemaTool,
)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    args_model: type[BaseModel]
    handler: Callable[
        [Any],
        dict[str, Any],
    ]

    def api_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": (
                    self.args_model.model_json_schema()
                ),
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        schema_search = SchemaSearchTool()
        table_schema = TableSchemaTool()

        self._tools = {
            "search_schema": ToolSpec(
                name="search_schema",
                description=(
                    "Discover database tables "
                    "relevant to a data-analysis "
                    "question when the exact table "
                    "name is not yet known. Returns "
                    "ranked candidate tables and "
                    "their business purpose. Use "
                    "get_table_schema afterward "
                    "when exact columns, keys, or "
                    "relationships are needed."
                ),
                args_model=SearchSchemaArgs,
                handler=schema_search.execute,
            ),
            "get_table_schema": ToolSpec(
                name="get_table_schema",
                description=(
                    "Inspect one exact database "
                    "table and return its columns, "
                    "data types, primary key, "
                    "foreign keys, and business "
                    "metadata. Use this when the "
                    "exact table name is already "
                    "known. If it is unknown, use "
                    "search_schema first."
                ),
                args_model=GetTableSchemaArgs,
                handler=table_schema.execute,
            ),
        }

    @property
    def api_schemas(
        self,
    ) -> list[dict[str, Any]]:
        return [
            spec.api_schema()
            for spec in self._tools.values()
        ]

    def execute(
        self,
        tool_name: str,
        arguments_json: str,
    ) -> str:
        spec = self._tools.get(tool_name)

        if spec is None:
            return json.dumps(
                {
                    "is_error": True,
                    "error": (
                        f"Unknown tool: "
                        f"{tool_name}"
                    ),
                }
            )

        try:
            arguments = (
                spec.args_model.model_validate_json(
                    arguments_json
                )
            )

            result = spec.handler(arguments)

            return json.dumps(
                result,
                ensure_ascii=False,
            )

        except ValidationError as exc:
            return json.dumps(
                {
                    "is_error": True,
                    "error": (
                        "Invalid tool arguments."
                    ),
                    "details": exc.errors(),
                }
            )

        except Exception as exc:
            return json.dumps(
                {
                    "is_error": True,
                    "error": (
                        "Tool execution failed: "
                        f"{exc}"
                    ),
                }
            )