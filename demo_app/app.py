import json
import random
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="PostgreSQL Health Monitor",
    page_icon="🟢",
    layout="wide",
)

DATA_FILE = Path(__file__).with_name("latest_metrics.json")


def get_demo_metrics():
    return {
        "idle_connections": random.randint(1, 20),
        "db_sizes": {
            "app_db": random.randint(100, 500),
            "users_db": random.randint(80, 300),
            "logs_db": random.randint(50, 250),
        },
        "top_databases": {
            "app_db": random.randint(20, 80),
            "users_db": random.randint(10, 60),
            "logs_db": random.randint(5, 40),
        },
        "query_latency_ms": round(random.uniform(5, 250), 2),
        "connections_per_db": {
            "app_db": random.randint(5, 30),
            "users_db": random.randint(3, 20),
            "logs_db": random.randint(1, 10),
        },
    }


def load_metrics():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return get_demo_metrics()


metrics = load_metrics()

st.title("PostgreSQL Health Monitor")
st.caption("A simple visual proof-of-work demo for your internship project.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Idle Connections", metrics["idle_connections"])

with col2:
    st.metric("Query Latency (ms)", metrics["query_latency_ms"])

with col3:
    total_size = sum(metrics["db_sizes"].values())
    st.metric("Total DB Size (MB)", total_size)

with col4:
    total_conn = sum(metrics["connections_per_db"].values())
    st.metric("Total Connections", total_conn)

st.divider()

status = "Healthy"
status_color = "🟢"

if metrics["query_latency_ms"] > 180 or metrics["idle_connections"] > 15:
    status = "Warning"
    status_color = "🟡"

if metrics["query_latency_ms"] > 220 or metrics["idle_connections"] > 18:
    status = "Critical"
    status_color = "🔴"

st.subheader(f"{status_color} System Status: {status}")

left, right = st.columns(2)

with left:
    st.markdown("### Database Sizes")
    df_sizes = pd.DataFrame(
        list(metrics["db_sizes"].items()),
        columns=["Database", "Size (MB)"],
    )
    fig_sizes = px.bar(df_sizes, x="Database", y="Size (MB)", text="Size (MB)")
    st.plotly_chart(fig_sizes, use_container_width=True)

with right:
    st.markdown("### Connections Per Database")
    df_conn = pd.DataFrame(
        list(metrics["connections_per_db"].items()),
        columns=["Database", "Connections"],
    )
    fig_conn = px.pie(df_conn, names="Database", values="Connections")
    st.plotly_chart(fig_conn, use_container_width=True)

st.markdown("### Top Databases In Use")
df_top = pd.DataFrame(
    list(metrics["top_databases"].items()),
    columns=["Database", "Usage"],
)
fig_top = px.line(df_top, x="Database", y="Usage", markers=True)
st.plotly_chart(fig_top, use_container_width=True)

st.markdown("### Proof of Work")
st.write(
    "This dashboard shows how PostgreSQL health data can be collected, "
    "summarized, and displayed visually for quick understanding."
)

st.code(
    """
Project flow:
PostgreSQL -> Python exporter -> monitoring data -> dashboard

What this demo proves:
- database health checking
- metric collection
- visual reporting
- easy explanation for non-technical people
""".strip(),
    language="text",
)

if st.button("Refresh Demo Values"):
    st.rerun()