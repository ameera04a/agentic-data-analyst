from typing import Any

from langchain_core.tools import BaseTool, tool

from agentic_data_analyst.tools.schema_search import (
    SchemaSearchTool,
    SearchSchemaArgs,
)
from agentic_data_analyst.tools.sql_execution import (
    ExecuteSqlArgs,
    SqlExecutionTool,
)
from agentic_data_analyst.tools.table_schema import (
    GetTableSchemaArgs,
    TableSchemaTool,
)
from pydantic import Field


def build_langchain_tools() -> list[BaseTool]:
    schema_search_tool = SchemaSearchTool()
    table_schema_tool = TableSchemaTool()
    sql_execution_tool = SqlExecutionTool()

    @tool(
        "search_schema",
        args_schema=SearchSchemaArgs,
        description=(
            "Discover database tables relevant to a "
            "data-analysis question when exact table "
            "names are not known. Use this for table "
            "discovery, then inspect exact tables with "
            "get_table_schema."
        ),
    )
    def search_schema(
        query: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        args = SearchSchemaArgs(
            query=query,
            top_k=top_k,
        )

        return schema_search_tool.execute(args)

    @tool(
        "get_table_schema",
        args_schema=GetTableSchemaArgs,
        description=(
            "Inspect one exact database table and "
            "return its columns, data types, primary "
            "key, foreign keys, and business metadata. "
            "Use this to verify schema and join paths "
            "before generating SQL."
        ),
    )
    def get_table_schema(
        table_name: str,
        schema_name: str = "public",
    ) -> dict[str, Any]:
        args = GetTableSchemaArgs(
            schema_name=schema_name,
            table_name=table_name,
        )

        return table_schema_tool.execute(args)

    @tool(
    "get_table_schemas",
    description=(
        "Inspect multiple known database tables together. "
        "Prefer this for questions requiring joins."
    ),
    )
    def get_table_schemas(
        table_names: list[str] = Field(
            min_length=1,
            max_length=5,
        ),
    ) -> dict[str, Any]:
        results = []

        for table_name in table_names:
            args = GetTableSchemaArgs(
                table_name=table_name,
                schema_name="public",
            )

            results.append(
                table_schema_tool.execute(args)
            )

        return {"tables": results}

    
    @tool(
        "execute_sql",
        args_schema=ExecuteSqlArgs,
        description=(
            "Execute one read-only PostgreSQL query "
            "against the business database. Use only "
            "verified tables and columns. The tool "
            "does not permit database writes."
        ),
    )
    def execute_sql(
        sql: str,
    ) -> dict[str, Any]:
        args = ExecuteSqlArgs(
            sql=sql,
        )

        return sql_execution_tool.execute(args)

    return [
        search_schema,
        get_table_schema,
        get_table_schemas,
        execute_sql,
    ]