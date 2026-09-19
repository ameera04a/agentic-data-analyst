from dataclasses import dataclass

from sqlalchemy import select

from agentic_data_analyst.db import SessionLocal
from agentic_data_analyst.embedding_service import EmbeddingService
from agentic_data_analyst.models import SchemaDocument


@dataclass(frozen=True)
class DenseSearchResult:
    schema_name: str
    table_name: str
    content: str
    distance: float
    similarity: float


class DenseSchemaRetriever:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.embedding_service = (
            embedding_service or EmbeddingService()
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[DenseSearchResult]:
        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        distance_expression = (
            SchemaDocument.embedding.cosine_distance(
                query_embedding
            )
        )

        statement = (
            select(
                SchemaDocument,
                distance_expression.label(
                    "distance"
                ),
            )
            .where(
                SchemaDocument.embedding.is_not(None)
            )
            .where(
                SchemaDocument.embedding_model
                == self.embedding_service.model_name
            )
            .order_by(distance_expression)
            .limit(top_k)
        )

        with SessionLocal() as session:
            rows = session.execute(
                statement
            ).all()

        results = []

        for document, distance in rows:
            distance_value = float(distance)

            results.append(
                DenseSearchResult(
                    schema_name=document.schema_name,
                    table_name=document.table_name,
                    content=document.content,
                    distance=distance_value,
                    similarity=1.0 - distance_value,
                )
            )

        return results