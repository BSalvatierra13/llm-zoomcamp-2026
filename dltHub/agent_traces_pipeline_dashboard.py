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
    pipeline = dlt.attach(
        "agent_traces_pipeline",
        destination="playground",
        dataset_name="agent_traces",
    )
    dataset = pipeline.dataset()
    return (dataset,)


@app.cell
def _(mo):
    mo.md("""
    # Agent Traces Usage Report
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
        FROM logs
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
    ).properties(title="Agent Traces Activity Over Time (hourly event count)")
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
            date_trunc('hour', timestamp) AS hour,
            SUM(usage__input_tokens) AS input_tokens,
            SUM(usage__output_tokens) AS output_tokens
        FROM logs
        WHERE timestamp IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """).df()
    df_chart2_melted = df_chart2.melt(
        id_vars=["hour"],
        value_vars=["input_tokens", "output_tokens"],
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
        FROM logs
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
    ## Tool Usage Frequency
    """)
    return


@app.cell
def _(dataset):
    df_chart4 = dataset("""
        SELECT
            name AS tool_name,
            COUNT(*) AS use_count
        FROM logs__message__content
        WHERE type = 'tool_use' AND name IS NOT NULL
        GROUP BY 1
        ORDER BY use_count DESC
    """).df()
    return (df_chart4,)


@app.cell
def _(alt, df_chart4):
    _chart = alt.Chart(df_chart4).mark_bar().encode(
        x=alt.X("use_count:Q", title="Uses"),
        y=alt.Y("tool_name:N", sort="-x", title="Tool"),
        tooltip=["tool_name:N", "use_count:Q"]
    ).properties(title="Tool Usage Frequency")
    _chart
    return


if __name__ == "__main__":
    app.run()
