from typing import Any

import dlt
from dlt.hub import run
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source(name="agent_traces")
def agent_traces_source(base_url: str = dlt.config.value) -> Any:
    """Load agent trace logs from the test-agent-traces-api.

    Args:
        base_url: API base URL. Auto-loaded from config.toml under [sources.agent_traces].

    Example:
        pipeline.run(agent_traces_source())
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "paginator": {
                "type": "offset",
                "limit": 1000,
                "offset_param": "offset",
                "limit_param": "limit",
                "total_path": "total",
            },
        },
        "resources": [
            {
                "name": "logs",
                "primary_key": "uuid",
                "endpoint": {
                    "path": "logs",
                    "data_selector": "logs",
                },
            },
        ],
    }

    yield from rest_api_resources(config)


@run.pipeline("agent_traces_pipeline")
def load_logs() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="agent_traces_pipeline",
        destination="playground",
        dataset_name="agent_traces",
    )

    load_info = pipeline.run(
        agent_traces_source(),
        write_disposition="replace",
    )
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    load_logs()
