# scripts/convert_csv_to_pkl.py
import pandas as pd
import os

INPUT_FILE = "df_total.csv"
OUTPUT_FILE = "df_total.pkl"

# Verifica que el archivo .csv existe
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Archivo no encontrado: {INPUT_FILE}")

# Carga el archivo CSV
print(f"Cargando {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE, parse_dates=['date'])  # Asegura que 'date' sea datetime

# Exporta a formato pickle
print(f"Guardando como {OUTPUT_FILE}...")
df.to_pickle(OUTPUT_FILE)

print("Conversión completada ✅")
