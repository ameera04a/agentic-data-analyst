from agentic_data_analyst.analyst_graph import (
    route_after_sql,
)
from agentic_data_analyst.graph_state import (
    initial_analyst_state,
)


def test_success_routes_to_answer():
    state = initial_analyst_state("Test question")
    state["query_result"] = {"is_error": False}

    assert route_after_sql(state) == "answer_question"


def test_first_failure_routes_to_retry():
    state = initial_analyst_state("Test question")
    state["query_result"] = {"is_error": True}
    state["retry_count"] = 1

    assert route_after_sql(state) == "generate_sql"


def test_retry_limit_routes_to_answer():
    state = initial_analyst_state("Test question")
    state["query_result"] = {"is_error": True}
    state["retry_count"] = 2

    assert route_after_sql(state) == "answer_question"