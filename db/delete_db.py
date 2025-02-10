import os
import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError

# Load environment variables from .env file
load_dotenv()

def drop_database():
    try:
        # Connect to PostgreSQL server (using default 'postgres' database)
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            dbname='postgres',  # Connect to maintenance database
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', 5432)  # Default PostgreSQL port
        )
        conn.autocommit = True  # Required for database operations
        cur = conn.cursor()

        # Get database name to drop from environment variables
        db_name = os.getenv('DB_NAME')
        if not db_name:
            raise ValueError("DB_NAME not set in .env file")

        # Drop database
        cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
        print(f"Database '{db_name}' dropped successfully")

    except OperationalError as e:
        print(f"Operational Error: {e}")
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        # Clean up connections
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    drop_database()