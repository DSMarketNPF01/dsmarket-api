import pandas as pd
from datetime import timedelta
from sqlalchemy import text
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
from data.database import (
    get_env_db_params,
    get_alloydb_engine,
)

# Conexión
params = get_env_db_params()
engine = get_alloydb_engine(**params)

# Obtener última fecha global de la tabla
with engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(date) FROM historical_sales")).fetchone()
    end_date = result[0]

if end_date is None:
    raise ValueError("❌ No se encontró ninguna fecha en la tabla historical_sales.")

start_date = end_date - timedelta(days=30)

# Cargar ventas
print(f"📦 Cargando ventas desde {start_date} hasta {end_date}...")
query = text("""
    SELECT id, item, date, daily_sales, cluster
    FROM historical_sales
    WHERE date BETWEEN :start AND :end
""")
df = pd.read_sql_query(query, engine, params={"start": start_date, "end": end_date})

# Calcular agregados
ventas_id = df.groupby("id")["daily_sales"].sum().rename("ventas_id")
ventas_item = df.groupby("item")["daily_sales"].sum().rename("ventas_item")
ventas_cluster = df.groupby("cluster")["daily_sales"].sum().rename("ventas_cluster")

# Calcular pesos
df_weights = df[["id", "item", "cluster"]].drop_duplicates()
df_weights = df_weights.merge(ventas_id, on="id")
df_weights = df_weights.merge(ventas_item, on="item")
df_weights = df_weights.merge(ventas_cluster, on="cluster")
df_weights["peso_30"] = (df_weights["ventas_id"] / df_weights["ventas_item"]) * \
                        (df_weights["ventas_item"] / df_weights["ventas_cluster"])

# Actualizar AlloyDB
print("🛠 Actualizando columna peso_30 en historical_sales...")

with engine.connect() as conn:
    for _, row in df_weights.iterrows():
        update_query = text("""
            UPDATE historical_sales
            SET peso_30 = :peso
            WHERE id = :id AND date BETWEEN :start AND :end
        """)
        conn.execute(update_query, {
            "peso": float(row["peso_30"]),
            "id": row["id"],
            "start": start_date,
            "end": end_date
        })
    conn.commit()

print("✅ Actualización completada.")
