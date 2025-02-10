#!/bin/bash

# Load environment variables from the server
if [ -f /db/.env ]; then
  source /db/.env
else
  echo "⚠️ .env file not found at /db/.env"
  exit 1
fi

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -p 5432 -U $DB_USER; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Check if the table exists
TABLE_EXISTS=$(psql -h localhost -U $DB_USER -d $DB_NAME -tAc "SELECT to_regclass('public.observaciones')")

if [ "$TABLE_EXISTS" != "observaciones" ]; then
  echo "⚡ Applying schema.sql as 'observaciones' table does not exist."
  psql -h localhost -U $DB_USER -d $DB_NAME -f /docker-entrypoint-initdb.d/schema.sql
  echo "✅ Database schema has been initialized successfully."
else
  echo "✅ Schema already exists. Skipping initialization."
fi
