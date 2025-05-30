#!/bin/bash
# Script para iniciar la aplicación EcoSmart Advisor

# Detener procesos existentes
echo "Deteniendo posibles procesos anteriores..."
pkill -f "python main.py" || true
pkill -f "gunicorn" || true

# Esperar a que se liberen los puertos
sleep 2

# Configurar puerto
export PORT=8080

# Iniciar la aplicación en modo debug para desarrollo
echo "Iniciando EcoSmart Advisor en modo debug en puerto $PORT..."
python main.py