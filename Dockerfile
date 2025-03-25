# Usa una versión moderna y estable de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Actualizar pip e instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la API
COPY api.py .
COPY run_local.py .
COPY features/ ./features/
COPY events/ ./events/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Opcional: Copiar modelos si no los descargas desde un storage externo
COPY models_cluster.pkl .
COPY df_cluster_ST.pkl .

# Exponer el puerto 8080 (requerido por Cloud Run)
EXPOSE 8080

# Comando para ejecutar la API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]