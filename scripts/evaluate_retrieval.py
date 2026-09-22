from agentic_data_analyst.dense_retrieval import (
    DenseSchemaRetriever,
)
from agentic_data_analyst.hybrid_retrieval import (
    HybridSchemaRetriever,
)
from agentic_data_analyst.lexical_retrieval import (
    LexicalSchemaRetriever,
)
from agentic_data_analyst.reranking import (
    SchemaReranker,
)
from agentic_data_analyst.retrieval_eval_cases import (
    RETRIEVAL_TEST_CASES,
)
from agentic_data_analyst.retrieval_evaluation import (
    hit_at_k,
    recall_at_k,
    reciprocal_rank,
)

def table_names(results) -> list[str]:
    return [
        f"{result.schema_name}.{result.table_name}"
        for result in results
    ]


def table_names(results) -> list[str]:
    return [
        f"{result.schema_name}.{result.table_name}"
        for result in results
    ]


def evaluate(
    name: str,
    search,
) -> None:
    hit_scores = []
    recall_scores = []
    reciprocal_ranks = []

    print("=" * 80)
    print(name)

    for case in RETRIEVAL_TEST_CASES:
        results = search(
            case.query,
            3,
        )

        ranked_tables = table_names(
            results
        )

        hit_scores.append(
            hit_at_k(
                ranked_tables,
                case.relevant_tables,
                k=1,
            )
        )

        recall_scores.append(
            recall_at_k(
                ranked_tables,
                case.relevant_tables,
                k=3,
            )
        )

        reciprocal_ranks.append(
            reciprocal_rank(
                ranked_tables,
                case.relevant_tables,
            )
        )

    hit_at_1 = (
        sum(hit_scores)
        / len(hit_scores)
    )

    recall_at_3 = (
        sum(recall_scores)
        / len(recall_scores)
    )

    mrr = (
        sum(reciprocal_ranks)
        / len(reciprocal_ranks)
    )

    print(f"Hit@1:   {hit_at_1:.3f}")
    print(f"Recall@3:{recall_at_3:.3f}")
    print(f"MRR:     {mrr:.3f}")
    print()


def main() -> None:
    dense = DenseSchemaRetriever()
    lexical = LexicalSchemaRetriever()
    hybrid = HybridSchemaRetriever()

    reranked = SchemaReranker(
        hybrid_retriever=hybrid
    )

    evaluate(
        "Dense",
        lambda query, k: dense.search(
            query=query,
            top_k=k,
        ),
    )

    evaluate(
        "Lexical",
        lambda query, k: lexical.search(
            query=query,
            top_k=k,
        ),
    )

    evaluate(
        "Hybrid RRF",
        lambda query, k: hybrid.search(
            query=query,
            top_k=k,
            candidate_k=5,
        ),
    )

    evaluate(
        "Hybrid + Reranker",
        lambda query, k: reranked.search(
            query=query,
            top_k=k,
            candidate_k=5,
        ),
    )


if __name__ == "__main__":
    main()