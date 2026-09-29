import json
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from agentic_data_analyst.tools.schema_search import (
    SchemaSearchTool,
    SearchSchemaArgs,
)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    args_model: type[BaseModel]
    handler: Callable[[Any], dict[str, Any]]

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

        self._tools = {
            "search_schema": ToolSpec(
                name="search_schema",
                description=(
                    "Search the database schema and business "
                    "metadata for tables, columns, keys, and "
                    "relationships relevant to a data-analysis "
                    "question. Use this before assuming database "
                    "structure or generating SQL."
                ),
                args_model=SearchSchemaArgs,
                handler=schema_search.execute,
            )
        }

    @property
    def api_schemas(self) -> list[dict[str, Any]]:
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
                        f"Unknown tool: {tool_name}"
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
                        f"Tool execution failed: {exc}"
                    ),
                }
            )