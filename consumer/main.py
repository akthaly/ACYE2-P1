import paho.mqtt.client as mqtt
import pymongo
import json
from datetime import datetime
import os

# Usamos los nombres de los contenedores que definimos en docker-compose
MONGO_HOST = os.getenv("MONGO_HOST", "park_db")
MQTT_HOST = os.getenv("MQTT_HOST", "park_broker")

# 1. Conexión a MongoDB
cliente_mongo = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:27017/")
db = cliente_mongo["park_db"]
coleccion_eventos = db["eventos"]

def on_connect(client, userdata, flags, rc):
    print(f"Conectado al Broker MQTT con código: {rc}")
    # Nos suscribimos a todo lo que pase en el parqueo
    client.subscribe("parkguard/#")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        topic = msg.topic
        
        # 2. Clasificación de eventos según la rúbrica
        tipo_evento = "log_general"
        if "acceso" in topic:
            tipo_evento = "intento_acceso"
        elif "emergencia" in topic:
            tipo_evento = "emergencia_activada"
        elif "ocupacion" in topic:
            tipo_evento = "cambio_ocupacion"
        elif "ventilador" in topic:
            tipo_evento = "accion_ventilador"

        # 3. Armar el documento
        nuevo_evento = {
            "tipo_evento": tipo_evento,
            "origen": topic,
            "detalle": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 4. Guardar en Base de Datos NoSQL
        coleccion_eventos.insert_one(nuevo_evento)
        print(f"[{tipo_evento}] guardado exitosamente desde {topic}")
        
    except json.JSONDecodeError:
        print(f"Error: El mensaje en {msg.topic} no es un JSON válido.")
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Iniciando Consumer... Conectando a {MQTT_HOST}")
client.connect(MQTT_HOST, 1883, 60)

# Mantener el script escuchando infinitamente
client.loop_forever()