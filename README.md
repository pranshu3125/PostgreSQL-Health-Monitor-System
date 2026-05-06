# PostgreSQL Metrics Exporter
## 🚀 Live Demo
👉 https://your-app-name.streamlit.app

This is a PostgreSQL Health Monitoring Dashboard built using Python and Streamlit.

This project is a Python-based Prometheus metrics exporter for PostgreSQL. It collects various metrics from a PostgreSQL database and pushes them to a Prometheus Pushgateway for monitoring. Then the metrics are represented graphically using Grafana.

## Table of Contents

- [Getting Started](#getting-started)
- [Adding/Updating Python Packages](#addingupdating-python-packages)
- [Local Development](#local-development)
- [Metrics Overview](#metrics-overview)
- [Adding New Metrics](#adding-new-metrics)

## Getting Started

### Prerequisites

Ensure the following installed on your system:

- Docker
- Docker Compose
- Helm
- Python 3.9 or higher
- Poetry

### Installation

   ```
   git clone https://github.com/your-repo/sc-ops-postgres-metrics-exporter.git
   cd sc-ops-postgres-metrics-exporter
   docker-compose up --d
   docker ps
   ```
   The following containers will be running postgres, prometheus, pushgateway, and sc-ops-postgres-metrics-exporter.
   
### Adding/Updating Python Packages

Poetry is the tool to insta
- Poetry used to manage project dependencies.
- Ruff used to lint and format code.
- Pytest used for unit tests.

### Local Development

- Setting up the Environment

1. Install Dependencies - This will create a pyproject.toml file in which the dependencies are listed.
```
poetry install
```

2. Initialize Poetry - This will create the poetry.lock
```
poetry init
```

3. Format the code
```
poetry run ruff format .
```

4. Run test
```
poetry run pytest \
```

### Running the Exporter Locally

- Setup Enviornment Variables
```
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=your_database
export POSTGRES_USER=your_user
export POSTGRES_PASSWORD=your_password
export PROMETHEUS_PUSHGATEWAY=http://localhost:9091
```

- Run the exporter
```
poetry run python postgres_metrics_exporter.py
```

### Metrics Overview

The exporter collects the following PostgreSQL metrics:

- Idle Connections (postgres_db_idle_connection): Number of idle connections in the PostgreSQL database.
- Database Sizes (postgres_db_name_sizes): Size of each database in the PostgreSQL instance.
- Top Databases (postgres_top_db_inuse): The most active databases in use.
- Query Latency (postgres_db_query_latency): Latency of specific queries.
- Connections per Database (postgres_connections_per_db): Number of connections per database.

These metrics are pushed to the Prometheus Pushgateway and can be visualized using Prometheus and Grafana.

### Adding New Metrics

To add new metrics to the exporter, follow these steps:

- Define the metrics - In postgres_metrics_exporter.py, define a new metric using the appropriate Prometheus metric type (e.g., Gauge, Counter):

```
self.new_metric = Gauge(
    "metric_name",
    "Metric description",
    labelnames=["label1", "label2"],
    registry=self.registry,
)
```
- Update Metrics Data - Create a new function in sc_ops_postgres_metrics_exporter.py to query the required data from PostgreSQL:

```
def get_new_metric_data(cursor):
    query = "SELECT ..."
    cursor.execute(query)
    data = cursor.fetchall()
    return {row[0]: row[1] for row in data}
```

- Push the metrics - Use the update_metric function to set the metric values and push them to the Pushgateway:

```
update_metric(
    get_new_metric_data,
    postgres_metrics_exporter.new_metric,
    cursor,
    postgres_metrics_exporter,
)
```

- Test the new metrics - Add tests in test_metrics.py to validate the new metric's data collection and pushing logic:

```
def test_get_new_metric_data(mock_cursor):
    mock_cursor.fetchall.return_value = [("label_value", 123)]
    result = get_new_metric_data(mock_cursor)
    assert result == {"label_value": 123}
```

- Run the tests using pytest to ensure everything works as expected.
```
poetry run pytest \
```

- The metrics dashboard will be added to sc-ops-grafana-configs

### Note - Alert Manager Configurations are left and in WIP will add the changes soon. Ticket for Ref: https://jira.storage.hpecorp.net/browse/CDSDO-9710




