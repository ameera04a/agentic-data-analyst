from agentic_data_analyst.dense_retrieval import (
    DenseSchemaRetriever,
)


def main() -> None:
    retriever = DenseSchemaRetriever()

    queries = (
        "Where can I find customer payment installment information?",
        "Which table contains product dimensions and weight?",
        "Where is customer city and state information stored?",
        "Where can I analyze freight costs?",
        "Which table contains order delivery status?",
    )

    for query in queries:
        print("=" * 80)
        print(f"Query: {query}\n")

        results = retriever.search(
            query=query,
            top_k=3,
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"{result.schema_name}."
                f"{result.table_name} "
                f"(similarity={result.similarity:.4f})"
            )

        print()


if __name__ == "__main__":
    main()