import re
from dataclasses import dataclass

from sqlalchemy import func, select

from agentic_data_analyst.db import SessionLocal
from agentic_data_analyst.models import SchemaDocument


@dataclass(frozen=True)
class LexicalSearchResult:
    schema_name: str
    table_name: str
    content: str
    score: float


def build_lexical_query(query: str) -> str:
    terms = re.findall(
        r"\w+",
        query.lower(),
    )

    return " OR ".join(terms)


class LexicalSchemaRetriever:
    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[LexicalSearchResult]:
        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        lexical_query = build_lexical_query(query)

        if not lexical_query:
            return []

        ts_query = func.websearch_to_tsquery(
            "english",
            lexical_query,
        )

        rank_expression = func.ts_rank_cd(
            SchemaDocument.search_vector,
            ts_query,
        )

        statement = (
            select(
                SchemaDocument,
                rank_expression.label(
                    "score"
                ),
            )
            .where(
                SchemaDocument.search_vector.op("@@")(
                    ts_query
                )
            )
            .order_by(
                rank_expression.desc()
            )
            .limit(top_k)
        )

        with SessionLocal() as session:
            rows = session.execute(
                statement
            ).all()

        return [
            LexicalSearchResult(
                schema_name=document.schema_name,
                table_name=document.table_name,
                content=document.content,
                score=float(score),
            )
            for document, score in rows
        ]