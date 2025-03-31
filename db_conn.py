import pymssql

import config

def connect_db():
    conn = pymssql.connect(
    config.DICT.get("SERVER"),
    config.DICT.get("USER_DB"),
    config.DICT.get("PASSWORD_DB"),
    config.DICT.get("DATABASE_DB"),
    autocommit=True
    	)
    try:
        db = conn.cursor(as_dict=True)
    except Exception as e:
        return e
