#!/bin/bash
# Create additional databases for Round 2 and Round 3
# This script runs automatically on first PostgreSQL init.

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE mlfest_r2;
    CREATE DATABASE mlfest_r3;
EOSQL
