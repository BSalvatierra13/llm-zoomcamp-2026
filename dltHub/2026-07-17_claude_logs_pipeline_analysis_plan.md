# Analysis Plan: claude_logs_pipeline

## Connection
- Pipeline: `claude_logs_pipeline`
- Dataset: `claude_logs` (dev_mode, dataset suffixed per run)
- Destination: duckdb (`.dlt/data/dev/claude_logs_pipeline.duckdb`)

## Profile Summary
- `session_events` — 1116 rows. Core event log: one row per session event (assistant/user/system messages, tool calls, attachments, etc).
- `session_events__message__content` — 663 rows. Nested content blocks per message, including `type='tool_use'` rows with tool `name`.
- `session_events__message__usage__iterations` — 444 rows. Per-iteration token usage (input/output/cache tokens), parent-linked to `session_events` via `_dlt_parent_id` = `session_events._dlt_id`.
- Time range observed: 2026-06-09T16:21 UTC to 2026-06-11T16:45 UTC. 1 session, 2 distinct `cwd` (project directories).
- Anomaly notes: `message__model` / `message__role` are blank for non-assistant event types (user/system/etc rows don't carry a model) — expected, not a data quality issue. Several `message__diagnostics`/`message__container`/`message__stop_details` columns are entirely null in this dataset (not materialized).
- PII/sensitivity notes: `cwd` and various `tool_use_result__file__file_path` / `tool_use_result__file_path` columns contain local filesystem paths. Excluded from chart labels/tooltips.

## Questions
- [x] What does activity look like over time (hourly event volume)?
- [x] How do token counts (input/output/cache) trend over time?
- [x] What's the mix of event/message types (assistant, user, tool, system, etc)?
- [x] How much of input token usage is served from cache vs fresh?
- [ ] Which tools are used most often (Edit, Bash, Read, PowerShell, ...)?
- [ ] How does activity split across the 2 projects (cwd)?

## Data Gaps
None identified for the charted questions.

## Chart 1
**Question:** What does activity look like over time (hourly event volume)?
**Type:** Line chart
**Source:** `session_events`

```sql
SELECT
    date_trunc('hour', timestamp) AS hour,
    COUNT(*) AS event_count
FROM session_events
WHERE timestamp IS NOT NULL
GROUP BY 1
ORDER BY 1
```

```python
alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("hour:T", title="Hour"),
    y=alt.Y("event_count:Q", title="Events"),
    tooltip=["hour:T", "event_count:Q"]
).properties(title="Claude Code Activity Over Time (hourly event count)")
```

## Chart 2
**Question:** How do token counts (input/output/cache) trend over time?
**Type:** Stacked area chart
**Source:** `session_events` joined to `session_events__message__usage__iterations`

```sql
SELECT
    date_trunc('hour', se.timestamp) AS hour,
    SUM(it.input_tokens) AS input_tokens,
    SUM(it.output_tokens) AS output_tokens,
    SUM(it.cache_read_input_tokens) AS cache_read_tokens,
    SUM(it.cache_creation_input_tokens) AS cache_creation_tokens
FROM session_events se
JOIN session_events__message__usage__iterations it
    ON it._dlt_parent_id = se._dlt_id
GROUP BY 1
ORDER BY 1
```

```python
melted = df.melt(id_vars=["hour"], value_vars=["input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens"], var_name="token_type", value_name="tokens")

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
**Source:** `session_events`

```sql
SELECT
    type,
    COUNT(*) AS event_count
FROM session_events
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
**Question:** How much of input token usage is served from cache vs fresh?
**Type:** Stacked bar chart
**Source:** `session_events` joined to `session_events__message__usage__iterations`

```sql
SELECT
    date_trunc('hour', se.timestamp) AS hour,
    SUM(it.cache_read_input_tokens) AS cache_read_tokens,
    SUM(it.input_tokens) AS fresh_input_tokens
FROM session_events se
JOIN session_events__message__usage__iterations it
    ON it._dlt_parent_id = se._dlt_id
GROUP BY 1
ORDER BY 1
```

```python
melted = df.melt(id_vars=["hour"], value_vars=["cache_read_tokens", "fresh_input_tokens"], var_name="source", value_name="tokens")

alt.Chart(melted).mark_bar().encode(
    x=alt.X("hour:T", title="Hour"),
    y=alt.Y("tokens:Q", title="Input tokens", stack="normalize"),
    color=alt.Color("source:N", title="Source"),
    tooltip=["hour:T", "source:N", "tokens:Q"]
).properties(title="Cache Efficiency: Cache-Read vs Fresh Input Tokens")
```
