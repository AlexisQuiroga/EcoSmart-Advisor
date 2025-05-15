#!/bin/bash
# Script para iniciar la aplicación EcoSmart Advisor en modo producción

# Detener procesos existentes
echo "Deteniendo posibles procesos anteriores..."
pkill -f "python main.py" || true
pkill -f "gunicorn" || true

# Esperar a que se liberen los puertos
sleep 2

# Configurar puerto
export PORT=8080

# Iniciar con gunicorn para entorno de producción
echo "Iniciando EcoSmart Advisor en modo producción en puerto $PORT..."
gunicorn --config gunicorn_config.py app:app