import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import dlt

    return alt, dlt, mo


@app.cell
def _(dlt):
    pipeline = dlt.attach("claude_logs_pipeline")
    dataset = pipeline.dataset()
    return (dataset,)


@app.cell
def _(mo):
    mo.md("""
    # Claude Code Usage Report
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Activity Over Time
    """)
    return


@app.cell
def _(dataset):
    df_chart1 = dataset("""
        SELECT
            date_trunc('hour', timestamp) AS hour,
            COUNT(*) AS event_count
        FROM session_events
        WHERE timestamp IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """).df()
    return (df_chart1,)


@app.cell
def _(alt, df_chart1):
    _chart = alt.Chart(df_chart1).mark_line(point=True).encode(
        x=alt.X("hour:T", title="Hour"),
        y=alt.Y("event_count:Q", title="Events"),
        tooltip=["hour:T", "event_count:Q"]
    ).properties(title="Claude Code Activity Over Time (hourly event count)")
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Token Usage Over Time
    """)
    return


@app.cell
def _(dataset):
    df_chart2 = dataset("""
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
    """).df()
    df_chart2_melted = df_chart2.melt(
        id_vars=["hour"],
        value_vars=["input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens"],
        var_name="token_type",
        value_name="tokens",
    )
    return (df_chart2_melted,)


@app.cell
def _(alt, df_chart2_melted):
    _chart = alt.Chart(df_chart2_melted).mark_area().encode(
        x=alt.X("hour:T", title="Hour"),
        y=alt.Y("tokens:Q", title="Tokens", stack=True),
        color=alt.Color("token_type:N", title="Token type"),
        tooltip=["hour:T", "token_type:N", "tokens:Q"]
    ).properties(title="Token Usage Over Time")
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Event / Message Type Mix
    """)
    return


@app.cell
def _(dataset):
    df_chart3 = dataset("""
        SELECT
            type,
            COUNT(*) AS event_count
        FROM session_events
        GROUP BY 1
        ORDER BY event_count DESC
    """).df()
    return (df_chart3,)


@app.cell
def _(alt, df_chart3):
    _chart = alt.Chart(df_chart3).mark_bar().encode(
        x=alt.X("event_count:Q", title="Event count"),
        y=alt.Y("type:N", sort="-x", title="Event type"),
        tooltip=["type:N", "event_count:Q"]
    ).properties(title="Event/Message Type Mix")
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Cache Efficiency
    """)
    return


@app.cell
def _(dataset):
    df_chart4 = dataset("""
        SELECT
            date_trunc('hour', se.timestamp) AS hour,
            SUM(it.cache_read_input_tokens) AS cache_read_tokens,
            SUM(it.input_tokens) AS fresh_input_tokens
        FROM session_events se
        JOIN session_events__message__usage__iterations it
            ON it._dlt_parent_id = se._dlt_id
        GROUP BY 1
        ORDER BY 1
    """).df()
    df_chart4_melted = df_chart4.melt(
        id_vars=["hour"],
        value_vars=["cache_read_tokens", "fresh_input_tokens"],
        var_name="source",
        value_name="tokens",
    )
    return (df_chart4_melted,)


@app.cell
def _(alt, df_chart4_melted):
    _chart = alt.Chart(df_chart4_melted).mark_bar().encode(
        x=alt.X("hour:T", title="Hour"),
        y=alt.Y("tokens:Q", title="Input tokens", stack="normalize"),
        color=alt.Color("source:N", title="Source"),
        tooltip=["hour:T", "source:N", "tokens:Q"]
    ).properties(title="Cache Efficiency: Cache-Read vs Fresh Input Tokens")
    _chart
    return


if __name__ == "__main__":
    app.run()
