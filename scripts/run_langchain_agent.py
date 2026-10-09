from agentic_data_analyst.langchain_agent import (
    create_data_analyst_agent,
)

from agentic_data_analyst.langchain_run_summary import (
    summarize_agent_run,
)

def main() -> None:
    agent = create_data_analyst_agent()

    question = input(
        "Ask the LangChain data analyst: "
    ).strip()

    if not question:
        print("Question cannot be empty.")
        return

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    final_message = result["messages"][-1]

    print("\nAnswer:")
    print(final_message.content)

    summary = summarize_agent_run(
        result["messages"]
    )

    print("\nRun summary:")
    print("Model calls:", summary["model_calls"])
    print("Tool calls:", summary["tool_calls"])
    print("Tools used:", summary["tools_used"])
    print("Tool errors:", summary["tool_errors"])

if __name__ == "__main__":
    main()