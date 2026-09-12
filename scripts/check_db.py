from agentic_data_analyst.db import (
    check_database_connection,
    check_pgvector_extension,
)


database_name = check_database_connection()
vector_version = check_pgvector_extension()

print(f"Database: {database_name}")
print(f"pgvector version: {vector_version}")