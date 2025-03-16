# DS Market API

Esta API de predicción de ventas está desplegada en Google Cloud Run y se actualiza automáticamente con Cloud Build.

## 🔹 Cómo usar

1️⃣ Enviar una petición `POST` a `/predict` con un JSON de datos.  
2️⃣ Recibirás la predicción de ventas en respuesta.

## 🔹 Despliegue Automático (CI/CD)
Cada vez que hagas `git push`, Google Cloud Build:
✔ Construirá una imagen Docker.  
✔ Subirá la imagen a Artifact Registry.  
✔ Desplegará la API en Cloud Run.

## 🔹 Ejemplo de uso con `curl`
```sh
curl -X 'POST' \
  'https://tu-api-en-cloud-run/predict' \
  -H 'Content-Type: application/json' \
  -d '{
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
  }'
