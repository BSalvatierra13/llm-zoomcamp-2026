"""dlt filesystem pipeline: load Claude Code session logs (.jsonl) into DuckDB."""

import dlt
from dlt.hub import run
from dlt.sources.filesystem import filesystem, read_jsonl


@run.pipeline("claude_logs_pipeline")
def load_session_events() -> None:
    """Load raw Claude Code session log lines into DuckDB.

    bucket_url is read from .dlt/config.toml under [sources.filesystem].
    file_glob is set inline so it lives next to the code that depends on it.
    """
    pipeline = dlt.pipeline(
        pipeline_name="claude_logs_pipeline",
        destination="duckdb",
        dataset_name="claude_logs",
    )

    reader = (filesystem(file_glob="*.jsonl") | read_jsonl()).with_name("session_events")

    load_info = pipeline.run(reader, write_disposition="replace")
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_session_events()
