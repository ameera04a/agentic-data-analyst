from sentence_transformers import SentenceTransformer

from agentic_data_analyst.embedding_config import (
    EMBEDDING_CONFIG,
    EmbeddingConfig,
)


class EmbeddingService:
    def __init__(
        self,
        config: EmbeddingConfig = EMBEDDING_CONFIG,
    ) -> None:
        self.config = config

        model_kwargs = {}

        if config.backend == "onnx":
            model_kwargs["provider"] = config.provider

        self.model = SentenceTransformer(
            config.model_name,
            backend=config.backend,
            model_kwargs=model_kwargs,
        )

        actual_dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        if actual_dimension != config.dimension:
            raise RuntimeError(
                "Embedding dimension mismatch: "
                f"configured={config.dimension}, "
                f"model={actual_dimension}"
            )

    @property
    def model_name(self) -> str:
        return self.config.model_name

    @property
    def dimension(self) -> int:
        return self.config.dimension

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode_document(
            texts,
            normalize_embeddings=(
                self.config.normalize_embeddings
            ),
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        embedding = self.model.encode_query(
            query,
            prompt=self.config.query_instruction,
            normalize_embeddings=(
                self.config.normalize_embeddings
            ),
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embedding.tolist()