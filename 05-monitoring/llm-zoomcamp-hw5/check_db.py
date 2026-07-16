import sqlite3

conn = sqlite3.connect("traces.db")
cur = conn.cursor()

cur.execute("""
    SELECT
        name,
        SUM(end_time - start_time) AS total_duration_ns
    FROM spans
    WHERE name != 'rag'
    GROUP BY name
""")

rows = cur.fetchall()
for name, total_ns in rows:
    total_ms = total_ns / 1_000_000  # nanosegundos a milisegundos
    print(f"{name}: {total_ms:.2f} ms")

conn.close()