import configparser
import getpass
import json
import os
import win32print
import win32ui
import config
import logger as D

def config_archive():
    # Verifica si el archivo de configuracion existe y si esta vacio
    if os.path.exists(config.CONFIG_PATH):
        with open(config.CONFIG_PATH, "r") as archive:
            if os.stat(config.CONFIG_PATH).st_size == 0:
                D.warning(
                    f"El archivo {config.CONFIG_PATH} está vacío. Inicializando configuración vacía."
                )
                return []
            else:
                printers_info = json.load(archive)
                D.info(
                    f"El archivo {config.CONFIG_PATH} ya existe. Verificando nuevas impresoras."
                )
            return printers_info
    else:
        D.info(
            f"Archivo {config.CONFIG_PATH} no existe. Creando archivo de configuración."
        )
        return []

# Funcion que configura las impresoras (crea el archivo si no existe)
def printers_config():
    printers_info = config_archive()

    # Obtiene las impresoras del sistema
    printer_names = [printer[2] for printer in win32print.EnumPrinters(2)]

    # Recorre las impresoras y añade las nuevas
    existing_printers = {printer["name"] for printer in printers_info}
    for printer in printer_names:
        if printer not in existing_printers:
            printer_config = get_printer_config(printer)
            printers_info.append(printer_config)
            D.info(
                f"Impresora nueva encontrada: {printer}. Se añadió al archivo de configuración."
            )

    # Repara campos faltantes (incluyendo el DPI, solo si es necesario)
    for printer in printers_info:
        # Actualiza el DPI solo si falta en la configuracion
        get_printer_dpi(printer)
        # Repara otros campos faltantes
        fix_missing_fields(printer)

    # Guarda la configuracion (creada o actualizada)
    with open(config.CONFIG_PATH, "w") as archive:
        json.dump(printers_info, archive, indent=4)
        D.info(f"Archivo de configuración {config.CONFIG_PATH} actualizado.")
        config.DICT = config.update_dict()

# Funcion para obtener la configuracion inicial de la impresora
def get_printer_config(printer):
    try:
        attributes = get_printer_attributes(printer)
        return {
            "name": printer,
            "duplex": attributes["duplex"],
            "copies": 1,
            "sides": 1,
            "dpi": attributes["dpi"],
            "max_dpi": attributes["dpi"],
        }
    except Exception as e:
        D.error(f"Error al obtener información de la impresora {printer}: {str(e)}")
        return {
            "name": printer,
            "duplex": False,
            "copies": 1,
            "sides": 1,
            "dpi": attributes["dpi"],
            "max_dpi": attributes["dpi"],
        }

# Funcion para verificar y reparar campos faltantes en la configuracion
def fix_missing_fields(printer_config):
    # Si falta el campo 'duplex', lo actualiza usando get_printer_attributes
    if "duplex" not in printer_config:
        attributes = get_printer_attributes(printer_config["name"])
        printer_config["duplex"] = attributes["duplex"]
    # Si faltan 'copies' o 'sides', se asigna el valor por defecto 1
    if "copies" not in printer_config:
        printer_config["copies"] = 1
    if "sides" not in printer_config:
        printer_config["sides"] = 1
    # El DPI ya se actualiza con get_printer_dpi si falta
    return printer_config


# Funcion para obtener los atributos basicos de la impresora: DPI y duplex.
def get_printer_attributes(printer):
    try:
        dpi = get_printer_dpi({"name": printer})

        printer_handle = win32print.OpenPrinter(printer)
        printer_info = win32print.GetPrinter(printer_handle, 2)
        dev_mode = printer_info.get("pDevMode", None)
        duplex = (
            dev_mode.Duplex > 1 if dev_mode and hasattr(dev_mode, "Duplex") else False
        )
        win32print.ClosePrinter(printer_handle)

        return {"dpi": dpi, "duplex": duplex}
    except Exception as e:
        D.error(f"Error al obtener atributos de la impresora {printer}: {str(e)}")
        return {"dpi": 200, "duplex": False}


# Funcion que obtiene el DPI, pero solo se ejecuta si el campo "dpi" no esta definido o es falsy.
def get_printer_dpi(printer_config):  # sourcery skip: extract-method
    if not printer_config.get("dpi"):
        try:
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_config["name"])
            horizontal_dpi = hDC.GetDeviceCaps(88)
            vertical_dpi = hDC.GetDeviceCaps(90)
            dpi = (
                horizontal_dpi
                if horizontal_dpi == vertical_dpi
                else min(horizontal_dpi, vertical_dpi)
            )
            printer_config["dpi"] = dpi
            D.info(f"DPI obtenido para {printer_config['name']}: {dpi}")
        except Exception as e:
            D.error(f"Error al obtener DPI para {printer_config['name']}: {str(e)}")
            printer_config["dpi"] = 200  # Valor por defecto en caso de error
    return printer_config["dpi"]

# Configuración predeterminada
DEFAULT_CONFIG = {
    "POPUP_MENU": {
        "ico_path": "1024x1024.ico",
        "app_name": "eA3SC - v1.0.0",
        "information_url": "https://www.jnc.es",
        "configuration_url": "http://localhost:19191/management/home",
        "option_1": "Information",
        "option_2": "Settings",
        "option_3": "Exit",
    },
    "SERVICE_NOTIFICATION": {
        "popup_title": "Servicio funcionando correctamente",
        "popup_text": "Servicio funcionando correctamente.",
    },
    "MAIL_NOTIFICATION": {
        "popup_title": "Mail enviado.",
        "popup_text": "Se ha notificado correctamente a {TO}.",
    },
    "MAIL": {
        "notify": "off",
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
    if not os.path.isdir(SETTINGS_PATH):
        os.mkdir(SETTINGS_PATH)
    config = configparser.ConfigParser()

    for section, values in DEFAULT_CONFIG.items():
        config[section] = values

    with open(SETTINGS_FILE, "w") as configfile:
        config.write(configfile)
    D.info(f"{SETTINGS_FILE} ha sido creado correctamente.")

# Si el archivo no existe, lo creamos
if not os.path.exists(SETTINGS_FILE):
    create_config_file()

# Ahora cargamos la configuración
config.CONFIG_PARSER = configparser.ConfigParser()
config.CONFIG_PARSER.read(SETTINGS_FILE)

