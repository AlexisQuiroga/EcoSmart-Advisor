"""
Script para iniciar la aplicación EcoSmart Advisor en un puerto de prueba
"""
import os
from ecosmart_advisor.app import create_app

if __name__ == "__main__":
    # Crear la instancia de la aplicación
    app = create_app()
    
    # Usar un puerto diferente para no conflictos
    port = int(os.environ.get("PORT", 5001))
    
    # Ejecutar aplicación
    app.run(host="0.0.0.0", port=port, debug=True)