from agentic_data_analyst.analyst_graph import (
    build_analyst_graph,
)
from agentic_data_analyst.graph_state import (
    initial_analyst_state,
)


def main() -> None:
    question = input(
        "Ask the LangGraph data analyst: "
    ).strip()

    if not question:
        print("Question cannot be empty.")
        return

    graph = build_analyst_graph()

    initial_state = initial_analyst_state(
        question
    )

    result = graph.invoke(initial_state)

    print("\nAnswer:")
    print(result["final_answer"])

    print("\nGenerated SQL:")
    print(result["generated_sql"])

    query_result = result["query_result"]

    print("\nExecution status:")
    print(
        "Success"
        if not query_result["is_error"]
        else "Failed"
    )

    print(
        "Failed SQL attempts:",
        result["retry_count"],
    )


if __name__ == "__main__":
    main()