# Usa una versión moderna y estable de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor (df_total.pkl está excluido por .dockerignore)
COPY . /app

# Instalar las dependencias del proyecto desde el archivo requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que la API se ejecutará (por ejemplo, 8000 para FastAPI)
EXPOSE 8000

# Comando para ejecutar la API (suponiendo que uses FastAPI, puedes ajustarlo según el framework)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
