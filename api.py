from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from datetime import timedelta
import pickle

from features.feature_builder import generate_dataframe
from features.forecasting_utils import generate_fh_from_date
from events.events_loader import load_events_and_holidays
from data.database import (
    get_env_db_params, get_alloydb_engine,
    get_last_available_date, load_table,
    get_weight_for_id_and_date
)

print("🧠 Cargando modelos de predicción...")
models = pd.read_pickle('models_cluster.pkl')

print("🔗 Conectando a AlloyDB...")
params = get_env_db_params()
engine = get_alloydb_engine(**params)

print("📦 Cargando mapa de regiones...")
df_region_map = load_table("region_map", engine)
df_region = df_region_map.set_index("code")
print("✅ Región cargada correctamente.")

# NUEVAS FUNCIONES DE CONSULTA PUNTUAL
def get_store_code(store: str) -> str:
    query = "SELECT store_code FROM historical_sales WHERE store = %s LIMIT 1"
    result = pd.read_sql_query(query, engine, params=(store,))
    return result.iloc[0]['store_code'] if not result.empty else "UNKNOWN"

def get_cluster_for_item(item: str) -> str:
    query = "SELECT cluster FROM clusters WHERE item = %s"
    result = pd.read_sql_query(query, engine, params=(item,))
    cluster = result.iloc[0]['cluster'] if not result.empty else 0
    return f"CLUSTER_{float(cluster):.1f}"

def get_latest_price(item_store_id: str, date: str) -> float:
    query = """
        SELECT sell_price FROM historical_sales
        WHERE id = %s AND date <= %s
        ORDER BY date DESC
        LIMIT 1
    """
    result = pd.read_sql_query(query, engine, params=(item_store_id, date))
    return float(result.iloc[0]['sell_price']) if not result.empty else None

# FastAPI app
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

    # Cargar eventos y festivos
    regions = df_region['city'].unique().tolist()
    events_df, holidays_df = load_events_and_holidays(year=prediction_date.year, regions=regions)

    # Obtener store_code y región
    store_code = get_store_code(store)
    region_code = store_code.split('_')[0]
    region = df_region['city'].get(region_code, "Unknown")

    # Obtener cluster y modelo
    cluster_value = get_cluster_for_item(item)
    model_cluster = models.get(cluster_value)
    if not model_cluster:
        return {"error": f"No se encontró modelo para {cluster_value}"}
    print(f"🔍 Cluster detectado: {cluster_value}")

    # Obtener precio
    id_item_store = f"{item}_{store_code}"
    sell_price = get_latest_price(id_item_store, str(last_date))

    # Obtener peso del id dentro del cluster
    # prediction_date o last_date?
    id_item_store_weight = get_weight_for_id_and_date(id_item_store, last_date, engine)


    # Generar features
    df_input = generate_dataframe(
        store_code=store_code,
        region=region,
        item=item,
        date_API=prediction_date,
        sell_price=sell_price,
        events_df=events_df,
        holidays_df=holidays_df
    )
    print("📊 Features generadas correctamente.")

    # Generar horizonte y predecir
    fh = generate_fh_from_date(last_date, horizon=1)
    prediction = model_cluster.predict(fh=fh, X=df_input)
    y_pred = float(prediction.values[0])
    y_pred_weighted = y_pred * id_item_store_weight
    print(f"✅ Predicción realizada: {y_pred_weighted:.2f}")

    return {
        "item": item,
        "store": store,
        "date": prediction_date.strftime("%Y-%m-%d"),
        "predicted_sales": round(y_pred_weighted, 2)
    }

@app.get("/")
def root():
    return {"message": "API de predicción de ventas funcionando con AlloyDB ✅"}
