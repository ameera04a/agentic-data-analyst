from typing import Any, TypedDict


class AnalystState(TypedDict):
    question: str
    schema_context: list[dict[str, Any]]
    generated_sql: str
    query_result: dict[str, Any]
    retry_count: int
    final_answer: str


def initial_analyst_state(
    question: str,
) -> AnalystState:
    return {
        "question": question,
        "schema_context": [],
        "generated_sql": "",
        "query_result": {},
        "retry_count": 0,
        "final_answer": "",
    }