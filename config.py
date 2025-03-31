import getpass
import configparser
import platform

# ---------------------------------------------------------------------------------
# -------------------------------Flask    Config-----------------------------------

PORT = 19191
BASE_URL = f"http://127.0.0.1:{PORT}/"

# ---------------------------------------------------------------------------------
# ----------------------------------Program  Data----------------------------------

VERSION = 1.1
PLATFORM = platform.system()
PATH = f"C:/Users/{getpass.getuser()}/AppData/Local/eA3SC"
CONFIG_PATH = f"{PATH}/config.json"
SETTINGS_PATH = f"{PATH}/settings.ini"
LOGS = f"{PATH}/Logs"

CONFIG_PARSER = configparser.ConfigParser()
CONFIG_PARSER.read(SETTINGS_PATH)

# ---------------------------------------------------------------------------------
# -----------------------------------[Dictionary]----------------------------------

def update_dict():
    return {
    "NOTIFY": CONFIG_PARSER['MAIL']['NOTIFY'],
    "NOTIFICATION": CONFIG_PARSER['MAIL']['NOTIFICATION'],
    "EMAIL": CONFIG_PARSER['MAIL']['EMAIL'],
    "PASSWORD": CONFIG_PARSER['MAIL']['PASSWORD'],
    "PORT": CONFIG_PARSER['MAIL']['PORT'],
    "HOST": CONFIG_PARSER['MAIL']['HOST'],
    "TO": CONFIG_PARSER['MAIL']['TO'],
    "CC": CONFIG_PARSER['MAIL']['CC'],
    "SUBJECT": CONFIG_PARSER['MAIL']['SUBJECT'],
    "PRINT_SC": CONFIG_PARSER['PRINT_SETTINGS']['PRINT_SC'],
    "TIME_SECONDS": int(CONFIG_PARSER['PRINT_SETTINGS']['TIME_SECONDS']),
    "USER_DB": CONFIG_PARSER['BD']['USER_DB'],
    "PASSWORD_DB": CONFIG_PARSER['BD']['PASSWORD_DB'],
    "SERVER": CONFIG_PARSER['BD']['SERVER'],
    "DATABASE_DB": CONFIG_PARSER['BD']['DATABASE_DB'],
    }

DICT = {}

# # ---------------------------------------------------------------------------------
# #---------------------------[SERVICE_NOTIFICATION]
# POPUP_TITLE = CONFIG_PARSER['SERVICE_NOTIFICATION']['POPUP_TITLE']
# POPUP_TEXT = CONFIG_PARSER['SERVICE_NOTIFICATION']['POPUP_TEXT']

# # ---------------------------------------------------------------------------------
# #---------------------------[MAIL_NOTIFICATION]
# MAIL_POPUP_TITLE = CONFIG_PARSER['MAIL_NOTIFICATION']['POPUP_TITLE']
# MAIL_POPUP_TEXT = CONFIG_PARSER['MAIL_NOTIFICATION']['POPUP_TEXT']

# # ---------------------------------------------------------------------------------
# #---------------------------[MAIL]
# NOTIFICATION = CONFIG_PARSER['MAIL']['NOTIFICATION']
# EMAIL = CONFIG_PARSER['MAIL']['EMAIL']
# PASSWORD = CONFIG_PARSER['MAIL']['PASSWORD']
# PORT = CONFIG_PARSER['MAIL']['PORT']
# HOST = CONFIG_PARSER['MAIL']['HOST']
# TO = CONFIG_PARSER['MAIL']['TO']
# CC = CONFIG_PARSER['MAIL']['CC']
# SUBJECT = CONFIG_PARSER['MAIL']['SUBJECT']

# # ---------------------------------------------------------------------------------
# #---------------------------[PRINT_SETTINGS]
# PRINT_SC = CONFIG_PARSER['PRINT_SETTINGS']['PRINT_SC']
# TIME_SECONDS = int(CONFIG_PARSER['PRINT_SETTINGS']['TIME_SECONDS'])

# # ---------------------------------------------------------------------------------
# #---------------------------[BD]
# USER_DB = CONFIG_PARSER['BD']['USER_DB']
# PASSWORD_DB = CONFIG_PARSER['BD']['PASSWORD_DB']
# SERVER = CONFIG_PARSER['BD']['SERVER']
# DATABASE_DB = CONFIG_PARSER['BD']['DATABASE_DB']
