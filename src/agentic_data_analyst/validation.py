from pathlib import Path

from sqlalchemy import text

from agentic_data_analyst.db import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


TABLE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
}



def count_csv_rows(filename: str) -> int:
    path = RAW_DATA_DIR / filename

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return sum(1 for _ in file) - 1



def count_database_rows(table_name: str) -> int:
    allowed_tables = set(TABLE_FILES)

    if table_name not in allowed_tables:
        raise ValueError(
            f"Unexpected table name: {table_name}"
        )

    query = text(
        f"SELECT COUNT(*) FROM {table_name};"
    )

    with engine.connect() as connection:
        result = connection.execute(query)

        return result.scalar_one()



def validate_row_counts() -> bool:
    all_match = True

    for table, filename in TABLE_FILES.items():
        csv_count = count_csv_rows(filename)
        database_count = count_database_rows(table)

        matches = csv_count == database_count

        print(
            f"{table}: "
            f"CSV={csv_count}, "
            f"DB={database_count}, "
            f"match={matches}"
        )

        if not matches:
            all_match = False

    return all_match



def check_orphan_records() -> dict[str, int]:
    queries = {
        "orders_without_customer": """
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
        """,

        "items_without_order": """
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL;
        """,

        "items_without_product": """
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN products p
                ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL;
        """,

        "payments_without_order": """
            SELECT COUNT(*)
            FROM order_payments op
            LEFT JOIN orders o
                ON op.order_id = o.order_id
            WHERE o.order_id IS NULL;
        """,
    }

    results = {}

    with engine.connect() as connection:
        for name, query in queries.items():
            count = connection.execute(
                text(query)
            ).scalar_one()

            results[name] = count

    return results


def check_invalid_numeric_values() -> dict[str, int]:
    queries = {
        "negative_product_prices": """
            SELECT COUNT(*)
            FROM order_items
            WHERE price < 0;
        """,

        "negative_freight_values": """
            SELECT COUNT(*)
            FROM order_items
            WHERE freight_value < 0;
        """,

        "negative_payment_values": """
            SELECT COUNT(*)
            FROM order_payments
            WHERE payment_value < 0;
        """,
    }

    results = {}

    with engine.connect() as connection:
        for name, query in queries.items():
            count = connection.execute(
                text(query)
            ).scalar_one()

            results[name] = count

    return results



def run_data_validation() -> None:
    print("\nROW COUNT VALIDATION")
    print("-" * 40)

    row_counts_ok = validate_row_counts()

    print("\nFOREIGN KEY VALIDATION")
    print("-" * 40)

    orphan_results = check_orphan_records()

    for check, count in orphan_results.items():
        print(f"{check}: {count}")

    print("\nNUMERIC VALIDATION")
    print("-" * 40)

    numeric_results = check_invalid_numeric_values()

    for check, count in numeric_results.items():
        print(f"{check}: {count}")

    orphan_checks_ok = all(
        count == 0
        for count in orphan_results.values()
    )

    numeric_checks_ok = all(
        count == 0
        for count in numeric_results.values()
    )

    if not (
        row_counts_ok
        and orphan_checks_ok
        and numeric_checks_ok
    ):
        raise RuntimeError(
            "Data validation failed."
        )

    print("\nAll data validation checks passed.")

