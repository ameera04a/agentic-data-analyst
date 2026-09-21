from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects import postgresql
from sqlalchemy import (
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from agentic_data_analyst.embedding_config import (
    EMBEDDING_CONFIG,
)

class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )

    customer_unique_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    customer_zip_code_prefix: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    customer_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    customer_state: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )

    product_category_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    product_name_length: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product_description_length: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product_photos_qty: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product_weight_g: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product_length_cm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product_height_cm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product_width_cm: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"),
        nullable=False,
    )

    order_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    order_purchase_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    order_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    order_delivered_carrier_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    order_delivered_customer_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    order_estimated_delivery_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id"),
        primary_key=True,
    )

    order_item_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.product_id"),
        nullable=False,
    )

    seller_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    shipping_limit_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    freight_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )


class OrderPayment(Base):
    __tablename__ = "order_payments"

    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id"),
        primary_key=True,
    )

    payment_sequential: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    payment_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    payment_installments: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    payment_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )




class SchemaDocument(Base):
    __tablename__ = "schema_documents"

    __table_args__ = (
        UniqueConstraint(
            "schema_name",
            "table_name",
            name="uq_schema_documents_schema_table",
        ),
        Index(
            "ix_schema_documents_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
    )
    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english'::regconfig, content)",
            persisted=True,
        ),
        nullable=False,
    )
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    schema_name: Mapped[str] = mapped_column(
        String(63),
        nullable=False,
    )

    table_name: Mapped[str] = mapped_column(
        String(63),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_CONFIG.dimension),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )