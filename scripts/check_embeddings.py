from agentic_data_analyst.embedding_service import (
    EmbeddingService,
)
from agentic_data_analyst.schema_documents import (
    build_schema_documents,
)
from agentic_data_analyst.schema_introspection import (
    introspect_schema,
)


def dot_product(
    first: list[float],
    second: list[float],
) -> float:
    return sum(
        left * right
        for left, right in zip(first, second)
    )


def main() -> None:
    service = EmbeddingService()

    tables = introspect_schema()
    documents = build_schema_documents(tables)

    document_embeddings = service.embed_documents(
        [document.content for document in documents]
    )

    query = (
        "Where can I find customer payment "
        "installment information?"
    )

    query_embedding = service.embed_query(query)

    print(f"Model: {service.model_name}")
    print(f"Dimension: {len(query_embedding)}")
    print(f"Documents embedded: {len(document_embeddings)}")

    results = []

    for document, embedding in zip(
        documents,
        document_embeddings,
    ):
        score = dot_product(
            query_embedding,
            embedding,
        )

        results.append(
            (
                score,
                document.table_name,
            )
        )

    print(f"\nQuery: {query}\n")

    for score, table_name in sorted(
        results,
        reverse=True,
    ):
        print(
            f"{table_name:<20} "
            f"{score:.4f}"
        )


if __name__ == "__main__":
    main()