#!/bin/bash
# Script maestro para ejecutar EcoSmart Advisor

# Definir colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Banner de inicio
echo -e "${GREEN}"
echo "====================================================="
echo "        EcoSmart Advisor - Sistema de Inicio         "
echo "====================================================="
echo -e "${NC}"

# Verificar dependencias del sistema
echo -e "${YELLOW}Verificando dependencias del sistema...${NC}"
python check_dependencies.py

# Comprobar si la verificación fue exitosa
if [ $? -ne 0 ]; then
  echo -e "${RED}Error: La verificación de dependencias falló. Revise el log para más detalles.${NC}"
  exit 1
fi

# Detener posibles procesos previos
echo -e "${YELLOW}Deteniendo posibles procesos previos...${NC}"
pkill -f "python main.py" || true
pkill -f "gunicorn" || true
sleep 2

# Determinar el modo de ejecución (desarrollo o producción)
if [ "$1" == "prod" ]; then
  echo -e "${GREEN}Iniciando EcoSmart Advisor en modo PRODUCCIÓN...${NC}"
  # Configurar puerto
  export PORT=8080
  # Iniciar con gunicorn para producción
  gunicorn --config gunicorn_config.py app:app
else
  echo -e "${GREEN}Iniciando EcoSmart Advisor en modo DESARROLLO...${NC}"
  # Configurar puerto
  export PORT=8080
  # Iniciar la aplicación en modo debug
  python main.py
fi