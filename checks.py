# import os
# import sys
# import pandas as pd
# import numpy as np

# # # Directorio de trabajo actual
# # print("Directorio de trabajo actual:", os.getcwd())

# # # Ruta del script (si estás en un .py)
# # try:
# #     print("Directorio del script:", os.path.dirname(os.path.abspath(__file__)))
# # except NameError:
# #     print("No estás en un script (probablemente en un entorno interactivo)")

# # # Intérprete de Python
# # print("Ruta del intérprete de Python:", sys.executable)

# # from data.database import get_env_db_params, get_alloydb_engine, get_last_available_date

# # params = get_env_db_params()
# # engine = get_alloydb_engine(**params)

# # print(get_last_available_date("ACCESORIES_1_001", "Greenwich_Village", engine))

# df = pd.read_pickle("df_cluster_ST.pkl")
# print(df.head())
import pandas as pd
from datetime import timedelta
from sqlalchemy import text
from data.database import get_env_db_params, get_alloydb_engine

# Conexión
params = get_env_db_params()
engine = get_alloydb_engine(**params)

# Obtener última fecha global en la tabla
with engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(date) FROM historical_sales")).fetchone()
    end_date = result[0]

if end_date is None:
    raise ValueError("❌ No se encontró ninguna fecha en la tabla historical_sales.")

start_date = end_date - timedelta(days=30)

# Cargar datos con peso_30
print(f"📦 Verificando datos entre {start_date} y {end_date}...")
query = text("""
    SELECT id, item, cluster, date, daily_sales, peso_30
    FROM historical_sales
    WHERE date BETWEEN :start AND :end
""")
df = pd.read_sql_query(query, engine, params={"start": start_date, "end": end_date})

# Recalcular pesos
ventas_id = df.groupby("id")["daily_sales"].sum().rename("ventas_id")
ventas_item = df.groupby("item")["daily_sales"].sum().rename("ventas_item")
ventas_cluster = df.groupby("cluster")["daily_sales"].sum().rename("ventas_cluster")

df_check = df[["id", "item", "cluster"]].drop_duplicates()
df_check = df_check.merge(ventas_id, on="id")
df_check = df_check.merge(ventas_item, on="item")
df_check = df_check.merge(ventas_cluster, on="cluster")

df_check["peso_30_calc"] = (df_check["ventas_id"] / df_check["ventas_item"]) * \
                           (df_check["ventas_item"] / df_check["ventas_cluster"])

# Comparar con lo almacenado
df_check = df_check.merge(
    df.groupby("id")["peso_30"].first().reset_index(),
    on="id",
    how="left"
)
df_check["abs_error"] = (df_check["peso_30_calc"] - df_check["peso_30"]).abs()

# Resultados
print("\n✅ Verificación completada")
print(f"👉 Total IDs verificados: {len(df_check)}")
print(f"⚠️ IDs con diferencia: {(df_check['abs_error'] > 1e-6).sum()}")
print(f"📈 Máximo error absoluto: {df_check['abs_error'].max():.6f}")

# Mostrar discrepancias
muestra = df_check[df_check["abs_error"] > 1e-6].head()
if not muestra.empty:
    print("\n🔍 Ejemplo de discrepancias:")
    print(muestra[["id", "peso_30", "peso_30_calc", "abs_error"]])
else:
    print("✅ Todos los pesos coinciden perfectamente.")
