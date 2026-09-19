from agentic_data_analyst.schema_sync import (
    sync_schema_index,
)


def main() -> None:
    report = sync_schema_index()

    print("\nSchema index synchronization complete.")
    print(f"Inserted: {report.inserted}")
    print(f"Updated:  {report.updated}")
    print(f"Skipped:  {report.skipped}")
    print(f"Deleted:  {report.deleted}")


if __name__ == "__main__":
    main()