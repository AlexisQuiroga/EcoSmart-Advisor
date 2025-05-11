#!/bin/bash

# Script para iniciar EcoSmart Advisor en modo producción
# Asegura que la aplicación se inicie correctamente tanto en desarrollo como en despliegue

# Configuración de la aplicación para producción
export FLASK_ENV=production
export FLASK_APP=ecosmart_advisor.app

# Obtener el puerto de Replit o usar 5000 por defecto
PORT=${PORT:-5000}

# Iniciar la aplicación
python -c "import os; os.environ['PORT'] = '$PORT'; from ecosmart_advisor.app import create_app; app = create_app(); app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)"