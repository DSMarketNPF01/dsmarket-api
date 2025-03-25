# Usa una versión moderna y estable de Python
FROM python:3.11-slim
 
# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivos necesarios al contenedor
COPY requirements.txt .
COPY api.py .
COPY models_cluster.pkl .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080 (requerido por Cloud Run)
EXPOSE 8080

# Comando para ejecutar la API cuando el contenedor se inicie
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]