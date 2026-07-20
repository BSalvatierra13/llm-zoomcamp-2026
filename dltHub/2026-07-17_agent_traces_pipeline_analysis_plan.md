# Analysis Plan: agent_traces_pipeline

## Connection
- Pipeline: `agent_traces_pipeline`
- Dataset: `agent_traces` (dev_mode, dataset suffixed per run)
- Destination: duckdb (`.dlt/data/dev/agent_traces_pipeline.duckdb`)
- Source: REST API `GET /logs` at https://test-agent-traces-api-xt2e7ottma-ew.a.run.app

## Profile Summary
- `logs` — 20,000 rows. One row per log event (Claude Code transcript format: assistant/user messages), loaded via offset/limit pagination, capped at 20k of ~1,000,000 available.
- `logs__message__content` — 19,668 rows. Nested content blocks per message, including `type='tool_use'` rows with tool `name`.
- Time range observed: 2026-01-01T00:00:00 UTC to 2026-01-02T14:53:13 UTC. 2,476 distinct sessions.
- `type` has only 2 distinct values in this dataset: `assistant` (13,024), `user` (6,976) — no `system`/`tool_result` rows like the filesystem-sourced `claude_logs_pipeline`.
- Token usage is flat on `logs` (`usage__input_tokens`, `usage__output_tokens`) — there is no nested per-iteration usage table and **no cache token fields** (`cache_read_input_tokens` / `cache_creation_input_tokens` do not exist in this API's response shape).
- PII/sensitivity notes: `cwd` contains local filesystem paths — excluded from chart labels/tooltips, same as the filesystem-sourced report.

## Questions
- [x] What does activity look like over time (hourly event volume)?
- [x] How do token counts (input/output) trend over time?
- [x] What's the mix of event/message types (assistant vs user)?
- [x] Which tools are used most often (Read, Grep, WebFetch, Edit, ...)?

## Data Gaps
- Cache-efficiency chart (cache-read vs fresh input tokens) from the original `claude_logs_pipeline` report **cannot be replicated** — this API's `/logs` response has no cache token fields. Replaced with a tool-usage frequency chart instead (data available via `logs__message__content`).

## Chart 1
**Question:** What does activity look like over time (hourly event volume)?
**Type:** Line chart
**Source:** `logs`

```sql
SELECT
    date_trunc('hour', timestamp) AS hour,
    COUNT(*) AS event_count
FROM logs
WHERE timestamp IS NOT NULL
GROUP BY 1
ORDER BY 1
```

```python
alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("hour:T", title="Hour"),
    y=alt.Y("event_count:Q", title="Events"),
    tooltip=["hour:T", "event_count:Q"]
).properties(title="Agent Traces Activity Over Time (hourly event count)")
```

## Chart 2
**Question:** How do token counts (input/output) trend over time?
**Type:** Stacked area chart
**Source:** `logs`

```sql
SELECT
    date_trunc('hour', timestamp) AS hour,
    SUM(usage__input_tokens) AS input_tokens,
    SUM(usage__output_tokens) AS output_tokens
FROM logs
WHERE timestamp IS NOT NULL
GROUP BY 1
ORDER BY 1
```

```python
melted = df.melt(id_vars=["hour"], value_vars=["input_tokens", "output_tokens"], var_name="token_type", value_name="tokens")

alt.Chart(melted).mark_area().encode(
    x=alt.X("hour:T", title="Hour"),
    y=alt.Y("tokens:Q", title="Tokens", stack=True),
    color=alt.Color("token_type:N", title="Token type"),
    tooltip=["hour:T", "token_type:N", "tokens:Q"]
).properties(title="Token Usage Over Time")
```

## Chart 3
**Question:** What's the mix of event/message types?
**Type:** Bar chart
**Source:** `logs`

```sql
SELECT
    type,
    COUNT(*) AS event_count
FROM logs
GROUP BY 1
ORDER BY event_count DESC
```

```python
alt.Chart(df).mark_bar().encode(
    x=alt.X("event_count:Q", title="Event count"),
    y=alt.Y("type:N", sort="-x", title="Event type"),
    tooltip=["type:N", "event_count:Q"]
).properties(title="Event/Message Type Mix")
```

## Chart 4
**Question:** Which tools are used most often?
**Type:** Bar chart
**Source:** `logs__message__content`

```sql
SELECT
    name AS tool_name,
    COUNT(*) AS use_count
FROM logs__message__content
WHERE type = 'tool_use' AND name IS NOT NULL
GROUP BY 1
ORDER BY use_count DESC
```

```python
alt.Chart(df).mark_bar().encode(
    x=alt.X("use_count:Q", title="Uses"),
    y=alt.Y("tool_name:N", sort="-x", title="Tool"),
    tooltip=["tool_name:N", "use_count:Q"]
).properties(title="Tool Usage Frequency")
```
