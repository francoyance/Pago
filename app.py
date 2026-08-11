from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite peticiones de origen cruzado (necesario para Flutter)

# Diccionario de usuarios válidos (usuario: contraseña)
USUARIOS_VALIDOS = {
    "kayser": "1234",
    "admin": "admin2026",
    "usuario2": "abcd",
    "piero": "piero12345678"  # <--- Nuevo usuario agregado aquí
}

@app.route('/login', methods=['POST'])
def login():
    # Obtener los datos JSON enviados desde Flutter
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Datos no proporcionados"}), 400

    usuario = data.get('usuario')
    password = data.get('password')

    # Validar si el usuario existe y la contraseña coincide
    if usuario in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario] == password:
        return jsonify({
            "status": "success",
            "mensaje": f"¡Bienvenido, {usuario}! Inicio de sesión exitoso."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "mensaje": "Usuario o contraseña incorrectos"
        }), 401

if __name__ == '__main__':
    # host='0.0.0.0' permite que la API escuche peticiones desde emuladores o dispositivos en la misma red
    app.run(host='0.0.0.0', port=5000, debug=True)
