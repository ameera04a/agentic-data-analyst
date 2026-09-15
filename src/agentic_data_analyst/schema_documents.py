from dataclasses import dataclass
from hashlib import sha256

from agentic_data_analyst.business_metadata import (
    BUSINESS_METADATA,
    TableBusinessMetadata,
)
from agentic_data_analyst.schema_introspection import SchemaTable


@dataclass(frozen=True)
class SchemaDocumentDraft:
    schema_name: str
    table_name: str
    content: str
    content_hash: str


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def get_business_metadata(
    table: SchemaTable,
) -> TableBusinessMetadata | None:
    key = f"{table.schema_name}.{table.table_name}"

    return BUSINESS_METADATA.get(key)


def build_schema_document(
    table: SchemaTable,
) -> SchemaDocumentDraft:
    business_metadata = get_business_metadata(table)

    lines: list[str] = []

    lines.append(
        f"Table: {table.schema_name}.{table.table_name}"
    )

    lines.append("")
    lines.append("Business purpose:")

    if business_metadata:
        lines.append(
            normalize_text(business_metadata.purpose)
        )
    else:
        lines.append(
            "No curated business metadata available."
        )

    lines.append("")
    lines.append("Common analytical uses:")

    if business_metadata:
        for use_case in business_metadata.use_cases:
            lines.append(
                f"- {normalize_text(use_case)}"
            )
    else:
        lines.append(
            "- No curated analytical use cases available."
        )

    lines.append("")
    lines.append("Columns:")

    for column in sorted(
        table.columns,
        key=lambda item: item.name,
    ):
        nullable_text = (
            "nullable"
            if column.nullable
            else "not nullable"
        )

        description = None

        if business_metadata:
            description = (
                business_metadata
                .column_descriptions
                .get(column.name)
            )

        if description:
            description = normalize_text(description)
        else:
            description = (
                "No curated business description available."
            )

        lines.append(
            f"- {column.name}: "
            f"{column.data_type}; "
            f"{nullable_text}; "
            f"{description}"
        )

    lines.append("")
    lines.append("Primary key:")

    if table.primary_key:
        lines.append(
            "- " + ", ".join(table.primary_key)
        )
    else:
        lines.append("- None")

    lines.append("")
    lines.append("Foreign keys:")

    if table.foreign_keys:
        sorted_foreign_keys = sorted(
            table.foreign_keys,
            key=lambda foreign_key: (
                foreign_key.constrained_columns,
                foreign_key.referred_table,
                foreign_key.referred_columns,
            ),
        )

        for foreign_key in sorted_foreign_keys:
            source_columns = ", ".join(
                foreign_key.constrained_columns
            )

            target_columns = ", ".join(
                foreign_key.referred_columns
            )

            target_schema = (
                foreign_key.referred_schema
                or table.schema_name
            )

            lines.append(
                f"- {source_columns} -> "
                f"{target_schema}."
                f"{foreign_key.referred_table}"
                f"({target_columns})"
            )
    else:
        lines.append("- None")

    content = "\n".join(lines).strip() + "\n"

    content_hash = sha256(
        content.encode("utf-8")
    ).hexdigest()

    return SchemaDocumentDraft(
        schema_name=table.schema_name,
        table_name=table.table_name,
        content=content,
        content_hash=content_hash,
    )


def build_schema_documents(
    tables: tuple[SchemaTable, ...],
) -> tuple[SchemaDocumentDraft, ...]:
    return tuple(
        build_schema_document(table)
        for table in tables
    )