# Usar Python 3.12 slim como base
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p /app/logs

# Exponer el puerto
EXPOSE 8083

# Variable de entorno por defecto
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
