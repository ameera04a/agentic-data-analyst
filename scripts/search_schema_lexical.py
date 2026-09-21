from agentic_data_analyst.lexical_retrieval import (
    LexicalSchemaRetriever,
)


def main() -> None:
    retriever = LexicalSchemaRetriever()

    queries = (
        "payment_sequential",
        "payment installments",
        "product weight dimensions",
        "customer city state",
        "freight shipping",
        "delivery status",
    )

    for query in queries:
        print("=" * 80)
        print(f"Query: {query}\n")

        results = retriever.search(
            query=query,
            top_k=3,
        )

        if not results:
            print("No lexical matches.")
            continue

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"{result.schema_name}."
                f"{result.table_name} "
                f"(score={result.score:.4f})"
            )

        print()


if __name__ == "__main__":
    main()
    