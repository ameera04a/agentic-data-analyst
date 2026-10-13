from agentic_data_analyst.analyst_graph import (
    build_analyst_graph,
)
from agentic_data_analyst.graph_state import (
    initial_analyst_state,
)


graph = build_analyst_graph()


def mock_generate_sql(state):
    return {
        "generated_sql": (
            "SELECT nonexistent_column "
            "FROM public.orders"
        )
    }


def mock_execute_sql(state):
    retry_count = state["retry_count"] + 1

    return {
        "query_result": {
            "is_error": True,
            "error": "Column does not exist",
        },
        "retry_count": retry_count,
    }

from langgraph.graph import END, START, StateGraph

from agentic_data_analyst.analyst_graph import (
    route_after_sql,
)
from agentic_data_analyst.graph_state import (
    AnalystState,
    initial_analyst_state,
)


def generate_sql(state: AnalystState) -> dict:
    return {
        "generated_sql": (
            "SELECT nonexistent_column "
            "FROM public.orders"
        )
    }


def execute_sql(state: AnalystState) -> dict:
    return {
        "query_result": {
            "is_error": True,
            "error": "Column does not exist",
        },
        "retry_count": state["retry_count"] + 1,
    }


def answer_question(state: AnalystState) -> dict:
    return {
        "final_answer": "Stopped after retry limit."
    }


workflow = StateGraph(AnalystState)

workflow.add_node("generate_sql", generate_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("answer_question", answer_question)

workflow.add_edge(START, "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    route_after_sql,
)

workflow.add_edge("answer_question", END)

graph = workflow.compile()

result = graph.invoke(
    initial_analyst_state("Test retry")
)

assert result["retry_count"] == 2
assert result["final_answer"] == "Stopped after retry limit."

print("Retry routing passed.")