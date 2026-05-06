# Copyright 2024-2025 Hewlett Packard Enterprise Development LP


# This script collects PostgreSQL metrics such as database sizes, active connections, query latency,
# and idle connections, then pushes them to a Prometheus Pushgateway.

#!/usr/bin/python

import time
import os
import psycopg2  # PostgreSQL database adapter for Python
import re  # For cleaning label names
from postgres_metrics_monitor import (
    PostgresExporter,
)  # Custom exporter class to handle metrics


# Method to get idle connections in the PostgreSQL database
def get_idle_connections(cursor, postgres_metrics_exporter):
    try:
        query = """
            SELECT
                datname AS database_name,
                COUNT(*) AS idle_connections
            FROM
                pg_stat_activity
            WHERE
                state = 'idle'
                AND query NOT ILIKE '<IDLE>'
            GROUP BY
                datname;
        """
        cursor.execute(query)
        idle_connections = cursor.fetchall()
        # Convert list of tuples into a dictionary {database_name: idle_connections}
        return {row[0]: row[1] for row in idle_connections}
    except psycopg2.Error as e:
        print(f"Error in get_idle_connections: {e}")
        return {}


# Method to get long running queries and transactions in the PostgreSQL database
def get_long_running_queries_and_transactions(cursor, postgres_metrics_exporter):
    try:
        query = """
            SELECT 
                datname AS database_name,
                application_name,
                wait_event_type,
                wait_event,
                age(clock_timestamp(), xact_start) AS transaction_duration,
                age(clock_timestamp(), query_start) AS query_duration,
                xact_start,
                query_start,
                query
            FROM pg_stat_activity
            WHERE state = 'active'
              AND (
                   (xact_start IS NOT NULL AND clock_timestamp() - xact_start > interval '1 minute')
                   OR (clock_timestamp() - query_start > interval '1 minute')
                  )
            ORDER BY transaction_duration DESC, query_duration DESC;
        """
        cursor.execute(query)
        long_running_data = cursor.fetchall()
        print("Debug: Fetched long running queries data:", long_running_data)
        long_running_queries = {}
        for row in long_running_data:
            # row[0] = database_name, row[8] = query text.
            query_text = row[8]
            db_name = row[0]
            long_running_queries[query_text] = {
                "database_name": db_name,
                "transaction_duration": row[4].total_seconds(),
                "query_duration": row[5].total_seconds(),
            }
        return long_running_queries
    except psycopg2.Error as e:
        print(f"Error in get_long_running_queries_and_transactions: {e}")
        return {}


# Method to get the total size of the DB
def get_total_db_size(cursor, postgres_metrics_exporter):
    try:
        query = """
            SELECT
                SUM(pg_database_size(datname)) / 1024 / 1024 / 1024 AS total_size_gb
            FROM
                pg_database
        """
        cursor.execute(query)
        total_size_gb = cursor.fetchone()[0]
        return {"total_size": float(total_size_gb)}
    except psycopg2.Error as e:
        print(f"Error in get_total_db_size: {e}")
        return 0.0


# Method to get the sizes of all databases in the PostgreSQL instance
def get_db_sizes(cursor, postgres_metrics_exporter):
    try:
        query = """
            SELECT
                datname AS database_name,
                pg_database_size(datname) / 1024 / 1024 /1024 AS size_gb
            FROM
                pg_database
        """
        cursor.execute(query)
        return {row[0]: float(row[1]) for row in cursor.fetchall()}
    except psycopg2.Error as e:
        print(f"Error in get_db_sizes: {e}")
        return {}


# Method to get the top databases by the number of active connections
def get_top_databases_by_connections(cursor, postgres_metrics_exporter):
    try:
        query = """
            SELECT datname, COUNT(*) AS active_connections
            FROM pg_stat_activity
            GROUP BY datname
            ORDER BY COUNT(*) DESC;
        """
        cursor.execute(query)
        return {row[0]: row[1] for row in cursor.fetchall()}
    except psycopg2.Error as e:
        print(f"Error in get_top_databases_by_connections: {e}")
        return {}


# Method to get query latency for active queries in the PostgreSQL instance
def get_query_latency(cursor, metric_name, postgres_metrics_exporter):
    try:
        print("get_query_latency ........")
        top_databases = get_top_databases_by_connections(
            cursor, postgres_metrics_exporter
        )
        print(f"Top databases: {top_databases}")
        query = """
            SELECT 
                now() - query_start AS query_latency,
                pid,
                usename,
                datname,
                query,
                state,
                backend_start,
                application_name,
                EXTRACT(EPOCH FROM (now() - query_start)) AS duration_ms
            FROM 
                pg_stat_activity
            WHERE
                state = 'active';
        """
        cursor.execute(query)
        results = cursor.fetchall()
        print("Results fetched from cursor:", results)
        data = {}
        for row in results:
            query_text = row[4]
            duration_ms = float(row[8])
            database_name = row[3]
            if database_name in top_databases:
                data[query_text] = {
                    "duration_ms": duration_ms,
                    "database_name": database_name,
                    "query": query_text,
                }
        print("Data to be returned:", data)
        return data
    except psycopg2.Error as e:
        print(f"Error in get_query_latency: {e}")
        return {}


# Method to get the number of connections per database in the PostgreSQL instance
def get_connections_per_db(cursor, postgres_metrics_exporter):
    try:
        query = "SELECT datname, numbackends FROM pg_stat_database"
        cursor.execute(query)
        return {row[0]: row[1] for row in cursor.fetchall()}
    except psycopg2.Error as e:
        print(f"Error in get_connections_per_db: {e}")
        return {}


