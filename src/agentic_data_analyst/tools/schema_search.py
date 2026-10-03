from typing import Any

from pydantic import BaseModel, Field

from agentic_data_analyst.business_metadata import (
    BUSINESS_METADATA,
)
from agentic_data_analyst.reranking import (
    SchemaReranker,
)


class SearchSchemaArgs(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=500,
        description=(
            "Natural-language description of the "
            "database information, tables, columns, "
            "or relationships needed."
        ),
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=5,
        description=(
            "Maximum number of relevant schema "
            "documents to return."
        ),
    )


class SchemaSearchTool:
    def __init__(
        self,
        retriever: SchemaReranker | None = None,
    ) -> None:
        self.retriever = (
            retriever or SchemaReranker()
        )

    def execute(
        self,
        args: SearchSchemaArgs,
    ) -> dict[str, Any]:
        results = self.retriever.search(
            query=args.query,
            top_k=args.top_k,
            candidate_k=5,
        )

        compact_results = []

        for rank, result in enumerate(
            results,
            start=1,
        ):
            key = (
                f"{result.schema_name}."
                f"{result.table_name}"
            )

            metadata = BUSINESS_METADATA.get(key)

            compact_results.append(
                {
                    "rank": rank,
                    "schema_name": result.schema_name,
                    "table_name": result.table_name,
                    "business_purpose": (
                        metadata.purpose
                        if metadata is not None
                        else None
                    ),
                }
            )

        return {
            "query": args.query,
            "results": compact_results,
        }