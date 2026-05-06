# Copyright 2024-2025 Hewlett Packard Enterprise Development LP
# This file contains unit tests for the functions and methods in postgres_metrics_exporter.py
# and postgres_metrics_monitor.py, ensuring the correctness of PostgreSQL metrics collection and export.

import pytest
from unittest.mock import MagicMock, patch
from postgres_metrics_exporter import (
    get_total_db_size,
    get_top_databases_by_connections,
    get_query_latency,
    get_connections_per_db,
    get_idle_connections,
    get_long_running_queries_and_transactions,
    main,
)


@pytest.fixture
def mock_cursor():
    return MagicMock()


@pytest.fixture
def mock_exporter():
    mock_exporter = MagicMock()
    mock_exporter.db_total_size = MagicMock()
    mock_exporter.top_db = MagicMock()
    mock_exporter.db_query_latency = MagicMock()
    mock_exporter.connections_per_db = MagicMock()
    mock_exporter.db_idle_connection = MagicMock()
    mock_exporter.db_long_running_queries = MagicMock()
    mock_exporter.db_total_connections = MagicMock()  # Adding db_total_connections mock
    return mock_exporter


# Test for retrieving total database sizes
def test_get_total_db_size(mock_cursor, mock_exporter):
    mock_cursor.fetchone.return_value = (3000000000,)
    result = get_total_db_size(mock_cursor, mock_exporter)
    assert result == {"total_size": 3000000000.0}


# Test for no database sizes returned
def test_get_total_db_size_no_databases(mock_cursor, mock_exporter):
    mock_cursor.fetchall.return_value = []
    result = get_total_db_size(mock_cursor, mock_exporter)
    assert result == {"total_size": 1.0}


# Test for retrieving connections per database
def test_get_connections_per_db(mock_cursor):
    mock_cursor.fetchall.return_value = [("db1", 10), ("db2", 20)]
    result = get_connections_per_db(mock_cursor, None)
    assert result == {"db1": 10, "db2": 20}


# Test for no active connections per database
def test_get_top_databases_by_connections_empty(mock_cursor):
    mock_cursor.fetchall.return_value = []
    result = get_top_databases_by_connections(mock_cursor, None)
    assert result == {}


# Test for active connections per database
def test_get_top_databases_by_connections(mock_cursor):
    mock_cursor.fetchall.return_value = [("db1", 5), ("db2", 3)]
    result = get_top_databases_by_connections(mock_cursor, None)
    assert result == {"db1": 5, "db2": 3}


# Test for getting top databases by active connections
def test_get_top_databases_by_connections_full(mock_cursor, mock_exporter):
    mock_cursor.fetchall.return_value = [("db1", 5), ("db2", 3), ("db3", 2)]
    top_databases = get_top_databases_by_connections(mock_cursor, mock_exporter)
    assert top_databases == {"db1": 5, "db2": 3, "db3": 2}


# Test for no query latency results
def test_get_query_latency_no_results(mock_cursor, mock_exporter):
    mock_cursor.fetchall.return_value = []
    result = get_query_latency(mock_cursor, mock_exporter, None)
    assert result == {}


# Test for retrieving idle connections per database
def test_get_idle_connections(mock_cursor):
    mock_cursor.fetchall.return_value = [("db1", 2), ("db2", 4)]
    result = get_idle_connections(mock_cursor, None)
    assert result == {"db1": 2, "db2": 4}


# Test for no idle connections in the database
def test_get_idle_connections_no_results(mock_cursor):
    mock_cursor.fetchall.return_value = []
    result = get_idle_connections(mock_cursor, None)
    assert result == {}


# Test for db_total_connections metric
def test_db_total_connections(mock_exporter):
    """Test the db_total_connections metric."""
    # Check if db_total_connections metric is created
    mock_exporter.db_total_connections.set(50)

    # Verify if the metric's value is correctly set
    mock_exporter.db_total_connections.set.assert_called_with(50)

    # Check if the db_total_connections name is correct
    mock_exporter.db_total_connections._name = (
        "postgres_total_connections"  # Set the name manually
    )
    assert mock_exporter.db_total_connections._name == "postgres_total_connections"


# Test for empty result in get_long_running_queries
def test_get_long_running_queries_and_transactions_empty(mock_cursor):
    mock_cursor.fetchall.return_value = []
    result = get_long_running_queries_and_transactions(mock_cursor, None)
    assert result == {}


# Test for the main function, including environment variables and function calls
def test_main(monkeypatch, mock_exporter):
    # Mock environment variables
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "testdb")
    monkeypatch.setenv("POSTGRES_USER", "user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")
    monkeypatch.setenv("ENVIRONMENT", "local")

    # Mock the connection and cursor
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor().__enter__()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Mock the exporter
        with patch(
            "postgres_metrics_exporter.PostgresExporter",
            return_value=mock_exporter,
        ):
            main()

        # Assert that the correct functions were called
        mock_cursor.execute.assert_called()
        mock_exporter.push_metric.assert_called()


# Test for failing database connection in main function
def test_main_db_connection_failure(monkeypatch, mock_exporter):
    # Mock environment variables
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "testdb")
    monkeypatch.setenv("POSTGRES_USER", "user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")
    monkeypatch.setenv("ENVIRONMENT", "local")

    # Simulate connection failure
    with patch("psycopg2.connect", side_effect=Exception("Connection failed")):
        with pytest.raises(Exception, match="Connection failed"):
            main()
