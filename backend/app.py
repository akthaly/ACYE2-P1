from flask import Flask, request, jsonify
from functools import wraps
import pymongo
import jwt
import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permite que el frontend web se conecte sin errores

# Configuración de seguridad para los Tokens JWT
app.config['SECRET_KEY'] = 'super-secreto-park'
MONGO_HOST = os.getenv("MONGO_HOST", "park_db")

# Conexión a la Base de Datos NoSQL
cliente_mongo = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:27017/")
db = cliente_mongo["park_db"]
coleccion_usuarios = db["usuarios_rfid"]

def token_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = None
        # El frontend debe enviar el token en el header 'Authorization' como 'Bearer <token>'
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'mensaje': 'Falta el token. Acceso denegado.'}), 401

        try:
            # Intentamos desencriptar el token usando nuestra clave secreta
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            usuario_actual = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'mensaje': 'El token ha expirado. Vuelve a iniciar sesión.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensaje': 'Token inválido.'}), 401

        # Si el token es válido, dejamos pasar a la ruta original
        return f(usuario_actual, *args, **kwargs)
    
    return decorador

# --- RUTA 1: Login y Generación de Token JWT ---
@app.route('/api/login', methods=['POST'])
def login():
    datos = request.json
    # Usuario administrador quemado por ahora para pruebas
    if datos and datos.get('username') == 'admin' and datos.get('password') == '1234':
        token = jwt.encode({
            'user': 'admin',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2) # El token expira en 2 horas
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token}), 200
    
    return jsonify({'mensaje': 'Credenciales inválidas'}), 401

# --- RUTA 2: Crear un Usuario RFID (AHORA PROTEGIDA) ---
@app.route('/api/usuarios', methods=['POST'])
@token_requerido # <--- ¡Aquí pusimos el candado!
def crear_usuario(usuario_actual): # Recibe el usuario_actual que le pasa el decorador
    nuevo_usuario = request.json
    coleccion_usuarios.insert_one(nuevo_usuario)
    nuevo_usuario.pop('_id', None)
    
    # Podemos incluso registrar quién creó este usuario
    return jsonify({
        'mensaje': 'Usuario registrado exitosamente', 
        'creado_por': usuario_actual,
        'data': nuevo_usuario
    }), 201


if __name__ == '__main__':
    # El host '0.0.0.0' es obligatorio para que funcione dentro de Docker
    app.run(host='0.0.0.0', port=5000)