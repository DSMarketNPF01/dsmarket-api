# scripts/split_df_by_year.py
import pandas as pd
import os

INPUT_FILE = "df_total.csv"
OUTPUT_DIR = "data/chunks"
CHUNK_SIZE = 500_000

# Crear carpeta de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Diccionario para ir acumulando por año
yearly_data = {}

print(f"Leyendo {INPUT_FILE} por chunks...")

for chunk in pd.read_csv(INPUT_FILE, parse_dates=['date'], chunksize=CHUNK_SIZE):
    if 'year' not in chunk.columns:
        chunk['year'] = chunk['date'].dt.year

    for year, group in chunk.groupby('year'):
        if year not in yearly_data:
            yearly_data[year] = []
        yearly_data[year].append(group)

# Concatenar y guardar por año
for year, data_parts in yearly_data.items():
    df_year = pd.concat(data_parts, ignore_index=True)
    output_file = os.path.join(OUTPUT_DIR, f"df_total_{year}.csv")
    df_year.to_csv(output_file, index=False)
    print(f"Guardado: {output_file} ({len(df_year)} filas)")

print("División completada ✅")
