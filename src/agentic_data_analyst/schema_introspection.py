from dataclasses import dataclass

from sqlalchemy import inspect

from agentic_data_analyst.db import engine

@dataclass(frozen=True)
class SchemaColumn:
    name: str
    data_type: str
    nullable: bool


@dataclass(frozen=True)
class SchemaForeignKey:
    constrained_columns: tuple[str, ...]
    referred_schema: str | None
    referred_table: str
    referred_columns: tuple[str, ...]


@dataclass(frozen=True)
class SchemaTable:
    schema_name: str
    table_name: str
    columns: tuple[SchemaColumn, ...]
    primary_key: tuple[str, ...]
    foreign_keys: tuple[SchemaForeignKey, ...]


EXCLUDED_TABLES = {
    "alembic_version",
    "schema_documents",
}


def introspect_schema(
    schema_name: str = "public",
) -> tuple[SchemaTable, ...]:
    inspector = inspect(engine)

    table_names = inspector.get_table_names(
        schema=schema_name,
    )

    schema_tables = []

    for table_name in sorted(table_names):
        if table_name in EXCLUDED_TABLES:
            continue

        raw_columns = inspector.get_columns(
            table_name,
            schema=schema_name,
        )

        columns = tuple(
            SchemaColumn(
                name=column["name"],
                data_type=str(column["type"]),
                nullable=column["nullable"],
            )
            for column in raw_columns
        )

        pk_info = inspector.get_pk_constraint(
            table_name,
            schema=schema_name,
        )

        primary_key = tuple(
            pk_info.get("constrained_columns") or ()
        )

        raw_foreign_keys = inspector.get_foreign_keys(
            table_name,
            schema=schema_name,
        )

        foreign_keys = tuple(
            SchemaForeignKey(
                constrained_columns=tuple(
                    foreign_key.get("constrained_columns") or ()
                ),
                referred_schema=foreign_key.get(
                    "referred_schema"
                ),
                referred_table=foreign_key["referred_table"],
                referred_columns=tuple(
                    foreign_key.get("referred_columns") or ()
                ),
            )
            for foreign_key in raw_foreign_keys
        )

        schema_tables.append(
            SchemaTable(
                schema_name=schema_name,
                table_name=table_name,
                columns=columns,
                primary_key=primary_key,
                foreign_keys=foreign_keys,
            )
        )

    return tuple(schema_tables)