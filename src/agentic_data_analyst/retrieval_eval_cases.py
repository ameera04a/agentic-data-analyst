from agentic_data_analyst.retrieval_evaluation import (
    RetrievalTestCase,
)


RETRIEVAL_TEST_CASES = (
    RetrievalTestCase(
        query=(
            "Where are customer payment "
            "installments stored?"
        ),
        relevant_tables=frozenset({
            "public.order_payments",
        }),
    ),

    RetrievalTestCase(
        query="Which table contains payment_sequential?",
        relevant_tables=frozenset({
            "public.order_payments",
        }),
    ),

    RetrievalTestCase(
        query=(
            "How did customers pay over "
            "several months?"
        ),
        relevant_tables=frozenset({
            "public.order_payments",
        }),
    ),

    RetrievalTestCase(
        query=(
            "Where are physical product "
            "dimensions and weight stored?"
        ),
        relevant_tables=frozenset({
            "public.products",
        }),
    ),

    RetrievalTestCase(
        query="Where is customer city and state stored?",
        relevant_tables=frozenset({
            "public.customers",
        }),
    ),

    RetrievalTestCase(
        query="Where can I find freight cost per item?",
        relevant_tables=frozenset({
            "public.order_items",
        }),
    ),

    RetrievalTestCase(
        query=(
            "Where can I find order delivery "
            "status and timestamps?"
        ),
        relevant_tables=frozenset({
            "public.orders",
        }),
    ),

    RetrievalTestCase(
        query=(
            "What tables are needed to analyze "
            "payment methods by customer state?"
        ),
        relevant_tables=frozenset({
            "public.customers",
            "public.orders",
            "public.order_payments",
        }),
    ),

    RetrievalTestCase(
        query=(
            "What tables are needed to analyze "
            "freight costs by product category?"
        ),
        relevant_tables=frozenset({
            "public.order_items",
            "public.products",
        }),
    ),
)