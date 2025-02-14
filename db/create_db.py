import os
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from model import Base

# Load environment variables from .env file
load_dotenv()

# Database connection details from .env
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', 5432)

def create_database():
    try:
        # Connect to PostgreSQL server (default 'postgres' database)
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create database
        cur.execute(f'CREATE DATABASE {DB_NAME}')
        print(f"Database '{DB_NAME}' created successfully")

    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

def execute_schema():
    try:
        # Connect to the new database
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cur = conn.cursor()

        # Read and execute schema.sql
        with open('schema.sql', 'r') as file:
            cur.execute(file.read())
        conn.commit()
        print("Schema executed successfully")

    except Exception as e:
        print(f"Error executing schema: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

def create_sqlalchemy_model():
    # Create SQLAlchemy engine
    engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

    # Create tables in the database
    Base.metadata.create_all(engine)
    print("SQLAlchemy model created and tables initialized in the database")

if __name__ == "__main__":
    create_database()
    create_sqlalchemy_model()