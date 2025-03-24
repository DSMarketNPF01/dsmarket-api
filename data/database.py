# data/database.py
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

def get_env_db_params():
    return {
        "user": os.getenv("ALLOYDB_USER"),
        "password": os.getenv("ALLOYDB_PASSWORD"),
        "host": os.getenv("ALLOYDB_HOST"),
        "port": os.getenv("ALLOYDB_PORT"),
        "db": os.getenv("ALLOYDB_DB"),
    }

# Configura aquí tu conexión a AlloyDB
def get_alloydb_engine(user, password, host, port, db):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)

# Guardar un DataFrame en una tabla de AlloyDB (reemplaza si existe)
def save_dataframe_to_alloydb(df, table_name, engine):
    df.to_sql(table_name, engine, if_exists='replace', index=False)

# Consultar la última fecha conocida para una combinación item-store
def get_last_available_date(item, store, engine):
    query = text("""
        SELECT MAX(date) FROM historical_sales
        WHERE item = :item AND store = :store
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"item": item, "store": store}).fetchone()
    return result[0] if result and result[0] else None

# Consultar el peso_30 para un id y fecha específicos
# Mejorar la función por si no existe el registro, calcular el peso_30
# Si no existen registros para el cálculo, devolver la media por defecto
def get_weight_for_id_and_date(id_item_store: str, date_exacta, engine):
    """
    Devuelve el peso_30 para un id y una fecha exactos.
    Si no existe, devuelve 1.0 por defecto.
    """
    query = text("""
        SELECT peso_30 FROM historical_sales
        WHERE id = :id
        AND date = :date
        AND peso_30 IS NOT NULL
        LIMIT 1
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"id": id_item_store, "date": date_exacta}).fetchone()
        return float(result[0]) if result and result[0] is not None else 1.0

# Leer una tabla completa desde AlloyDB
def load_table(table_name, engine):
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)

# Leer eventos por región y año
def load_events_by_region(region, engine):
    query = f'''
        SELECT date, holiday, region FROM events
        WHERE region = %s;
    '''
    return pd.read_sql_query(query, engine, params=(region,))
