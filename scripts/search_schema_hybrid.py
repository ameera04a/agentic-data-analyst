from agentic_data_analyst.hybrid_retrieval import (
    HybridSchemaRetriever,
)


def main() -> None:
    retriever = HybridSchemaRetriever()

    queries = (
        "Where can I find customer payment installment information?",
        "Which table contains payment_sequential?",
        "How did customers pay over several months?",
        "Where are product dimensions and weight stored?",
        "Where can I analyze freight costs?",
        "Where is customer city and state information?",
    )

    for query in queries:
        print("=" * 80)
        print(f"Query: {query}\n")

        results = retriever.search(
            query=query,
            top_k=3,
            candidate_k=10,
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):
            dense_rank = (
                result.dense_rank
                if result.dense_rank is not None
                else "-"
            )

            lexical_rank = (
                result.lexical_rank
                if result.lexical_rank is not None
                else "-"
            )

            print(
                f"{rank}. "
                f"{result.schema_name}."
                f"{result.table_name}"
            )

            print(
                f"   RRF={result.rrf_score:.5f} "
                f"DenseRank={dense_rank} "
                f"LexicalRank={lexical_rank}"
            )

        print()


if __name__ == "__main__":
    main()