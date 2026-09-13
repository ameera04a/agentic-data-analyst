from dataclasses import dataclass
from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

from agentic_data_analyst.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


@dataclass(frozen=True)
class CsvLoadSpec:
    filename: str
    table: str
    columns: tuple[str, ...]


LOAD_SPECS = (
    CsvLoadSpec(
        filename="olist_customers_dataset.csv",
        table="customers",
        columns=(
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
    ),
    CsvLoadSpec(
        filename="olist_products_dataset.csv",
        table="products",
        columns=(
            "product_id",
            "product_category_name",
            "product_name_length",
            "product_description_length",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
    ),
    CsvLoadSpec(
        filename="olist_orders_dataset.csv",
        table="orders",
        columns=(
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
    ),
    CsvLoadSpec(
        filename="olist_order_items_dataset.csv",
        table="order_items",
        columns=(
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
    ),
    CsvLoadSpec(
        filename="olist_order_payments_dataset.csv",
        table="order_payments",
        columns=(
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
    ),
)
def get_psycopg_dsn() -> str:
    url = make_url(settings.database_url)

    psycopg_url = url.set(
        drivername="postgresql",
    )

    return psycopg_url.render_as_string(
        hide_password=False,
    )

def ensure_tables_are_empty(
    connection: psycopg.Connection,
) -> None:
    with connection.cursor() as cursor:
        for spec in LOAD_SPECS:
            query = sql.SQL(
                "SELECT EXISTS (SELECT 1 FROM {} LIMIT 1);"
            ).format(
                sql.Identifier(spec.table)
            )

            cursor.execute(query)

            has_rows = cursor.fetchone()[0]

            if has_rows:
                raise RuntimeError(
                    f"Table '{spec.table}' already contains data. "
                    "Refusing to reload."
                )


def copy_csv_to_table(
    connection: psycopg.Connection,
    spec: CsvLoadSpec,
) -> None:
    csv_path = RAW_DATA_DIR / spec.filename

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {csv_path}"
        )

    column_identifiers = [
        sql.Identifier(column)
        for column in spec.columns
    ]

    copy_query = sql.SQL(
        """
        COPY {} ({})
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE
        )
        """
    ).format(
        sql.Identifier(spec.table),
        sql.SQL(", ").join(column_identifiers),
    )

    with (
        csv_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as csv_file,
        connection.cursor() as cursor,
        cursor.copy(copy_query) as copy,
    ):
        while chunk := csv_file.read(1024 * 1024):
            copy.write(chunk)



def load_olist_data() -> None:
    dsn = get_psycopg_dsn()

    with psycopg.connect(dsn) as connection:
        ensure_tables_are_empty(connection)

        for spec in LOAD_SPECS:
            print(
                f"Loading {spec.filename} "
                f"into {spec.table}..."
            )

            copy_csv_to_table(
                connection,
                spec,
            )

        print("Olist data loaded successfully.")