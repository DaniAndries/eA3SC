import json
import requests
from flask import Blueprint, render_template, request, jsonify
import config
import logger as D

# Crear un Blueprint para las rutas
app_blueprint = Blueprint("app_blueprint", __name__)

@app_blueprint.route("/")
def index():
    D.info("Cargando pagina inicial")
    return render_template(
        "home.html",
            LOGS=config.LOGS,
            PATH=config.PATH,
            PLATFORM=config.PLATFORM,
            VERSION=config.VERSION,
            CONFIG_PATH=config.CONFIG_PATH,
    )

# Ruta para obtener informacion sobre la plataforma
@app_blueprint.route("/management/home")
def home():
    D.info("Cargando informacion")
    try:
        response = requests.get(config.BASE_URL)
        response.raise_for_status()
        return render_template(
            "home.html",
            LOGS=config.LOGS,
            PATH=config.PATH,
            PLATFORM=config.PLATFORM,
            VERSION=config.VERSION,
            CONFIG_PATH=config.CONFIG_PATH,
        )
    except requests.exceptions.RequestException as e:
        D.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Ruta para obtener informacion sobre la plataforma
@app_blueprint.route("/management/config")
def get_settings():
    D.info("Cargando configuracion")
    try:
        response = requests.get(config.BASE_URL)
        response.raise_for_status()
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)
        return render_template(
            "config.html",
            printers=printers_info,
            config_dict=config.DICT
        )
    except requests.exceptions.RequestException as e:
        D.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app_blueprint.route("/management/config", methods=["POST"])
def save_settings():
    try:
        print(f"Content-Type recibido: {request.content_type}")
        data = request.get_json()

        # Obtener valores del JSON recibido
        NOTIFICATION = data.get("NOTIFICATION")
        EMAIL = data.get("EMAIL")
        PASSWORD = data.get("PASSWORD")
        PORT = data.get("PORT")
        HOST = data.get("HOST")
        TO = data.get("TO")
        CC = data.get("CC")
        SUBJECT = data.get("SUBJECT")
        PRINT_SC = data.get("PRINT_SC")
        TIME_SECONDS = data.get("TIME_SECONDS")
        USER_DB = data.get("USER_DB")
        PASSWORD_DB = data.get("PASSWORD_DB")
        SERVER = data.get("SERVER")
        DATABASE_DB = data.get("DATABASE_DB")

        
        required_fields = [
            NOTIFICATION, EMAIL, PASSWORD, PORT, HOST, TO, CC, SUBJECT,
            PRINT_SC, TIME_SECONDS, USER_DB, PASSWORD_DB, SERVER, DATABASE_DB
        ]

        # Validar que todos los campos estén presentes
        if not all(required_fields):
            return jsonify({"error": "Todos los campos deben ser completados."}), 400

        # Actualizar o agregar valores a la sección MAIL
        if "MAIL" not in config.CONFIG_PARSER:
            config.CONFIG_PARSER["MAIL"] = {}

        config.CONFIG_PARSER["MAIL"]["NOTIFICATION"] = NOTIFICATION
        config.CONFIG_PARSER["MAIL"]["EMAIL"] = EMAIL
        config.CONFIG_PARSER["MAIL"]["PASSWORD"] = PASSWORD
        config.CONFIG_PARSER["MAIL"]["PORT"] = PORT
        config.CONFIG_PARSER["MAIL"]["HOST"] = HOST
        config.CONFIG_PARSER["MAIL"]["TO"] = TO
        config.CONFIG_PARSER["MAIL"]["CC"] = CC
        config.CONFIG_PARSER["MAIL"]["SUBJECT"] = SUBJECT

        # Actualizar o agregar valores a la sección PRINT_SETTINGS
        if "PRINT_SETTINGS" not in config.CONFIG_PARSER:
            config.CONFIG_PARSER["PRINT_SETTINGS"] = {}

        config.CONFIG_PARSER["PRINT_SETTINGS"]["PRINT_SC"] = PRINT_SC
        config.CONFIG_PARSER["PRINT_SETTINGS"]["TIME_SECONDS"] = str(TIME_SECONDS)

        # Actualizar o agregar valores a la sección BD
        if "BD" not in config.CONFIG_PARSER:
            config.CONFIG_PARSER["BD"] = {}

        config.CONFIG_PARSER["BD"]["USER_DB"] = USER_DB
        config.CONFIG_PARSER["BD"]["PASSWORD_DB"] = PASSWORD_DB
        config.CONFIG_PARSER["BD"]["SERVER"] = SERVER
        config.CONFIG_PARSER["BD"]["DATABASE_DB"] = DATABASE_DB

        # Guardar la configuración actualizada en el archivo settings.ini
        with open(config.SETTINGS_PATH, "w") as configfile:
            config.CONFIG_PARSER.write(configfile)
            config.CONFIG_PARSER.update()
            config.DICT = config.update_dict()

        return jsonify({"message": "Configuración guardada correctamente."}), 200

    except Exception as e:
        D.error(f"Error al guardar configuración: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

# Ruta para cargar la pagina de impresion con las impresoras disponibles
@app_blueprint.route("/management/print")
def printer():
    D.info("Cargando pagina de impresion")
    try:
        # Lee la configuración de las impresoras desde config.json
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)
        return render_template("print.html", printers=printers_info)
    except Exception as e:
        D.error(f"Error al obtener impresoras: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Ruta para obtener las impresoras disponibles en el sistema
@app_blueprint.route("/printers", methods=["GET"])
def get_printers():
    D.info("Obteniendo impresoras del cliente")
    try:
        # Abre el archivo de configuración y lee las impresoras
        with open(config.CONFIG_PATH, "r") as archive:
            printers_info = json.load(archive)  # Carga la lista de impresoras del archivo de configuración

        # Obtener la impresora configurada desde el archivo de configuración
        configured_printer = config.CONFIG_PARSER['PRINT_SETTINGS']['PRINT_SC']

        # Asegurarse de que la impresora configurada esté al principio de la lista, sin duplicarla si ya está
        if configured_printer and configured_printer not in printers_info:
            printers_info.remove({"name": configured_printer})  # Eliminar la impresora configurada de la lista
            printers_info.insert(0, {"name": configured_printer})  # Añadir la impresora configurada al principio de la lista

        # Devuelve la lista de impresoras en formato JSON
        if not printers_info:
            raise ValueError("No se encontraron impresoras en la configuración.")

        return jsonify(printers_info)
    except Exception as e:
        D.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
