import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="/db/.env")
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Function to delete the database
def delete_database():
    try:
        # Connect to the default 'postgres' database to execute DROP DATABASE
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname='postgres',  # Connect to the default database
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Terminate all active connections to the database
        cursor.execute(sql.SQL("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
              AND pid <> pg_backend_pid();
        """), [DB_NAME])

        # Drop the database
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {};").format(
            sql.Identifier(DB_NAME)
        ))

        print(f"✅ Database '{DB_NAME}' has been deleted successfully.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error while deleting the database: {e}")

if __name__ == "__main__":
    delete_database()