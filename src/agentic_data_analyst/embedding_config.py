from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class EmbeddingConfig:
    model_name: str
    dimension: int
    backend: Literal["onnx", "torch"]
    provider: str
    query_instruction: str
    normalize_embeddings: bool


EMBEDDING_CONFIG = EmbeddingConfig(
    model_name="BAAI/bge-small-en-v1.5",
    dimension=384,
    backend="onnx",
    provider="CPUExecutionProvider",
    query_instruction=(
        "Represent this sentence for searching relevant passages: "
    ),
    normalize_embeddings=True,
)