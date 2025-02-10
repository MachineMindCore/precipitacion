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

# Function to create the database
def create_database():
    try:
        # Connect to the default 'postgres' database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname='postgres',  # Connect to the default database
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create the database
        cursor.execute(sql.SQL("CREATE DATABASE {};").format(
            sql.Identifier(DB_NAME)
        ))

        print(f"✅ Database '{DB_NAME}' has been created successfully.")

        cursor.close()
        conn.close()

    except psycopg2.errors.DuplicateDatabase:
        print(f"⚠️ Database '{DB_NAME}' already exists.")
    except Exception as e:
        print(f"❌ Error while creating the database: {e}")

if __name__ == "__main__":
    create_database()
