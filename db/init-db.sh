#!/bin/bash

# Load environment variables
source /docker-entrypoint-initdb.d/.env

# Wait for PostgreSQL to be ready
until pg_isready -h postgres -p 5432 -U $DB_USER; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run the schema SQL script
psql -h postgres -U $DB_USER -d $DB_NAME -f /docker-entrypoint-initdb.d/schema.sql
