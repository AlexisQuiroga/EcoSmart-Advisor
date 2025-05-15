"""
EcoSmart Advisor
Una aplicación inteligente que asesora a los usuarios sobre qué sistema 
de energía renovable les conviene instalar según su ubicación y condiciones.
"""
import os
import logging
from flask import Flask, render_template

from ecosmart_advisor.app import create_app

# Configurar logging para ver los mensajes relacionados con Unsplash API
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

# Verificar que las variables de entorno estén disponibles
if "UNSPLASH_API_KEY" in os.environ:
    logger.info("UNSPLASH_API_KEY está configurada correctamente")
else:
    logger.warning("UNSPLASH_API_KEY no está configurada")

if __name__ == "__main__":
    app = create_app()
    # Using 0.0.0.0 to make it accessible outside localhost
    # Try several ports, starting with 8080 which is often available in Replit
    ports_to_try = [8080, 8000, 5001, 5002, 5003, 5004, 5005]
    
    # No nos preocupamos por PORT en este caso, usamos los puertos en la lista
    
    # Try to run with each port
    server_started = False
    for port in ports_to_try:
        try:
            print(f"Intentando iniciar en puerto {port}...")
            app.run(host="0.0.0.0", port=port, debug=False)
            server_started = True
            break  # Exit the loop if successful
        except OSError as e:
            print(f"No se pudo iniciar en puerto {port}: {e}")
            continue  # Try the next port
    
    if not server_started:
        print("No se pudo iniciar el servidor en ningún puerto disponible.")