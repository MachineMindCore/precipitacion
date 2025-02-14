import polars as pl
import requests
from datetime import datetime, timedelta
import sys
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.model import Estacion, Observacion
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv(dotenv_path="db/.env")
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=30)
Session = sessionmaker(bind=engine)

def get_data(fecha):
    url = "https://www.datos.gov.co/resource/s54a-sgyg.json"
    params = {
        '$where': f"fechaobservacion >= '{fecha}T00:00:00' AND fechaobservacion < '{fecha}T23:59:59'",
        '$limit': 50000,  # Increased limit if API allows
        "$order": "FechaObservacion ASC",
        "$offset": 0,
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            print(f"Data retrieved for {fecha}")
            return response.json()
        print(f"Error: {response.status_code}")
        return []
    except requests.exceptions.Timeout:
        print("Timeout occurred. Retrying...")
        return get_data(fecha_inicio, fecha_fin)  # Simple retry for timeouts

def process_data(raw_data):
    df = pl.DataFrame(raw_data)
    df = df.with_columns(pl.col("valorobservado").cast(pl.Float64))
    df_grouped = df.group_by("codigoestacion").agg(pl.col("valorobservado").sum())
    df = df.drop("valorobservado").join(df_grouped, on="codigoestacion")
    return df
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert

def upload_data(df: pl.DataFrame):
    if df.shape[0] == 0:
        return

    session = Session()
    stations_data = []
    observations_data = []

    for row in df.to_dicts():
        codigoestacion = row['codigoestacion']
        date = datetime.strptime(row['fechaobservacion'], '%Y-%m-%dT%H:%M:%S.%f').date()

        # Prepare station & observation data
        stations_data.append({
            "codigoestacion": codigoestacion,
            "nombreestacion": row["nombreestacion"],
            "departamento": row["departamento"],
            "municipio": row["municipio"],
            "zonahidrografica": row["zonahidrografica"],
            "latitud": row["latitud"],
            "longitud": row["longitud"]
        })

        observations_data.append({
            "id": f"{codigoestacion}_{date}",
            "codigoestacion": codigoestacion,
            "fechaobservacion": date,
            "valorobservado": row['valorobservado']
        })

    try:
        # Bulk insert for stations (skip duplicates)
        stmt = insert(Estacion).values(stations_data).on_conflict_do_nothing()
        session.execute(stmt)

        # Bulk insert for observations (skip duplicates)
        stmt = insert(Observacion).values(observations_data).on_conflict_do_nothing()
        session.execute(stmt)

        session.commit()
        
    except IntegrityError:
        session.rollback()  # Ignore duplicate key errors
    except Exception as e:
        session.rollback()
        print(f"Unexpected error: {e}")
    finally:
        session.close()



def process_day(date):
    raw_data = get_data(date)
    df = process_data(raw_data)
    upload_data(df)
    print(f"Inserted {date}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fill_data.py <start_date DD/MM/YYYY> <end_date DD/MM/YYYY>")
        sys.exit(1)

    fecha_inicio = datetime.strptime(sys.argv[1], "%d/%m/%Y").date()
    fecha_fin = datetime.strptime(sys.argv[2], "%d/%m/%Y").date()
    fechas = [fecha_inicio + timedelta(days=i) for i in range((fecha_fin - fecha_inicio).days + 1)]

    # ✅ Dynamically choose thread count
    max_threads = min(10, os.cpu_count() or 4)  # Use at most 10 threads, default to 4 if unknown
    print(f"Using {max_threads} threads")

    # ✅ Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_day, fecha): fecha for fecha in fechas}

        for future in as_completed(futures):
            try:
                future.result()  # Raises exceptions if any
            except Exception as e:
                print(f"Error processing {futures[future]}: {e}")