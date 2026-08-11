from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite peticiones de origen cruzado (necesario para Flutter)

# Credenciales estáticas en código
USUARIO_CORRECTO = "kayser"
PASSWORD_CORRECTO = "1234"

@app.route('/login', methods=['POST'])
def login():
    # Obtener los datos JSON enviados desde Flutter
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Datos no proporcionados"}), 400

    usuario = data.get('usuario')
    password = data.get('password')

    # Validar credenciales
    if usuario == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
        return jsonify({
            "status": "success",
            "mensaje": "¡Bienvenido! Inicio de sesión exitoso."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "mensaje": "Usuario o contraseña incorrectos"
        }), 401

if __name__ == '__main__':
    # host='0.0.0.0' permite que la API escuche peticiones desde emuladores o dispositivos en la misma red
    app.run(host='0.0.0.0', port=5000, debug=True)