# Method to get the total number of connections across all databases in PostgreSQL
def get_total_connections(cursor, postgres_metrics_exporter):
    try:
        query = """
            SELECT SUM(numbackends) AS total_connections
            FROM pg_stat_database;
        """
        cursor.execute(query)
        total_connections = cursor.fetchone()[0]
        return (
            {"total_connections": float(total_connections)}
            if total_connections is not None
            else {}
        )
    except psycopg2.Error as e:
        print(f"Error in get_total_connections: {e}")
        return {}


# Updated general method to update a specific metric based on the function provided
def update_metric(
    func, metric_name, cursor, postgres_metrics_exporter, *args, **kwargs
):
    """
    Calls the given metric function to collect data, and then updates the corresponding Prometheus Gauge.

    For the long running queries metric, if no qualifying queries are found,
    it sets a default metric value (0) with labels "none".

    For metrics that require two labels (db_name, query_name), we clean the labels to match Prometheus naming conventions.
    """
    print("func .....", func)
    print("metric_name .....", metric_name)
    print("cursor .....", cursor)

    # Check if the function expects a "metric_name" parameter
    if "metric_name" in func.__code__.co_varnames:
        db_conn = func(cursor, postgres_metrics_exporter, metric_name, *args, **kwargs)
    else:
        db_conn = func(cursor, postgres_metrics_exporter, *args, **kwargs)

    if db_conn is not None:
        # Branch for long running queries (requires two labels: db_name and query_name)
        if metric_name == postgres_metrics_exporter.db_long_running_queries:
            if not db_conn:
                print(
                    "Debug - No long running queries found, setting default value to 0."
                )
                metric_name.labels(db_name="none", query_name="none").set(0)
            else:
                for query_text, data in db_conn.items():
                    db_name = data["database_name"]
                    # Using transaction_duration as the metric value; you could also use query_duration if desired.
                    duration = data["transaction_duration"]
                    # Clean label values to follow Prometheus conventions (only letters, numbers, and underscores)
                    db_label = re.sub(r"[^a-zA-Z0-9_]", "_", db_name)
                    query_label = re.sub(r"[^a-zA-Z0-9_]", "_", query_text)
                    print(
                        f"Debug - Long Running Query Metric: DB: {db_label}, Query: {query_label}, Duration: {duration}"
                    )
                    metric_name.labels(db_name=db_label, query_name=query_label).set(
                        duration
                    )
        # Branch for query latency metric (also requires two labels)
        elif metric_name == postgres_metrics_exporter.db_query_latency:
            for name, value in db_conn.items():
                print("name...", name)
                print("value..", value)
                database_name = re.sub(
                    r"[^a-zA-Z0-9_]", "_", value["database_name"].replace(" ", "_")
                )
                query_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(name).replace(" ", "_"))
                metric_name.labels(db_name=database_name, query_name=query_name).set(
                    value["duration_ms"] / 1000
                )
        # Branch for all other metrics (with a single label: db_name)
        else:
            for name, value in db_conn.items():
                label_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(name))
                metric_name.labels(db_name=label_name).set(value)


# Main function to connect to the PostgreSQL database, gather metrics, and push them to the Prometheus Pushgateway
def main():
    """
    Main function that:
      - Reads environment variables for database and push gateway connection.
      - Connects to PostgreSQL.
      - Collects all metrics.
      - Pushes the metrics to the configured Prometheus Pushgateway.
    """
    prometheus_pushgateway = os.environ.get("PROMETHEUS_PUSHGATEWAY")
    postgres_host = os.environ.get("POSTGRES_HOST")
    postgres_port = os.environ.get("POSTGRES_PORT")
    postgres_db = os.environ.get("POSTGRES_DB")
    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    ENVIRONMENT = os.environ.get("ENVIRONMENT")

    # Delay if running locally to ensure the database is ready.
    if ENVIRONMENT == "local":
        time.sleep(60)

    # Initialize the PostgresExporter instance which holds the Prometheus metrics.
    postgres_metrics_exporter = PostgresExporter()
    print("Collection in registry.........")

    # Connect to PostgreSQL and collect metrics using a context manager.
    with psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        database=postgres_db,
        user=postgres_user,
        password=postgres_password,
    ) as conn:
        with conn.cursor() as cursor:
            print("Connection is established.......")
            update_metric(
                get_db_sizes,
                postgres_metrics_exporter.db_name_sizes,
                cursor,
                postgres_metrics_exporter,
            )
            update_metric(
                get_total_db_size,
                postgres_metrics_exporter.db_total_size,
                cursor,
                postgres_metrics_exporter,
            )
            update_metric(
                get_top_databases_by_connections,
                postgres_metrics_exporter.top_db,
                cursor,
                postgres_metrics_exporter,
            )
            update_metric(
                get_query_latency,
                postgres_metrics_exporter.db_query_latency,
                cursor,
                postgres_metrics_exporter,
            )
            update_metric(
                get_connections_per_db,
                postgres_metrics_exporter.connections_per_db,
                cursor,
                postgres_metrics_exporter,
            )
            update_metric(
                get_total_connections,
                postgres_metrics_exporter.db_total_connections,
                cursor,
                postgres_metrics_exporter,
            )
            update_metric(
                get_idle_connections,
                postgres_metrics_exporter.db_idle_connection,
                cursor,
                postgres_metrics_exporter,
            )
            update_metric(
                get_long_running_queries_and_transactions,
                postgres_metrics_exporter.db_long_running_queries,
                cursor,
                postgres_metrics_exporter,
            )
            print("gathered data.........")
            postgres_metrics_exporter.push_metric(
                prometheus_pushgateway, "postgres_metrics"
            )
            print("Pushing to push gateway.........")


if __name__ == "__main__":
    main()
