# Use the official PostgreSQL image as the base
FROM postgres:15

# Copy initialization scripts and schema
COPY init-db.sh /docker-entrypoint-initdb.d/init-db.sh
COPY schema.sql /docker-entrypoint-initdb.d/schema.sql

# Make sure the init script is executable
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

# Expose PostgreSQL port
EXPOSE 5432
