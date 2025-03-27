# app/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timedelta
import pickle

# Funciones de generación de features y forecasting horizon
from features.feature_builder import generate_dataframe
from features.forecasting_utils import generate_fh_from_date
from events.events_loader import load_events_and_holidays
# from data.database import get_env_db_params, get_alloydb_engine, get_last_available_date

# Carga del modelo
print("🧠 Cargando modelos de predicción...")
models = pd.read_pickle('models_cluster.pkl')

# Carga de datos base (histórico, regiones, precios...)
print(f"📂 Cargando base de datos...")
df_bbdd = pd.read_csv('df_api.csv')
print(df_bbdd.columns)

df_stores = df_bbdd[['store', 'store_code']].drop_duplicates().set_index('store')
prices_bbdd = (
    df_bbdd[['id', 'date', 'sell_price']]
    .assign(date=lambda df: pd.to_datetime(df['date']))
    .sort_values(by='date', ascending=False)
    .set_index('id')
)

# Regiones principales
region_map = {
    "ATL": "Atlanta",
    "AUS": "Austin",
    "BAL": "Baltimore",
    "BOS": "Boston",
    "BUF": "Buffalo",
    "CHA": "Charlotte",
    "CHI": "Chicago",
    "CIN": "Cincinnati",
    "CLE": "Cleveland",
    "COL": "Columbus",
    "DAL": "Dallas",
    "DEN": "Denver",
    "DET": "Detroit",
    "FTL": "Fort Lauderdale",
    "HOU": "Houston",
    "IND": "Indianápolis",
    "JAC": "Jacksonville",
    "KCY": "Kansas City",
    "LAS": "Las Vegas",
    "LAX": "Los Ángeles",
    "LGA": "New York",
    "LVS": "Las Vegas",
    "MIA": "Miami",
    "MIL": "Milwaukee",
    "MSP": "Minneapolis-Saint Paul",
    "MSY": "New Orleans",
    "NAN": "Nashville",
    "NYC": "New York",
    "OAK": "Oakland",
    "ORL": "Orlando",
    "PHI": "Philadelphia",
    "PHX": "Phoenix",
    "PIT": "Pittsburgh",
    "POR": "Portland",
    "RAL": "Raleigh-Durham",
    "RSW": "Fort Myers",
    "SAC": "Sacramento",
    "SAT": "San Antonio",
    "SDG": "San Diego",
    "SEA": "Seattle",
    "SFO": "San Francisco",
    "SJC": "San José",
    "SLC": "Salt Lake City",
    "SNA": "Santa Ana",
    "STL": "San Luis",
    "TPA": "Tampa",
    "WAS": "Washington D.C."
}

# Convertir a DataFrame
df_region = pd.DataFrame(region_map.items(), columns=["code", "city"]).set_index("code")

# NUEVAS FUNCIONES DE CONSULTA PUNTUAL
def get_store_code(store: str, df_bbdd: pd.DataFrame) -> str:
    # Filtramos el DataFrame para obtener el store_code correspondiente
    result = df_bbdd[df_bbdd['store'] == store]['store_code']
    
    # Si encontramos al menos un resultado, devolvemos el primero; de lo contrario, devolvemos "UNKNOWN"
    return result.iloc[0] if not result.empty else "UNKNOWN"

def get_cluster_for_item(item: str, df_bbdd: pd.DataFrame) -> str:
    # Filtramos el DataFrame para obtener el cluster correspondiente al item
    result = df_bbdd[df_bbdd['item'] == item]['cluster']
    
    # Si encontramos al menos un resultado, devolvemos el primer cluster; de lo contrario, devolvemos 0
    cluster = result.iloc[0] if not result.empty else 0
    
    # Formateamos el cluster como "CLUSTER_X.X"
    return f"CLUSTER_{float(cluster):.1f}"

def get_latest_price(item_store_id: str, date: str, df_bbdd: pd.DataFrame) -> float:
    # Filtramos el DataFrame para obtener las filas correspondientes al item_store_id
    result = df_bbdd[(df_bbdd['id'] == item_store_id) & (df_bbdd['date'] <= date)]
    
    # Si hay resultados, ordenamos por fecha descendente y tomamos el primer resultado
    if not result.empty:
        result_sorted = result.sort_values(by='date', ascending=False)
        return float(result_sorted.iloc[0]['sell_price'])
    
    # Si no hay resultados, retornamos None
    return None

