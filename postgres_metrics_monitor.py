# Copyright 2024-2025 Hewlett Packard Enterprise Development LP

"""
# This module defines the PostgresExporter class, which handles the creation and registration of
# PostgreSQL metrics, and provides methods to push these metrics to a Prometheus gateway.
"""

#!/usr/bin/python

from prometheus_client import Gauge, CollectorRegistry, push_to_gateway


class PostgresExporter:
    def __init__(self):
        # Create a custom registry to hold our metrics.
        self.registry = CollectorRegistry()

        # Gauge for idle connections, labeled by database name.
        self.db_idle_connection = Gauge(
            "postgres_db_idle_connection",
            "Size of the PostgreSQL database in bytes",
            labelnames=["db_name"],
            registry=self.registry,
        )

        # Gauge for long running queries/transactions, labeled by database name and query text.
        self.db_long_running_queries = Gauge(
            "postgres_long_running_queries_and_transactions",
            "Duration (in seconds) of long running transactions",
            labelnames=["db_name", "query_name"],
            registry=self.registry,
        )

        # Gauge for individual database sizes (in GB).
        self.db_name_sizes = Gauge(
            "postgres_db_name_sizes_gb",
            "DB size in the PostgreSQL database",
            labelnames=["db_name"],
            registry=self.registry,
        )

        # Gauge for total database size (in GB).
        self.db_total_size = Gauge(
            "postgres_db_name_sizes_total",
            "DB size in the PostgreSQL database",
            labelnames=["db_name"],
            registry=self.registry,
        )

        # Gauge for the top database (by number of active connections).
        self.top_db = Gauge(
            "postgres_top_db_inuse",
            "Top DB in use in the PostgreSQL database",
            labelnames=["db_name"],
            registry=self.registry,
        )

        # Gauge for query latency (in seconds), labeled by database and query.
        self.db_query_latency = Gauge(
            "postgres_db_query_latency",
            "Query latency in the PostgreSQL database",
            labelnames=["db_name", "query_name"],
            registry=self.registry,
        )

        # Gauge for number of connections per database.
        self.connections_per_db = Gauge(
            "postgres_connections_per_db",
            "Connections per DB in the PostgreSQL database",
            labelnames=["db_name"],
            registry=self.registry,
        )

        # Gauge for total number of connections.
        self.db_total_connections = Gauge(
            "postgres_total_connections",
            "Total number of database connections",
            labelnames=["db_name"],
            registry=self.registry,
        )

    def push_metric(self, url, job_name):
        """
        Pushes the collected metrics to the Prometheus Pushgateway.

        Args:
            url (str): The URL of the Prometheus Pushgateway.
            job_name (str): The job name under which the metrics will be pushed.
        """
        push_to_gateway(url, job=job_name, registry=self.registry)


# Usage:
# The PostgresExporter class is designed to collect various PostgreSQL metrics, such as the number of idle connections,
# database sizes, most active databases, query latencies, and the number of connections per database.
# These metrics are labeled for better identification and stored in a custom Prometheus registry.

# To push these metrics to a Prometheus push gateway, instantiate the PostgresExporter class,
# update the metrics as needed using the set or observe methods on each Gauge, and then call the push_metric() method
# with the appropriate gateway URL and job name. This allows the metrics to be monitored and visualized in Prometheus.
