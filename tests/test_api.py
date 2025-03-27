import pytest
import sys
import os
from fastapi.testclient import TestClient


# Agregar la raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_web import app  # Importamos la API desde `api.py`

client = TestClient(app)

def test_read_root():
    """Prueba la ruta raíz (/)"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API de predicción de ventas en funcionamiento"}

def test_predict():
    """Prueba la ruta /predict con datos de ejemplo"""
    sample_input = {
        "year": 2025,
        "month": 3,
        "quarter": 1,
        "week": 13,
        "day": 26,
        "weekday_int": 1,
        "w": 9,
        "holidays_boolean": 0,
        "event_boolean": 0,
        "lag_1": 23350.0,
        "lag_7": 30599.0,
        "lag_14": 32225.0,
        "lag_21": 31202.0,
        "lag_28": 29908.0,
        "lag_1_inc": 0.0364,
        "lag_7_inc": -0.0344,
        "lag_14_inc": -0.0749,
        "lag_21_inc": -0.1774,
        "lag_28_inc": -0.0834
    }
    
    response = client.post("/predict", json=sample_input)
    
    assert response.status_code == 200
    assert "predicted_sales" in response.json()
