import pymssql

def db():
    conn = pymssql.connect('localhost', 'sa', 'A3erp48.', 'Pruebas', autocommit=True)
    try:
        db = conn.cursor(as_dict=True)
    except Exception as e:
        return e
    with db:
            db.execute("SELECT * FROM PAISES")
            result = db.fetchone()
            print(result)
