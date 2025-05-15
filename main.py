"""
EcoSmart Advisor
Una aplicación inteligente que asesora a los usuarios sobre qué sistema 
de energía renovable les conviene instalar según su ubicación y condiciones.
"""
import os
import sys
import logging
import traceback
from flask import Flask, render_template

from ecosmart_advisor.app import create_app

# Configurar logging para capturar todos los errores y depurar
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ecosmart.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Iniciando EcoSmart Advisor")

# Configurar manejo de errores no capturados
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Excepción no capturada:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# Verificar que las variables de entorno estén disponibles
unsplash_key = os.environ.get("UNSPLASH_API_KEY")
if unsplash_key:
    logger.info(f"UNSPLASH_API_KEY está configurada correctamente (longitud: {len(unsplash_key)})")
else:
    logger.warning("UNSPLASH_API_KEY no está configurada")

if __name__ == "__main__":
    try:
        # Crear la aplicación con manejador de errores personalizado
        app = create_app()
        
        # Registrar manejador de errores para diagnóstico detallado
        @app.errorhandler(Exception)
        def handle_error(e):
            error_traceback = traceback.format_exc()
            logger.error(f"Error 500 en la aplicación: {str(e)}")
            logger.error(error_traceback)
            return render_template('error.html', 
                                 error=str(e), 
                                 trace=error_traceback if app.debug else None), 500
        
        # Using 0.0.0.0 to make it accessible outside localhost
        # Try several ports, starting with 8080 which is often available in Replit
        ports_to_try = [8080, 8000, 5001, 5002, 5003, 5004, 5005]
        
        # No nos preocupamos por PORT en este caso, usamos los puertos en la lista
        
        # Try to run with each port
        server_started = False
        for port in ports_to_try:
            try:
                logger.info(f"Intentando iniciar en puerto {port}...")
                app.run(host="0.0.0.0", port=port, debug=True)  # Activar modo debug para mostrar trazas
                server_started = True
                break  # Exit the loop if successful
            except OSError as e:
                logger.error(f"No se pudo iniciar en puerto {port}: {e}")
                continue  # Try the next port
        
        if not server_started:
            logger.critical("No se pudo iniciar el servidor en ningún puerto disponible.")
    except Exception as e:
        logger.critical(f"Error fatal al iniciar la aplicación: {str(e)}")
        logger.critical(traceback.format_exc())