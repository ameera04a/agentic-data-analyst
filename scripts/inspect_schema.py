from agentic_data_analyst.schema_introspection import (
    introspect_schema,
)


def main() -> None:
    tables = introspect_schema()

    for table in tables:
        print(f"\n{table.schema_name}.{table.table_name}")

        print("  Columns:")
        for column in table.columns:
            print(
                f"    - {column.name}: "
                f"{column.data_type}, "
                f"nullable={column.nullable}"
            )

        print(
            f"  Primary key: "
            f"{', '.join(table.primary_key) or 'None'}"
        )

        print("  Foreign keys:")
        if not table.foreign_keys:
            print("    - None")

        for foreign_key in table.foreign_keys:
            source = ", ".join(
                foreign_key.constrained_columns
            )

            target = ", ".join(
                foreign_key.referred_columns
            )

            target_schema = (
                foreign_key.referred_schema
                or table.schema_name
            )

            print(
                f"    - {source} -> "
                f"{target_schema}."
                f"{foreign_key.referred_table}"
                f"({target})"
            )


if __name__ == "__main__":
    main()