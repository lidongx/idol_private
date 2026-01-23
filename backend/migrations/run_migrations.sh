#!/bin/bash
# Run database migrations script
# Usage: ./run_migrations.sh

set -e

echo "Running database migrations..."

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Database connection details
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-idol_db}"
DB_USER="${DB_USER:-idol_user}"
DB_PASSWORD="${DB_PASSWORD:-idol_password}"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "Error: psql command not found. Please install PostgreSQL client."
    exit 1
fi

# Run migrations in order
echo "Running migration: 002_create_idols_table.sql"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f 002_create_idols_table.sql

echo "✅ All migrations completed successfully!"
