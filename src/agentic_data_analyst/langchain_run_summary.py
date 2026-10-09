import json
from typing import Any

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)


def summarize_agent_run(
    messages: list[Any],
) -> dict[str, Any]:

    model_calls = sum(
        isinstance(message, AIMessage)
        for message in messages
    )

    tool_names = []

    for message in messages:
        if isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                tool_names.append(
                    tool_call["name"]
                )

    tool_errors = 0

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        try:
            data = json.loads(message.content)
        except (TypeError, ValueError):
            continue

        if isinstance(data, dict) and data.get("is_error"):
            tool_errors += 1

    return {
        "model_calls": model_calls,
        "tool_calls": len(tool_names),
        "tools_used": tool_names,
        "tool_errors": tool_errors,
    }