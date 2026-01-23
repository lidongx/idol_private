#!/bin/bash
# Database initialization script for idol_private

set -e

echo "Initializing idol_private database..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
sleep 3

# Run the SQL initialization script
PGPASSWORD=dev_password psql -h localhost -U idol_user -d idol_db -f "$(dirname "$0")/init_db.sql"

echo "Database initialization complete!"
echo ""
echo "Users table created successfully."
echo "You can now start the FastAPI backend."
