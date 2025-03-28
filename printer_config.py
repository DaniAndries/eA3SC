import configparser
import getpass
import json
import os
import win32print
import config
import logger as D

def config_archive():
    """Verifica la existencia del archivo de configuración y su contenido."""
    if os.path.exists(config.CONFIG_PATH):
        with open(config.CONFIG_PATH, "r") as archive:
            if os.stat(config.CONFIG_PATH).st_size == 0:
                D.warning(f"El archivo {config.CONFIG_PATH} está vacío. Inicializando configuración vacía.")
            else:
                D.info(f"El archivo {config.CONFIG_PATH} ya existe. Verificando nuevas impresoras.")
    else:
        D.info(f"Archivo {config.CONFIG_PATH} no existe. Creando archivo de configuración.")

def printers_config():    
    config_archive()

    # Obtiene la lista de impresoras en el formato requerido
    printer_names = [{"name": printer[2]} for printer in win32print.EnumPrinters(2)]

    # Cargar impresoras existentes si el archivo tiene datos
    if os.path.exists(config.CONFIG_PATH) and os.stat(config.CONFIG_PATH).st_size > 0:
        with open(config.CONFIG_PATH, "r") as archive:
            try:
                existing_printers = {tuple(d.items()) for d in json.load(archive)}
            except json.JSONDecodeError:
                existing_printers = set()
    else:
        existing_printers = set()

    current_printers = {tuple(d.items()) for d in printer_names}

    if new_printers := current_printers - existing_printers:
        D.info("Nuevas impresoras encontradas.")

    updated_printers = [dict(p) for p in existing_printers | current_printers]

    # Guardar solo los nombres de las impresoras en el formato deseado
    with open(config.CONFIG_PATH, "w") as archive:
        json.dump(updated_printers, archive, indent=4)
        D.info(f"Archivo de configuración {config.CONFIG_PATH} actualizado con nombres de impresoras.")

# Configuración predeterminada
DEFAULT_CONFIG = {
    "POPUP_MENU": {
        "ico_path": "1024x1024.ico",
        "app_name": "eA3SC - v1.0.0",
        "information_url": "https://www.jnc.es",
        "configuration_url": "http://localhost:19191/management/about",
        "option_1": "Information",
        "option_2": "Settings",
        "option_3": "Exit",
    },
    "SERVICE_NOTIFICATION": {
        "popup_title": "Servicio en ejecución.",
        "popup_text": "Servicio funcionando correctamente.",
    },
    "MAIL_NOTIFICATION": {
        "popup_title": "Mail enviado.",
        "popup_text": "Se ha notificado correctamente a {TO}.",
    },
    "MAIL": {
        "notification": "Servicio funcionando correctamente.",
        "email": "ejemplo@ejemplo.co",
        "password": "ejemplo",
        "port": "ejemplo",
        "host": "ejemplo",
        "to": "ejemplo",
        "cc": "ejemplo",
        "subject": "ejemplo",
    },
    "PRINT_SETTINGS": {
        "print_sc": "",
        "time_seconds": "1",
    },
    "BD": {
        "user_db": "ejemplo",
        "password_db": "ejemplo",
        "server": "ejemplo",
        "database_db": "ejemplo",
    },
}

SETTINGS_PATH = f"C:/Users/{getpass.getuser()}/AppData/Local/eA3SC"
SETTINGS_FILE = f"{SETTINGS_PATH}/settings.ini"
def create_config_file():
    os.mkdir(SETTINGS_PATH)
    config = configparser.ConfigParser()
    
    for section, values in DEFAULT_CONFIG.items():
        config[section] = values

    with open(SETTINGS_FILE, "w") as configfile:
        config.write(configfile)
    print(f"{SETTINGS_FILE} ha sido creado correctamente.")

# Si el archivo no existe, lo creamos
if not os.path.exists(SETTINGS_FILE):
    create_config_file()

# Ahora cargamos la configuración
config.CONFIG_PARSER = configparser.ConfigParser()
config.CONFIG_PARSER.read(SETTINGS_FILE)

