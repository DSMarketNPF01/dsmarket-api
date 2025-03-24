# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timedelta
import pickle

from features.feature_builder import generate_dataframe
from features.forecasting_utils import generate_fh_from_date
from events.events_loader import load_events_and_holidays
from data.database import (
    get_env_db_params, get_alloydb_engine,
    get_last_available_date, load_table
)

print("🧠 Cargando modelos de predicción...")
models = pd.read_pickle('models_cluster.pkl')

print("🔗 Conectando a AlloyDB...")
params = get_env_db_params()
engine = get_alloydb_engine(**params)

print("📦 Cargando datos desde AlloyDB...")
df_stores = load_table("historical_sales", engine)[['store', 'store_code']].drop_duplicates().set_index('store')
df_region_map = load_table("region_map", engine)
df_region = df_region_map.set_index("code")
df_prices = load_table("historical_sales", engine)[['id', 'date', 'sell_price']]
prices_bbdd = (
    df_prices.assign(date=pd.to_datetime(df_prices['date']))
    .sort_values(by='date', ascending=False)
    .set_index('id')
)
df_clusters = load_table("clusters", engine).set_index("item")
print("✅ Datos cargados correctamente.")

# Crear la app FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    item: str
    store: str

@app.post("/predict")
def predict(request: PredictionRequest):
    item = request.item
    store = request.store

    print(f"\n📨 Petición recibida: item={item}, store={store}")

    last_date = get_last_available_date(item, store, engine)
    if last_date is None:
        print("❌ No se encontraron datos para esa combinación.")
        return {"error": "No hay datos disponibles para esa combinación item-store"}

    prediction_date = pd.to_datetime(last_date) + timedelta(days=1)
    print(f"📅 Última fecha encontrada: {last_date} → Predicción para: {prediction_date.date()}")

    regions = df_region['city'].unique().tolist()
    events_df, holidays_df = load_events_and_holidays(year=prediction_date.year, regions=regions)
    print("📑 Eventos y festivos cargados para el año y regiones correspondientes.")

    cluster_raw = df_clusters.at[item, 'cluster']
    cluster_value = f"CLUSTER_{float(cluster_raw):.1f}"
    print(f"🔍 Cluster detectado: {cluster_value}")
    model_cluster = models[cluster_value]

    df_input = generate_dataframe(
        store_API=store,
        item_API=item,
        date_API=prediction_date,
        df_stores=df_stores,
        df_region=df_region,
        prices_bbdd=prices_bbdd,
        events_df=events_df,
        holidays_df=holidays_df
    )
    print("📊 Features generadas correctamente.")

    fh = generate_fh_from_date(last_date, horizon=1)
    prediction = model_cluster.predict(fh=fh, X=df_input)
    y_pred = float(prediction.values[0])
    print(f"✅ Predicción realizada: {y_pred:.2f}")

    return {
        "item": item,
        "store": store,
        "date": prediction_date.strftime("%Y-%m-%d"),
        "predicted_sales": round(y_pred, 2)
    }

@app.get("/")
def root():
    return {"message": "API de predicción de ventas funcionando con AlloyDB ✅"}
