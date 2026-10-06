from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)  # Permite peticiones de origen cruzado para Flutter

# Estructura de usuarios más completa (Simulando una Base de Datos)
USUARIOS_DB = {
    "franco": {
        "password": generate_password_hash("franco2000"),
        "device_id": None,  # Al inicio no tiene dispositivo vinculado
        "membresia_inicio": "2026-01-01",
        "membresia_fin": "2026-12-31",  # Membresía activa por defecto para pruebas
    },
    "fabian": {
        "password": generate_password_hash("fabian2026"),
        "device_id": None,
        "membresia_inicio": "2026-01-01",
        "membresia_fin": "2026-03-01",  # Membresía vencida para pruebas
    },
    "giusepe": {
        "password": generate_password_hash("giusepe1234"),
        "device_id": None,
        "membresia_inicio": "2026-01-01",
        "membresia_fin": "2026-12-31",
    },
    "junior": {
        "password": generate_password_hash("junior123"),
        "device_id": None,
        "membresia_inicio": "2026-01-01",
        "membresia_fin": "2026-10-04",
    },
}


@app.route("/", methods=["GET"])
def home():
  return (
      jsonify({
          "status": "online",
          "mensaje": "API de Autenticación y Membresías funcionando",
      }),
      200,
  )


@app.route("/login", methods=["POST"])
def login():
  try:
    data = request.get_json()
    if not data:
      return jsonify({"status": "error", "mensaje": "Datos no proporcionados"}), 400

    usuario = data.get("usuario", "").strip().lower()
    password = data.get("password", "")
    device_id = data.get("device_id", "").strip()  # ID único del móvil desde Flutter

    if not usuario or not password or not device_id:
      return (
          jsonify({
              "status": "error",
              "mensaje": "Usuario, contraseña y device_id son obligatorios",
          }),
          400,
      )

    # Validar si el usuario existe
    if usuario not in USUARIOS_DB:
      return (
          jsonify({
              "status": "error",
              "mensaje": "Usuario o contraseña incorrectos",
          }),
          401,
      )

    user_data = USUARIOS_DB[usuario]

    # Validar contraseña
    if not check_password_hash(user_data["password"], password):
      return (
          jsonify({
              "status": "error",
              "mensaje": "Usuario o contraseña incorrectos",
          }),
          401,
      )

    # 1. Validar la Membresía por fechas
    hoy = datetime.now().date()
    try:
      fecha_fin = datetime.strptime(
          user_data["membresia_fin"], "%Y-%m-%d"
      ).date()
    except Exception:
      fecha_fin = hoy  # Por seguridad si hay formato inválido

    if hoy > fecha_fin:
      return (
          jsonify({
              "status": "error",
              "codigo": "MEMBRESIA_VENCIDA",
              "mensaje": (
                  "Membresía vencida. Su acceso ha expirado, por favor renueve"
                  " su afiliación."
              ),
          }),
          403,
      )

    # 2. Validar el Dispositivo Vinculado
    if user_data["device_id"] is None:
      # Primer inicio de sesión: Vinculamos este dispositivo
      user_data["device_id"] = device_id
    elif user_data["device_id"] != device_id:
      # Ya tiene otro dispositivo vinculado
      return (
          jsonify({
              "status": "error",
              "codigo": "DISPOSITIVO_NO_AUTORIZADO",
              "mensaje": (
                  "Esta cuenta ya se encuentra vinculada a otro dispositivo"
                  " móvil. Debe restablecerlo para iniciar sesión aquí."
              ),
          }),
          403,
      )

    return (
        jsonify({
            "status": "success",
            "mensaje": f"¡Bienvenido, {usuario}! Inicio de sesión exitoso.",
            "usuario": usuario,
            "membresia_fin": user_data["membresia_fin"],
        }),
        200,
    )

  except Exception as e:
    return (
        jsonify({
            "status": "error",
            "mensaje": "Ocurrió un error interno en el servidor",
            "detalles": str(e),
        }),
        500,
    )


# Endpoint PUT para restablecer/borrar el dispositivo vinculado
@app.route("/usuario/<usuario>/reset-device", methods=["PUT"])
def reset_device(usuario):
  usuario = usuario.strip().lower()
  if usuario not in USUARIOS_DB:
    return jsonify({"status": "error", "mensaje": "Usuario no encontrado"}), 404

  # Limpiamos el device_id
  USUARIOS_DB[usuario]["device_id"] = None
  return (
      jsonify({
          "status": "success",
          "mensaje": (
              f"Dispositivo del usuario '{usuario}' restablecido correctamente."
              " Ya puede vincular uno nuevo."
          ),
      }),
      200,
  )


# Endpoint PUT para configurar la membresía (fecha inicio y fecha fin)
@app.route("/usuario/<usuario>/membresia", methods=["PUT"])
def actualizar_membresia(usuario):
  try:
    usuario = usuario.strip().lower()
    if usuario not in USUARIOS_DB:
      return (
          jsonify({"status": "error", "mensaje": "Usuario no encontrado"}),
          404,
      )

    data = request.get_json()
    if not data:
      return jsonify({"status": "error", "mensaje": "Datos no proporcionados"}), 400

    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")

    if not fecha_inicio or not fecha_fin:
      return (
          jsonify({
              "status": "error",
              "mensaje": (
                  "Se requieren 'fecha_inicio' y 'fecha_fin' en formato YYYY-MM-DD"
              ),
          }),
          400,
      )

    # Validar formato de fechas básico
    datetime.strptime(fecha_inicio, "%Y-%m-%d")
    datetime.strptime(fecha_fin, "%Y-%m-%d")

    # Actualizar en la BD simulada
    USUARIOS_DB[usuario]["membresia_inicio"] = fecha_inicio
    USUARIOS_DB[usuario]["membresia_fin"] = fecha_fin

    return (
        jsonify({
            "status": "success",
            "mensaje": f"Membresía actualizada para el usuario '{usuario}'.",
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        }),
        200,
    )

  except ValueError:
    return (
        jsonify({
            "status": "error",
            "mensaje": (
                "Formato de fecha inválido. Utilice el formato YYYY-MM-DD."
            ),
        }),
        400,
    )
  except Exception as e:
    return (
        jsonify({
            "status": "error",
            "mensaje": "Error al actualizar la membresía",
            "detalles": str(e),
        }),
        500,
    )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
