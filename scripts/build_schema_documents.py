from agentic_data_analyst.schema_documents import (
    build_schema_documents,
)
from agentic_data_analyst.schema_introspection import (
    introspect_schema,
)


def main() -> None:
    tables = introspect_schema()

    documents = build_schema_documents(tables)

    for document in documents:
        print("=" * 80)
        print(document.content)
        print(
            f"SHA-256: {document.content_hash}"
        )


if __name__ == "__main__":
    main()