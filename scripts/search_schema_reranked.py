from agentic_data_analyst.reranking import (
    SchemaReranker,
)


def main() -> None:
    retriever = SchemaReranker()

    queries = (
        "Where can I find customer payment installment information?",
        "Which table contains payment_sequential?",
        "How did customers pay over several months?",
        "Where are product dimensions and weight stored?",
        "Where can I analyze freight costs?",
    )

    for query in queries:
        print("=" * 80)
        print(f"Query: {query}\n")

        results = retriever.search(
            query=query,
            top_k=3,
            candidate_k=5,
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"{result.schema_name}."
                f"{result.table_name}"
            )

            print(
                f"   RerankScore="
                f"{result.rerank_score:.4f} "
                f"HybridRank="
                f"{result.hybrid_rank}"
            )

        print()


if __name__ == "__main__":
    main()