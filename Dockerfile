# Usa una versión moderna y estable de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo los archivos necesarios para instalar dependencias primero (cache de capas Docker)
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código (incluyendo subcarpetas)
COPY . .

# Expón el puerto requerido por Cloud Run
EXPOSE 8080

# Comando para ejecutar la API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
