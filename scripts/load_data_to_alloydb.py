# scripts/load_data_to_alloydb.py
import pandas as pd
import pickle
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
from glob import glob
from events.events_generator import create_events_df
from data.database import get_alloydb_engine, get_env_db_params, save_dataframe_to_alloydb
from dotenv import load_dotenv

# 1. Cargar credenciales desde .env
load_dotenv()
params = get_env_db_params()
engine = get_alloydb_engine(**params)

# 2. Subir archivos divididos por año a historical_sales
chunk_dir = "data/chunks"
chunk_files = sorted(glob(os.path.join(chunk_dir, "df_total_*.csv")))

for file in chunk_files:
    print(f"Leyendo {file}...")
    df_chunk = pd.read_csv(file, parse_dates=["date"])
    # print(f"Subiendo {file} a historical_sales...")
    # df_chunk.to_sql("historical_sales", engine, if_exists='append', index=False)

# 3. Generar eventos y festivos (nuevo enfoque)
print("Generando eventos y festivos...")
first_chunk = pd.read_csv(chunk_files[0], nrows=10)
last_year = df_chunk['year'].max() if 'year' in df_chunk.columns else df_chunk['date'].dt.year.max()
regions = df_chunk['region'].dropna().unique().tolist()
events_df, holidays_df = create_events_df(year_input=last_year, regions_input=regions)

print("Subiendo events...")
save_dataframe_to_alloydb(events_df, "events", engine)

print("Subiendo holidays...")
save_dataframe_to_alloydb(holidays_df, "holidays", engine)

# 4. Subir df_clusters.pkl → clusters
print("Cargando df_clusters.pkl...")
df_clusters = pd.read_pickle("../df_cluster_ST.pkl")
print("Subiendo clusters...")
save_dataframe_to_alloydb(df_clusters, "clusters", engine)

# 5. Subir region_map → region_map
print("Subiendo region_map...")
region_map = {
    "NYC": "New York", "BOS": "Boston", "PHI": "Philadelphia",
    "CHI": "Chicago", "WAS": "Washington", "SFO": "San Francisco",
    "LAX": "Los Angeles", "SEA": "Seattle", "MIA": "Miami", "DAL": "Dallas"
}
df_region_map = pd.DataFrame(region_map.items(), columns=["code", "city"])
save_dataframe_to_alloydb(df_region_map, "region_map", engine)

print("Carga de datos a AlloyDB completada ✅")
