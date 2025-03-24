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
from data.database import get_env_db_params, get_alloydb_engine, get_last_available_date

# Carga del modelo
models = pd.read_pickle('models_cluster.pkl')

print(models.keys())

# Carga de datos base (histórico, regiones, precios...)
df_bbdd = pd.read_pickle('df_api.pkl')
clusters_bbdd = pd.read_pickle('df_cluster_ST.pkl')
clusters_bbdd.set_index('item', inplace=True)

clusters_list = list(models.keys())
print("Clusters disponibles en models:", clusters_list)

cluster_value = clusters_bbdd.at['SUPERMARKET_3_803', 'cluster_base_on_dtw']
print(f"Cluster para {'item'}: {cluster_value}")

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

    regions_bbdd = df_bbdd['region'].unique()

    events_bbdd, holidays_bbdd = load_events_and_holidays(year=prediction_date.year, regions=regions_bbdd)

    cluster_value = f'CLUSTER_{float(clusters_bbdd.at[item, 'cluster_base_on_dtw']):.1f}'

    model_cluster = models[cluster_value]
    
    # 2. Generar features
    df_input = generate_dataframe(
        store_API=store,
        item_API=item,
        date_API=prediction_date,
        df_stores=df_stores,
        df_region=df_region,
        prices_bbdd=prices_bbdd,
        events_df=events_bbdd,
        holidays_df=holidays_bbdd
    )

    # 3. Crear Forecasting Horizon
    fh = generate_fh_from_date(last_date, horizon=1)

    # 4. Hacer predicción
    prediction = model_cluster.predict(fh=fh, X=df_input)
    y_pred = float(prediction.values[0])

    return {
        "item": item,
        "store": store,
        "date": prediction_date.strftime("%Y-%m-%d"),
        "predicted_sales": round(y_pred, 2)
    }

@app.get("/")
def root():
    return {"message": "API de predicción de ventas funcionando"}

# La función generate_dataframe y generate_fh_from_date se pueden mover a /features/feature_builder.py
# y /features/forecasting_utils.py y ser importadas aquí.
