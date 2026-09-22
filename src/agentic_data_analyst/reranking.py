from dataclasses import dataclass

from sentence_transformers import CrossEncoder

from agentic_data_analyst.hybrid_retrieval import (
    HybridSchemaRetriever,
)


DEFAULT_RERANKER_MODEL = (
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


@dataclass(frozen=True)
class RerankedSearchResult:
    schema_name: str
    table_name: str
    content: str

    rerank_score: float
    hybrid_rank: int

    rrf_score: float
    dense_rank: int | None
    lexical_rank: int | None


class SchemaReranker:
    def __init__(
        self,
        hybrid_retriever: HybridSchemaRetriever | None = None,
        model_name: str = DEFAULT_RERANKER_MODEL,
    ) -> None:
        self.hybrid_retriever = (
            hybrid_retriever
            or HybridSchemaRetriever()
        )

        self.model_name = model_name

        self.model = CrossEncoder(
            model_name
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
        candidate_k: int = 5,
    ) -> list[RerankedSearchResult]:
        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if candidate_k < top_k:
            raise ValueError(
                "candidate_k must be greater than "
                "or equal to top_k."
            )

        candidates = self.hybrid_retriever.search(
            query=query,
            top_k=candidate_k,
            candidate_k=candidate_k,
        )

        if not candidates:
            return []

        pairs = [
            (
                query,
                candidate.content,
            )
            for candidate in candidates
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        scored_candidates = []

        for hybrid_rank, (
            candidate,
            score,
        ) in enumerate(
            zip(
                candidates,
                scores,
                strict=True,
            ),
            start=1,
        ):
            scored_candidates.append(
                (
                    float(score),
                    hybrid_rank,
                    candidate,
                )
            )

        scored_candidates.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            RerankedSearchResult(
                schema_name=candidate.schema_name,
                table_name=candidate.table_name,
                content=candidate.content,
                rerank_score=score,
                hybrid_rank=hybrid_rank,
                rrf_score=candidate.rrf_score,
                dense_rank=candidate.dense_rank,
                lexical_rank=candidate.lexical_rank,
            )
            for (
                score,
                hybrid_rank,
                candidate,
            ) in scored_candidates[:top_k]
        ]