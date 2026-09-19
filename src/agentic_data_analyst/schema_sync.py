from dataclasses import dataclass

from sqlalchemy import select

from agentic_data_analyst.db import SessionLocal
from agentic_data_analyst.embedding_service import EmbeddingService
from agentic_data_analyst.models import SchemaDocument
from agentic_data_analyst.schema_documents import (
    SchemaDocumentDraft,
    build_schema_documents,
)
from agentic_data_analyst.schema_introspection import (
    introspect_schema,
)


@dataclass(frozen=True)
class SchemaSyncReport:
    inserted: int
    updated: int
    skipped: int
    deleted: int


def document_key(
    schema_name: str,
    table_name: str,
) -> tuple[str, str]:
    return schema_name, table_name


def sync_schema_index() -> SchemaSyncReport:
    tables = introspect_schema()

    drafts = build_schema_documents(tables)

    drafts_by_key = {
        document_key(
            draft.schema_name,
            draft.table_name,
        ): draft
        for draft in drafts
    }

    embedding_service = EmbeddingService()

    with SessionLocal() as session:
        existing_documents = session.scalars(
            select(SchemaDocument)
        ).all()

    existing_state = {
        document_key(
            document.schema_name,
            document.table_name,
        ): {
            "content_hash": document.content_hash,
            "embedding_model": document.embedding_model,
            "has_embedding": document.embedding is not None,
        }
        for document in existing_documents
    }

    current_keys = set(drafts_by_key)
    existing_keys = set(existing_state)

    deleted_keys = existing_keys - current_keys

    drafts_to_embed: list[SchemaDocumentDraft] = []

    skipped = 0

    for key, draft in drafts_by_key.items():
        state = existing_state.get(key)

        needs_embedding = (
            state is None
            or state["content_hash"] != draft.content_hash
            or not state["has_embedding"]
            or state["embedding_model"]
            != embedding_service.model_name
        )

        if needs_embedding:
            drafts_to_embed.append(draft)
        else:
            skipped += 1

    embeddings = embedding_service.embed_documents(
        [
            draft.content
            for draft in drafts_to_embed
        ]
    )

    embeddings_by_key = {
        document_key(
            draft.schema_name,
            draft.table_name,
        ): embedding
        for draft, embedding in zip(
            drafts_to_embed,
            embeddings,
            strict=True,
        )
    }

    inserted = 0
    updated = 0
    deleted = 0

    with SessionLocal.begin() as session:
        stored_documents = session.scalars(
            select(SchemaDocument)
        ).all()

        stored_by_key = {
            document_key(
                document.schema_name,
                document.table_name,
            ): document
            for document in stored_documents
        }

        for key, draft in drafts_by_key.items():
            embedding = embeddings_by_key.get(key)

            if embedding is None:
                continue

            stored = stored_by_key.get(key)

            if stored is None:
                session.add(
                    SchemaDocument(
                        schema_name=draft.schema_name,
                        table_name=draft.table_name,
                        content=draft.content,
                        content_hash=draft.content_hash,
                        embedding_model=(
                            embedding_service.model_name
                        ),
                        embedding=embedding,
                    )
                )

                inserted += 1

            else:
                stored.content = draft.content
                stored.content_hash = draft.content_hash
                stored.embedding_model = (
                    embedding_service.model_name
                )
                stored.embedding = embedding

                updated += 1

        for key in deleted_keys:
            stored = stored_by_key.get(key)

            if stored is not None:
                session.delete(stored)
                deleted += 1

    return SchemaSyncReport(
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        deleted=deleted,
    )