import logging
from dataclasses import dataclass
from typing import Any

from groq import Groq

from agentic_data_analyst.config import settings
from agentic_data_analyst.tools.registry import (
    ToolRegistry,
)


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an agentic data analyst.

For questions about actual database data:

1. Use search_schema to discover the relevant tables
   when the required table names are not already known.

2. After search_schema identifies candidate tables,
   do not call search_schema again unless the previous
   results were genuinely insufficient.

3. Use get_table_schema to verify every table needed
   for the query, including columns, primary keys,
   foreign keys, and join relationships.

4. Once all required schema information has been
   verified, generate PostgreSQL and call execute_sql.
   Do not continue inspecting schema unnecessarily.

5. Base the final answer only on returned database
   results. Never invent numeric values.

Never invent table names, column names, relationships,
or database facts.

Only generate read-only analytical SQL. Never request
INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, or any
other operation that modifies database state.

If execute_sql returns an error, use the available
schema information and error details to correct the
query and retry when appropriate.

Keep queries focused on the user's question. Avoid
selecting unnecessary columns or large raw datasets.
""".strip()


@dataclass(frozen=True)
class AgentRunResult:
    answer: str
    iterations: int
    tool_calls: int


class ManualAgent:
    def __init__(
        self,
        client: Groq,
        tool_registry: ToolRegistry,
        model: str | None = None,
        max_iterations: int = 8,
    ) -> None:
        if max_iterations <= 0:
            raise ValueError(
                "max_iterations must be greater than zero."
            )

        self.client = client
        self.tool_registry = tool_registry
        self.model = model or settings.groq_model
        self.max_iterations = max_iterations

    def run(
        self,
        user_message: str,
    ) -> AgentRunResult:
        messages: list[Any] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        tool_call_count = 0

        for iteration in range(
            1,
            self.max_iterations + 1,
        ):
            response = (
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tool_registry.api_schemas,
                    tool_choice="auto",
                    temperature=0.1,
                )
            )

            assistant_message = (
                response.choices[0].message
            )

            messages.append(
                assistant_message
            )

            tool_calls = (
                assistant_message.tool_calls or []
            )

            if not tool_calls:
                answer = assistant_message.content

                if not answer:
                    raise RuntimeError(
                        "Model returned neither a "
                        "tool call nor a final answer."
                    )

                return AgentRunResult(
                    answer=answer,
                    iterations=iteration,
                    tool_calls=tool_call_count,
                )

            for tool_call in tool_calls:
                tool_call_count += 1

                tool_name = (
                    tool_call.function.name
                )

                logger.info(
                    "Executing tool=%s iteration=%d",
                    tool_name,
                    iteration,
                )

                tool_result = (
                    self.tool_registry.execute(
                        tool_name=tool_name,
                        arguments_json=(
                            tool_call.function.arguments
                        ),
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result,
                    }
                )

        raise RuntimeError(
            "Agent reached the maximum number "
            "of iterations without producing "
            "a final answer."
        )