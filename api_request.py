import pandas as pd
import requests
from datetime import datetime, timedelta
import sys
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="db/.env")
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Database connection
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

# Function to get data from the API
def obtener_datos(fecha_inicio, fecha_fin):
    url = "https://www.datos.gov.co/resource/s54a-sgyg.json"
    params = {
        '$where': f"fechaobservacion >= '{fecha_inicio}' AND fechaobservacion <= '{fecha_fin}'",
        '$limit': 1000
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print(f"Obteniendo datos del {fecha_inicio} al {fecha_fin}")
        return response.json()
    else:
        print(f"Error al obtener datos: {response.status_code}")
        return []

# Function to insert data into the database
def insertar_datos(df):
    if df.empty:
        return

    records = df[['codigoestacion', 'codigosensor', 'fechaobservacion', 'valorobservado']].values.tolist()
    query = """
        INSERT INTO observaciones (codigoestacion, codigosensor, fechaobservacion, valorobservado)
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cursor, query, records)
    conn.commit()

# Main function
if __name__ == "__main__":
    fecha_inicio = datetime.strptime(sys.argv[1], "%d/%m/%Y")
    fecha_fin = datetime.strptime(sys.argv[2], "%d/%m/%Y")

    fecha_actual = fecha_inicio

    while fecha_actual < fecha_fin:
        for hora in range(24):
            inicio = fecha_actual.replace(hour=hora, minute=0, second=0, microsecond=0).isoformat()
            fin = fecha_actual.replace(hour=hora, minute=59, second=59, microsecond=999999).isoformat()

            datos = obtener_datos(inicio, fin)
            if datos:
                df = pd.DataFrame(datos)
                insertar_datos(df)
                print(f"Datos insertados para {inicio} - {fin}")
        fecha_actual += timedelta(days=1)

    cursor.close()
    conn.close()
