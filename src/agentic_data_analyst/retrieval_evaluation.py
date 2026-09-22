from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalTestCase:
    query: str
    relevant_tables: frozenset[str]


@dataclass(frozen=True)
class RetrievalMetrics:
    hit_at_1: float
    recall_at_3: float
    mrr: float


def hit_at_k(
    ranked_tables: list[str],
    relevant_tables: frozenset[str],
    k: int,
) -> float:
    top_k = ranked_tables[:k]

    return float(
        any(
            table in relevant_tables
            for table in top_k
        )
    )


def recall_at_k(
    ranked_tables: list[str],
    relevant_tables: frozenset[str],
    k: int,
) -> float:
    if not relevant_tables:
        return 0.0

    retrieved = set(
        ranked_tables[:k]
    )

    relevant_retrieved = (
        retrieved & relevant_tables
    )

    return (
        len(relevant_retrieved)
        / len(relevant_tables)
    )


def reciprocal_rank(
    ranked_tables: list[str],
    relevant_tables: frozenset[str],
) -> float:
    for rank, table in enumerate(
        ranked_tables,
        start=1,
    ):
        if table in relevant_tables:
            return 1.0 / rank

    return 0.0