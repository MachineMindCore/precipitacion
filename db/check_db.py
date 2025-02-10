import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="db/.env")
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Function to check schema
def check_schema():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Query to get all tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cursor.fetchall()
        
        print("Tables in the database:")
        for table in tables:
            print(f"- {table[0]}")

            # Get columns for each table
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table[0]}';")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[0]} ({column[1]})")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()