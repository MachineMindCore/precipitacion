import pandas as pd
import requests
from datetime import datetime, timedelta
import sys
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.model import Estacion, Sensor, Observacion  # Import SQLAlchemy models
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv(dotenv_path="db/.env")
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Database connection using SQLAlchemy
DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)  # Connection pooling
Session = sessionmaker(bind=engine)

# Fetch existing stations and sensors at the start
def fetch_existing_records():
    session = Session()
    existing_estaciones = {estacion.codigoestacion for estacion in session.query(Estacion.codigoestacion).all()}
    existing_sensores = {sensor.codigosensor for sensor in session.query(Sensor.codigosensor).all()}
    session.close()
    return existing_estaciones, existing_sensores

# Function to get data from the API
def obtener_datos(fecha_inicio, fecha_fin):
    url = "https://www.datos.gov.co/resource/s54a-sgyg.json"
    params = {
        '$where': f"fechaobservacion >= '{fecha_inicio}' AND fechaobservacion <= '{fecha_fin}'",
        '$limit': 5000  # Increase limit to fetch more data per request
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print(f"Obteniendo datos del {fecha_inicio} al {fecha_fin}")
        return response.json()
    else:
        print(f"Error al obtener datos: {response.status_code}")
        return []

# Function to insert data into the database using SQLAlchemy (bulk insert)
def insertar_datos(datos, existing_estaciones, existing_sensores):
    if not datos:
        return

    session = Session()

    # Prepare data for bulk insert
    new_estaciones = []
    new_sensores = []
    observaciones = []

    for record in datos:
        # Station
        if record['codigoestacion'] not in existing_estaciones:
            new_estaciones.append(Estacion(
                codigoestacion=record['codigoestacion'],
                nombreestacion=record.get('nombreestacion', 'Unknown'),
                departamento=record.get('departamento', 'Unknown'),
                municipio=record.get('municipio', 'Unknown'),
                zonahidrografica=record.get('zonahidrografica', 'Unknown'),
                latitud=float(record.get('latitud', 0.0)),
                longitud=float(record.get('longitud', 0.0))
            ))
            existing_estaciones.add(record['codigoestacion'])  # Mark as existing

        # Sensor
        if record['codigosensor'] not in existing_sensores:
            new_sensores.append(Sensor(
                codigosensor=record['codigosensor'],
                descripcionsensor=record.get('descripcionsensor', 'Unknown'),
                unidadmedida=record.get('unidadmedida', 'Unknown')
            ))
            existing_sensores.add(record['codigosensor'])  # Mark as existing

        # Observation
        observaciones.append(Observacion(
            codigoestacion=record['codigoestacion'],
            codigosensor=record['codigosensor'],
            fechaobservacion=datetime.strptime(record['fechaobservacion'], '%Y-%m-%dT%H:%M:%S.%f'),
            valorobservado=float(record['valorobservado'])
        ))

    # Bulk insert new stations, sensors, and observations
    try:
        if new_estaciones:
            session.bulk_save_objects(new_estaciones)
        if new_sensores:
            session.bulk_save_objects(new_sensores)
        session.bulk_save_objects(observaciones)
        session.commit()
        print(f"Datos insertados: {len(observaciones)} observaciones, {len(new_estaciones)} nuevas estaciones, {len(new_sensores)} nuevos sensores")
    except Exception as e:
        session.rollback()
        print(f"Error al insertar datos: {e}")
    finally:
        session.close()

# Function to process a date range in parallel
def procesar_rango(fecha_inicio, fecha_fin, existing_estaciones, existing_sensores):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        fecha_actual = fecha_inicio

        while fecha_actual <= fecha_fin:
            inicio = fecha_actual.isoformat()
            fin = (fecha_actual + timedelta(days=1)).isoformat()  # Process daily chunks

            futures.append(executor.submit(procesar_dia, inicio, fin, existing_estaciones, existing_sensores))
            fecha_actual += timedelta(days=1)

        for future in as_completed(futures):
            future.result()  # Wait for all threads to complete

# Function to process a single day
def procesar_dia(inicio, fin, existing_estaciones, existing_sensores):
    datos = obtener_datos(inicio, fin)
    if datos:
        insertar_datos(datos, existing_estaciones, existing_sensores)

# Main function
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python upload_data.py <fecha_inicio> <fecha_fin>")
        print("Formato de fechas: dd/mm/YYYY")
        sys.exit(1)

    fecha_inicio = datetime.strptime(sys.argv[1], "%d/%m/%Y")
    fecha_fin = datetime.strptime(sys.argv[2], "%d/%m/%Y")

    # Fetch existing records once at the start
    existing_estaciones, existing_sensores = fetch_existing_records()

    procesar_rango(fecha_inicio, fecha_fin, existing_estaciones, existing_sensores)