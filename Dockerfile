# Copyright 2024-2025 Hewlett Packard Enterprise Development LP
FROM prometheuscommunity/elasticsearch-exporter:v1.7.0 as ops-prometheus-exporter

FROM python:3.12-alpine as ops-prometheus-postgres-exporter
WORKDIR /app

RUN apk add --no-cache \
    build-base \
    libpq-dev \
    && rm -rf /var/cache/apk/*
RUN apk upgrade xz-libs
RUN apk upgrade sqlite-libs

# Copy the application source code and dependency files
COPY src /app
COPY pyproject.toml /app/
COPY poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Configure Poetry to not create a virtual environment and install dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# Make Python scripts executable
RUN chmod a+rx *.py

# Set the user for running the application (optional)
RUN addgroup -S devops-cdsops-grp && adduser -S devops-cdsops -G devops-cdsops-grp
USER devops-cdsops

# Command to run the application
CMD ["/bin/sh", "-c", "python", "postgres_metrics_exporter.py"]
