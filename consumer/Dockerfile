# versión ligera de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos e instalamos dependencias primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos nuestro código
COPY main.py .

# Ejecutamos el script. El flag "-u" es un truco para que los "print" 
# se vean en tiempo real en la terminal de Ubuntu.
CMD ["python", "-u", "main.py"]