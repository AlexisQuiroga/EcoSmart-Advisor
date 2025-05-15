"""
Script para verificar que todas las dependencias necesarias estén instaladas
"""
import importlib
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Lista de dependencias requeridas
# Mapeo de nombres de paquetes a nombres de módulos (cuando difieren)
REQUIRED_PACKAGES = [
    'flask',
    'dotenv',  # El paquete se llama python-dotenv pero el módulo es dotenv
    'requests',
    'gunicorn',
    'openai',
    'deepseek_ai',  # El guión se convierte en guión bajo
]

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas correctamente"""
    logger.info("Verificando dependencias requeridas...")
    
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package.replace('-', '_'))
            logger.info(f"✅ {package} - Instalado correctamente")
        except ImportError:
            logger.error(f"❌ {package} - No instalado o no accesible")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Faltan {len(missing_packages)} dependencias: {', '.join(missing_packages)}")
        logger.error("Instale los paquetes faltantes con: pip install " + " ".join(missing_packages))
        return False
    else:
        logger.info("✅ Todas las dependencias están instaladas correctamente")
        return True

def check_environment_vars():
    """Verifica que las variables de entorno esenciales estén configuradas"""
    import os
    from dotenv import load_dotenv
    
    # Cargar variables de entorno
    load_dotenv()
    
    logger.info("Verificando variables de entorno...")
    
    # Variables opcionales pero recomendadas
    env_vars = {
        'DEEPSEEK_API_KEY': False,  # False = opcional
        'UNSPLASH_API_KEY': False,
    }
    
    missing_vars = []
    
    for var, required in env_vars.items():
        value = os.environ.get(var)
        if value:
            logger.info(f"✅ {var} - Configurado correctamente")
        elif required:
            logger.error(f"❌ {var} - REQUERIDO pero no configurado")
            missing_vars.append(var)
        else:
            logger.warning(f"⚠️ {var} - No configurado (opcional)")
    
    if any(missing_vars):
        logger.error(f"Faltan {len(missing_vars)} variables de entorno requeridas: {', '.join(missing_vars)}")
        logger.error("Configure las variables faltantes en el archivo .env")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("Iniciando verificación del entorno EcoSmart Advisor...")
    
    deps_ok = check_dependencies()
    env_ok = check_environment_vars()
    
    if deps_ok and env_ok:
        logger.info("✅ Sistema listo para ejecutar EcoSmart Advisor")
        sys.exit(0)
    else:
        logger.error("❌ Se encontraron problemas en la configuración")
        sys.exit(1)