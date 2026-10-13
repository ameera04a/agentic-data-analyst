from typing import Literal

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from agentic_data_analyst.graph_state import (
    AnalystState,
)
from agentic_data_analyst.graph_nodes import (
    AnalystNodes,
)


def route_after_sql(
    state: AnalystState,
) -> Literal["generate_sql", "answer_question"]:

    if not state["query_result"]["is_error"]:
        return "answer_question"

    if state["retry_count"] < 2:
        return "generate_sql"

    return "answer_question"


def build_analyst_graph():
    nodes = AnalystNodes()

    workflow = StateGraph(AnalystState)

    workflow.add_node(
        "discover_schema",
        nodes.discover_schema,
    )

    workflow.add_node(
        "generate_sql",
        nodes.generate_sql,
    )

    workflow.add_node(
        "execute_sql",
        nodes.execute_sql,
    )

    workflow.add_node(
        "answer_question",
        nodes.answer_question,
    )

    workflow.add_edge(
        START,
        "discover_schema",
    )

    workflow.add_edge(
        "discover_schema",
        "generate_sql",
    )

    workflow.add_edge(
        "generate_sql",
        "execute_sql",
    )

    workflow.add_conditional_edges(
        "execute_sql",
        route_after_sql,
        {
            "generate_sql": "generate_sql",
            "answer_question": "answer_question",
        },
    )

    workflow.add_edge(
        "answer_question",
        END,
    )

    return workflow.compile()