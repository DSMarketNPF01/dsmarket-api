from fastapi import FastAPI
import pickle
import pandas as pd
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Cargar el modelo desde el archivo .pkl
with open("best_model.pkl", "rb") as f:
    model = pickle.load(f)

# Crear la aplicación FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes (puedes restringirlo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para validación
class SalesInput(BaseModel):
    year: int
    month: int
    quarter: int
    week: int
    day: int
    weekday_int: int
    w: int
    holidays_boolean: int
    event_boolean: int
    lag_1: float
    lag_7: float
    lag_14: float
    lag_21: float
    lag_28: float
    lag_1_inc: float
    lag_7_inc: float
    lag_14_inc: float
    lag_21_inc: float
    lag_28_inc: float

@app.post("/predict")
def predict(sales_input: SalesInput):
    # Convertir entrada en DataFrame
    # data = pd.DataFrame([sales_input.dict()])
    expected_columns = ["year", "month", "quarter", "week", "day", "weekday_int", "w",
                    "holidays_boolean", "event_boolean", "lag_1", "lag_7", "lag_14",
                    "lag_21", "lag_28", "lag_1_inc", "lag_7_inc", "lag_14_inc",
                    "lag_21_inc", "lag_28_inc"]

    data = pd.DataFrame([sales_input.model_dump()], columns=expected_columns)

    
    # Hacer la predicción
    prediction = model.predict(fh=[1], X=data)

    # Extraer el valor limpio de la predicción
    predicted_value = float(prediction.values[0][0]) if isinstance(prediction.values[0], list) else float(prediction.values[0])

    return {"predicted_sales": round(predicted_value, 2)}

@app.get("/")
def read_root():
    return {"message": "API de predicción de ventas en funcionamiento"}
