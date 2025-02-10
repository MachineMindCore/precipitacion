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

# Apply the schema.sql to the database
psql -h localhost -U $DB_USER -d $DB_NAME -f /docker-entrypoint-initdb.d/schema.sql

echo "✅ Database schema has been initialized successfully."