def get_weight_for_id_and_date(id_item_store: str, date_exacta: str, df_api: pd.DataFrame) -> float:
    """
    Devuelve el peso_30 para un id y una fecha exactos desde el DataFrame df_api.
    Si no existe, devuelve 1.0 por defecto.
    """
    # Filtrar el DataFrame por id y fecha exacta
    result = df_api[(df_api['id'] == id_item_store) & (df_api['date'] == date_exacta)]
    
    # Comprobar si encontramos algún resultado
    if not result.empty:
        # Devolver el valor de 'peso_30' si no es nulo
        return float(result.iloc[0]['peso_30']) if pd.notna(result.iloc[0]['peso_30']) else 1.0
    
    # Si no se encuentra, devolver 1.0 por defecto
    return 1.0


# Crear la app FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada del usuario (petición)
class PredictionRequest(BaseModel):
    item: str
    store: str

@app.post("/predict")
def predict(request: PredictionRequest):
    item = request.item
    store = request.store

    # 1. Obtener la última fecha disponible para ese item-store
    df_item_store = df_bbdd[(df_bbdd['item'] == item) & (df_bbdd['store'] == store)]
    if df_item_store.empty:
        return {"error": "No hay datos para esa combinación de item y tienda."}
    last_date = df_item_store['date'].max()

    # Predicción para el día siguiente
    prediction_date = pd.to_datetime(last_date) + timedelta(days=1)
    print(f"📅 Última fecha encontrada: {last_date} → Predicción para: {prediction_date.date()}")

    # Cargar eventos y festivos
    regions_bbdd = df_bbdd['region'].unique()
    events_bbdd, holidays_bbdd = load_events_and_holidays(year=prediction_date.year, regions=regions_bbdd)

    # Obtener store_code y región
    store_code = get_store_code(store, df_bbdd)
    region_code = store_code.split('_')[0]
    region = df_region['city'].get(region_code, "Unknown")

    # Obtener cluster y modelo
    cluster_value = get_cluster_for_item(item, df_bbdd)
    model_cluster = models.get(cluster_value)
    if not model_cluster:
        return {"error": f"No se encontró modelo para {cluster_value}"}
    print(f"🔍 Cluster detectado: {cluster_value}")

    # Obtener precio
    id_item_store = f"{item}_{store_code}"
    sell_price = get_latest_price(id_item_store, str(last_date), df_bbdd)

    model_cluster = models[cluster_value]
    
    # Generar features
    df_input = generate_dataframe(
        store_code=store_code,
        region=region,
        item=item,
        date_API=prediction_date,
        sell_price=sell_price,
        events_df=events_bbdd,
        holidays_df=holidays_bbdd
    )
    print("📊 Features generadas correctamente.")

    # 3. Crear Forecasting Horizon
    fh = generate_fh_from_date(last_date, horizon=28)
    predictions = model_cluster.predict(fh=fh, X=df_input)
    y_pred = predictions.values

    dates = pd.date_range(start=prediction_date, periods=len(y_pred), freq='D')

    # Se calcula el peso de ese artículo en los últimos 30 días
    id_weight = get_weight_for_id_and_date(id_item_store, last_date, df_bbdd)

    y_pred_weighted = [round(float(y) * id_weight, 2) for y in y_pred]
    print("✅ Predicción realizada:")

    print(f"✅ Predicciones generadas para {len(y_pred_weighted)} días.")

    # 4. Hacer predicción
    prediction = model_cluster.predict(fh=fh, X=df_input)
    y_pred = float(prediction.values[0])

    results = [
        {"date": d.strftime("%Y-%m-%d"), "predicted_sales": y}
        for d, y in zip(dates, y_pred_weighted)
    ]
    return {
    "item": item,
    "store": store,
    "predictions": results
    }

@app.get("/data/structure")
def get_structure():
    # Filtrar los datos necesarios de 'df_bbdd'
    structure = {}
    
    # Iterar sobre los registros únicos de 'store', 'department' y 'item'
    for _, row in df_bbdd[['store', 'department', 'item']].drop_duplicates().iterrows():
        store = row['store']
        dept = row['department']
        item = row['item']
        
        if store not in structure:
            structure[store] = {}
        if dept not in structure[store]:
            structure[store][dept] = []
        if item not in structure[store][dept]:
            structure[store][dept].append(item)

    return structure

@app.get("/")
def root():
    return {"message": "API de predicción de ventas funcionando ✅"}
