# import pandas as pd
# # Configura pandas para mostrar todas las columnas
# df_api = pd.read_pickle('df_api.pkl')
# df_cluster = pd.read_pickle('df_cluster_ST.pkl')
# print(df_cluster.head(50))

# # Asumiendo que tu DataFrame original es `df` y el DataFrame con los clusters es `df_clusters`
# # Realizamos un merge entre ambos DataFrames usando la columna `item`
# df_api = df_api.merge(df_cluster[['item', 'cluster_base_on_dtw']], on='item', how='left')

# # Ahora, la columna 'cluster' se actualiza con los valores de 'cluster_base_on_dtw'
# df_api['cluster'] = df_api['cluster_base_on_dtw']

# # Elimina la columna temporal 'cluster_base_on_dtw' si no la necesitas
# df_api.drop(columns=['cluster_base_on_dtw'], inplace=True)
# print(df_api.head(50))
# df_api.to_pickle('df_api.pkl')

# import pandas as pd
# from datetime import timedelta

# # Cargar df_total desde el archivo pickle
# df_total = pd.read_pickle('df_total.pkl')

# # Asegurarse de que la columna 'date' esté en formato datetime
# df_total['date'] = pd.to_datetime(df_total['date'])

# # Obtener la fecha más reciente de df_total
# end_date = df_total['date'].max()

# # Filtrar los últimos 65 días de df_total
# start_date = end_date - pd.Timedelta(days=65)
# df_api = df_total[df_total['date'] >= start_date]

# # Guardar df_api como un nuevo archivo pickle
# df_api.to_pickle('df_api.pkl')

# # Calcular fechas de inicio y fin
# end_date = df_api['date'].max()  # Última fecha en df_api
# if end_date is None:
#     raise ValueError("❌ No se encontró ninguna fecha en el DataFrame.")

# start_date = end_date - timedelta(days=30)

# # Filtrar las ventas entre start_date y end_date
# df_filtered = df_api[(df_api['date'] >= start_date) & (df_api['date'] <= end_date)]

# # Calcular agregados
# ventas_id = df_filtered.groupby("id")["daily_sales"].sum().rename("ventas_id")
# ventas_item = df_filtered.groupby("item")["daily_sales"].sum().rename("ventas_item")
# ventas_cluster = df_filtered.groupby("cluster")["daily_sales"].sum().rename("ventas_cluster")

# # Crear un DataFrame con las combinaciones de id, item y cluster
# df_weights = df_filtered[["id", "item", "cluster"]].drop_duplicates()

# # Merge con las sumas de ventas
# df_weights = df_weights.merge(ventas_id, on="id", how="left")
# df_weights = df_weights.merge(ventas_item, on="item", how="left")
# df_weights = df_weights.merge(ventas_cluster, on="cluster", how="left")

# # Calcular el peso_30
# df_weights["peso_30"] = (df_weights["ventas_id"] / df_weights["ventas_item"]) * \
#                         (df_weights["ventas_item"] / df_weights["ventas_cluster"])

# df_weights['peso_30'] = df_weights['peso_30'].fillna(0)

# # Añadir la columna 'peso_30' al DataFrame original df_api
# df_api = df_api.merge(df_weights[["id", "peso_30"]], on="id", how="left")

# # Guardar df_api como un nuevo archivo pickle
# df_api.to_pickle('df_api.pkl')

# df_api = pd.read_pickle('df_api.pkl')
# print(df_api[['id', 'cluster','peso_30']].head(50))