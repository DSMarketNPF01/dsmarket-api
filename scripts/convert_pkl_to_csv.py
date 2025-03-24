# scripts/convert_pkl_to_csv.py
import pandas as pd
import os

INPUT_FILE = "df_total.pkl"
OUTPUT_FILE = "df_total.csv"

# Verifica que el archivo .pkl existe
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Archivo no encontrado: {INPUT_FILE}")

# Carga el archivo pickle
print(f"Cargando {INPUT_FILE}...")
df = pd.read_pickle(INPUT_FILE)

# Asegura que las fechas estén en formato correcto para CSV
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

# Exporta a CSV sin índice
print(f"Exportando a {OUTPUT_FILE}...")
df.to_csv(OUTPUT_FILE, index=False)

print("Conversión completada ✅")
