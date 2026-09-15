from dataclasses import dataclass


@dataclass(frozen=True)
class TableBusinessMetadata:
    purpose: str
    use_cases: tuple[str, ...]
    column_descriptions: dict[str, str]


BUSINESS_METADATA: dict[str, TableBusinessMetadata] = {
    "public.customers": TableBusinessMetadata(
        purpose=(
            "Stores customer identifiers and customer location information."
        ),
        use_cases=(
            "Analyze customers by city or state.",
            "Connect customers to their orders.",
            "Identify repeat customers using customer_unique_id.",
        ),
        column_descriptions={
            "customer_id": (
                "Order-level customer identifier used to link a customer "
                "to the orders table."
            ),
            "customer_unique_id": (
                "Stable customer identifier that can identify the same "
                "customer across multiple orders."
            ),
            "customer_zip_code_prefix": (
                "Prefix of the customer's postal code."
            ),
            "customer_city": "Customer city.",
            "customer_state": "Customer state code.",
        },
    ),

    "public.orders": TableBusinessMetadata(
        purpose=(
            "Stores customer orders and timestamps describing the order "
            "lifecycle from purchase through delivery."
        ),
        use_cases=(
            "Analyze order volumes and order status.",
            "Analyze purchase and delivery timelines.",
            "Connect customers to payments and order items.",
        ),
        column_descriptions={
            "order_id": "Unique identifier for an order.",
            "customer_id": (
                "Customer identifier linking the order to customers."
            ),
            "order_status": (
                "Current or final status of the order."
            ),
            "order_purchase_timestamp": (
                "Date and time when the customer placed the order."
            ),
            "order_approved_at": (
                "Date and time when payment/order approval occurred."
            ),
            "order_delivered_carrier_date": (
                "Date and time when the order was handed to the carrier."
            ),
            "order_delivered_customer_date": (
                "Date and time when the order was delivered to the customer."
            ),
            "order_estimated_delivery_date": (
                "Estimated delivery date communicated for the order."
            ),
        },
    ),

    "public.products": TableBusinessMetadata(
        purpose=(
            "Stores product category information and physical product "
            "attributes such as dimensions and weight."
        ),
        use_cases=(
            "Analyze products by category.",
            "Analyze product size, weight and physical characteristics.",
            "Connect products to individual order items.",
        ),
        column_descriptions={
            "product_id": "Unique identifier for a product.",
            "product_category_name": "Category assigned to the product.",
            "product_name_length": (
                "Length of the product name in the source dataset."
            ),
            "product_description_length": (
                "Length of the product description in the source dataset."
            ),
            "product_photos_qty": (
                "Number of product photos associated with the product."
            ),
            "product_weight_g": "Product weight in grams.",
            "product_length_cm": "Product length in centimeters.",
            "product_height_cm": "Product height in centimeters.",
            "product_width_cm": "Product width in centimeters.",
        },
    ),

    "public.order_items": TableBusinessMetadata(
        purpose=(
            "Stores the individual products included in orders, including "
            "seller, price, freight cost and shipping-limit information."
        ),
        use_cases=(
            "Analyze product sales and item prices.",
            "Analyze freight costs.",
            "Connect orders with products and sellers.",
        ),
        column_descriptions={
            "order_id": (
                "Order containing this item."
            ),
            "order_item_id": (
                "Sequence number identifying an item within an order."
            ),
            "product_id": (
                "Product purchased in this order item."
            ),
            "seller_id": (
                "Seller responsible for this order item."
            ),
            "shipping_limit_date": (
                "Shipping deadline associated with this item."
            ),
            "price": "Selling price of the item.",
            "freight_value": (
                "Freight or shipping amount associated with the item."
            ),
        },
    ),

    "public.order_payments": TableBusinessMetadata(
        purpose=(
            "Stores payments associated with customer orders, including "
            "payment method, payment amount and installment information."
        ),
        use_cases=(
            "Analyze payment methods.",
            "Analyze payment amounts.",
            "Analyze installment behavior.",
            "Identify orders using multiple payment records.",
        ),
        column_descriptions={
            "order_id": (
                "Order associated with the payment."
            ),
            "payment_sequential": (
                "Sequence number used when an order has multiple "
                "payment records."
            ),
            "payment_type": (
                "Payment method used for the transaction."
            ),
            "payment_installments": (
                "Number of installments used for the payment."
            ),
            "payment_value": (
                "Value of the payment transaction."
            ),
        },
    ),
}