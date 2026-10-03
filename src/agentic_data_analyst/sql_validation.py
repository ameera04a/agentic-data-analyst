from sqlglot import exp, parse
from sqlglot.errors import ParseError


FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.Merge,
    exp.Into,
)


def validate_readonly_sql(
    sql: str,
) -> str:
    cleaned_sql = sql.strip()

    if not cleaned_sql:
        raise ValueError(
            "SQL query cannot be empty."
        )

    try:
        statements = parse(
            cleaned_sql,
            read="postgres",
        )
    except ParseError as exc:
        raise ValueError(
            f"SQL could not be parsed: {exc}"
        ) from exc

    if len(statements) != 1:
        raise ValueError(
            "Exactly one SQL statement is allowed."
        )

    statement = statements[0]

    if not isinstance(
        statement,
        exp.Query,
    ):
        raise ValueError(
            "Only read-only SELECT queries "
            "are allowed."
        )

    for forbidden_type in FORBIDDEN_EXPRESSIONS:
        if statement.find(
            forbidden_type
        ) is not None:
            raise ValueError(
                "SQL contains a forbidden "
                "write operation."
            )

    return statement.sql(
        dialect="postgres"
    )