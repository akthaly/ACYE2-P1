FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Exponemos el puerto 5000 donde correrá Flask
EXPOSE 5000

# Comando para ejecutar la API
CMD ["python", "app.py"]