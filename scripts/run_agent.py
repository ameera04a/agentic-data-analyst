import logging

from agentic_data_analyst.agent_loop import (
    ManualAgent,
)
from agentic_data_analyst.llm_client import (
    create_groq_client,
)
from agentic_data_analyst.tools.registry import (
    ToolRegistry,
)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(levelname)s "
            "%(name)s: %(message)s"
        ),
    )

    client = create_groq_client()
    tools = ToolRegistry()

    agent = ManualAgent(
        client=client,
        tool_registry=tools,
    )

    question = input(
        "Ask the data analyst: "
    ).strip()

    if not question:
        print("Question cannot be empty.")
        return

    result = agent.run(question)

    print("\nAnswer:")
    print(result.answer)

    print("\nRun metadata:")
    print(
        f"Iterations: {result.iterations}"
    )
    print(
        f"Tool calls: {result.tool_calls}"
    )


if __name__ == "__main__":
    main()