import time  # Asegurar que esté importado al inicio
import os
import threading
from flask import Flask
import logger as D
from printer_config import printers_config
import routes
from tray_popup import popup

# Variable global para controlar el estado de la aplicación
APPLICATION_RUNNING = True
# Función de cierre modificada
def shutdown_application():
    global APPLICATION_RUNNING
    if APPLICATION_RUNNING:
        APPLICATION_RUNNING = False
        D.info("Cerrando la aplicación...")
        os._exit(0)  # Forzar cierre de todos los hilos

# Función que revisa si el hilo sigue vivo
def monitor_threads():
    global popup_thread, APPLICATION_RUNNING
    while APPLICATION_RUNNING:
        # Verificar estado de todos los hilos críticos
        if not popup_thread.is_alive():
            D.info("El popup ha finalizado.")
            shutdown_application()
        time.sleep(1)  # Evita consumir demasiados recursos

# Configuración y logger
D.Logger("logs")
app = Flask(__name__)
app.register_blueprint(routes.app_blueprint)

# Iniciar la función de configuración de impresoras
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    printers_config()
    # Inicia un hilo para el popup
    popup_thread = threading.Thread(target=popup, daemon=True)
    popup_thread.start()

    # Inicia otro hilo para monitorear la aplicación
    monitor_thread = threading.Thread(target=monitor_threads, daemon=True)
    monitor_thread.start()

# Manejar el cierre de Flask
@app.route("/shutdown", methods=["POST"])
def shutdown():
    shutdown_application()
    return "Servidor detenido"

if __name__ == "__main__":
    try:
        app.run()
    except KeyboardInterrupt:
        D.info("Deteniendo la aplicación manualmente...")
        shutdown_application()
    except Exception as e:
        D.info(f"Error inesperado: {e}")
        shutdown_application()