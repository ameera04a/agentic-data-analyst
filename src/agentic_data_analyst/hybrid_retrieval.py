from dataclasses import dataclass

from agentic_data_analyst.dense_retrieval import (
    DenseSchemaRetriever,
)
from agentic_data_analyst.lexical_retrieval import (
    LexicalSchemaRetriever,
)


@dataclass(frozen=True)
class HybridSearchResult:
    schema_name: str
    table_name: str
    content: str
    rrf_score: float
    dense_rank: int | None
    lexical_rank: int | None
    dense_similarity: float | None
    lexical_score: float | None


@dataclass
class _FusionCandidate:
    schema_name: str
    table_name: str
    content: str
    rrf_score: float = 0.0
    dense_rank: int | None = None
    lexical_rank: int | None = None
    dense_similarity: float | None = None
    lexical_score: float | None = None


def document_key(
    schema_name: str,
    table_name: str,
) -> tuple[str, str]:
    return schema_name, table_name


def reciprocal_rank_score(
    rank: int,
    rrf_k: int,
) -> float:
    return 1.0 / (rrf_k + rank)


class HybridSchemaRetriever:
    def __init__(
        self,
        dense_retriever: DenseSchemaRetriever | None = None,
        lexical_retriever: LexicalSchemaRetriever | None = None,
        rrf_k: int = 60,
    ) -> None:
        if rrf_k <= 0:
            raise ValueError(
                "rrf_k must be greater than zero."
            )

        self.dense_retriever = (
            dense_retriever
            or DenseSchemaRetriever()
        )

        self.lexical_retriever = (
            lexical_retriever
            or LexicalSchemaRetriever()
        )

        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 3,
        candidate_k: int = 10,
    ) -> list[HybridSearchResult]:
        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if candidate_k < top_k:
            raise ValueError(
                "candidate_k must be greater than "
                "or equal to top_k."
            )

        dense_results = (
            self.dense_retriever.search(
                query=query,
                top_k=candidate_k,
            )
        )

        lexical_results = (
            self.lexical_retriever.search(
                query=query,
                top_k=candidate_k,
            )
        )

        candidates: dict[
            tuple[str, str],
            _FusionCandidate,
        ] = {}

        for rank, result in enumerate(
            dense_results,
            start=1,
        ):
            key = document_key(
                result.schema_name,
                result.table_name,
            )

            candidate = candidates.setdefault(
                key,
                _FusionCandidate(
                    schema_name=result.schema_name,
                    table_name=result.table_name,
                    content=result.content,
                ),
            )

            candidate.rrf_score += (
                reciprocal_rank_score(
                    rank=rank,
                    rrf_k=self.rrf_k,
                )
            )

            candidate.dense_rank = rank
            candidate.dense_similarity = (
                result.similarity
            )

        for rank, result in enumerate(
            lexical_results,
            start=1,
        ):
            key = document_key(
                result.schema_name,
                result.table_name,
            )

            candidate = candidates.setdefault(
                key,
                _FusionCandidate(
                    schema_name=result.schema_name,
                    table_name=result.table_name,
                    content=result.content,
                ),
            )

            candidate.rrf_score += (
                reciprocal_rank_score(
                    rank=rank,
                    rrf_k=self.rrf_k,
                )
            )

            candidate.lexical_rank = rank
            candidate.lexical_score = result.score

        ranked_candidates = sorted(
            candidates.values(),
            key=lambda candidate: (
                -candidate.rrf_score,
                candidate.schema_name,
                candidate.table_name,
            ),
        )

        return [
            HybridSearchResult(
                schema_name=candidate.schema_name,
                table_name=candidate.table_name,
                content=candidate.content,
                rrf_score=candidate.rrf_score,
                dense_rank=candidate.dense_rank,
                lexical_rank=candidate.lexical_rank,
                dense_similarity=(
                    candidate.dense_similarity
                ),
                lexical_score=(
                    candidate.lexical_score
                ),
            )
            for candidate in ranked_candidates[:top_k]
        ]