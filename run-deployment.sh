#!/bin/bash

# Script de inicio para despliegue en Replit
echo "Iniciando EcoSmart Advisor en modo producción..."

# Establecer variables de entorno
export FLASK_ENV=production
export FLASK_DEBUG=0

# Intentar primero con gunicorn
if command -v gunicorn &> /dev/null; then
    echo "Usando Gunicorn para ejecutar la aplicación..."
    if [ -f "gunicorn_config.py" ]; then
        gunicorn --config gunicorn_config.py app:app
    else
        gunicorn --bind 0.0.0.0:$PORT app:app
    fi
else
    # Si no está disponible gunicorn, usar python directamente
    echo "Usando Flask para ejecutar la aplicación..."
    python main.py
fi