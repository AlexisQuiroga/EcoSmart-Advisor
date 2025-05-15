import os
import logging
import traceback
from ecosmart_advisor.app import create_app
from flask import render_template

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ecosmart.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Crear la aplicación
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

if __name__ == "__main__":
    try:
        # Obtener puerto desde variables de entorno
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"Iniciando servidor en el puerto {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.critical(f"Error fatal al iniciar la aplicación: {str(e)}")
        logger.critical(traceback.format_exc())