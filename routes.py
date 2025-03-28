import json
import os
import requests
from flask import Blueprint, render_template, request, jsonify
import config
import logger as D
import win32api
import win32print

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
        
        # Devuelve la lista de impresoras en formato JSON
        if not printers_info:
            raise ValueError("No se encontraron impresoras en la configuración.")

        return jsonify(printers_info)
    except Exception as e:
        D.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app_blueprint.route("/printers/<printer_id>", methods=["POST"])
def print_document(printer_id):
    try:
        hprinter = win32print.OpenPrinter(printer_id)

        # Obtiene el archivo y el numero de copias desde la solicitud
        file = request.files["file"]
        copies = int(
            request.form.get("copies", 1)
        )  # Valor predeterminado de 1 copia si no se especifica

        # Guarda el archivo en la carpeta temporal
        temp_folder = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_folder, exist_ok=True)
        file_path = os.path.join(temp_folder, file.filename)
        file.save(file_path)

        # Verifica que el archivo se haya guardado correctamente
        if not os.path.exists(file_path):
            return jsonify({"error": "Archivo no encontrado"}), 400

        # Determina la extension del archivo para procesarlo adecuadamente
        file_extension = file.filename.rsplit(".", 1)[-1].lower()

        with open(file_path, "rb") as f:
            data = f.read()
            # Imprime el archivo la cantidad de veces indicada
            for _ in range(copies):
                try:
                    # Empieza un trabajo de impresion con el nombre del archivo
                    job_info = (
                        file.filename,
                        None,
                        "RAW",
                    )  # Usa el nombre real del archivo
                    win32print.StartDocPrinter(hprinter, 1, job_info)

                    try:
                        win32print.StartPagePrinter(hprinter)
                        win32print.WritePrinter(
                            hprinter, data
                        )  # Envia los datos a la impresora

                        win32print.EndPagePrinter(hprinter)
                    finally:
                        win32print.EndDocPrinter(hprinter)
                except Exception as e:
                    print(f"Error al imprimir: {e}")

        return jsonify({"message": "Documento enviado a imprimir"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500