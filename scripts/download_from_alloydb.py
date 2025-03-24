# scripts/download_from_alloydb.py
import pandas as pd
import os
from dotenv import load_dotenv
from data.database import get_env_db_params, get_alloydb_engine, load_table

# Cargar credenciales desde .env
load_dotenv()
params = get_env_db_params()
engine = get_alloydb_engine(**params)

# Carpeta de salida
os.makedirs("data/downloads", exist_ok=True)

# Tablas a descargar
tables = ["historical_sales", "events", "holidays", "clusters", "region_map"]

for table in tables:
    print(f"Descargando tabla: {table}...")
    df = load_table(table, engine)
    output_path = f"data/downloads/{table}.csv"
    df.to_csv(output_path, index=False)
    print(f"Guardado en: {output_path} ✅")

print("Descarga completa de AlloyDB ✅")
