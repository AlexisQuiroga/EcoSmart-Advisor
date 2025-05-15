"""
Script para iniciar el servidor EcoSmart Advisor a través de un workflow
"""
import os
import sys
import time
import subprocess
import requests
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='start_server.log'
)
logger = logging.getLogger(__name__)

def detener_procesos_existentes():
    """Detiene cualquier proceso existente que pueda estar usando los puertos necesarios"""
    try:
        subprocess.run("pkill -f 'gunicorn'", shell=True)
        logger.info("Procesos gunicorn anteriores detenidos")
        print("Procesos gunicorn anteriores detenidos")
    except Exception as e:
        logger.warning(f"Error al detener procesos gunicorn: {str(e)}")
    
    try:
        subprocess.run("pkill -f 'python main.py'", shell=True)
        logger.info("Procesos python anteriores detenidos")
        print("Procesos python anteriores detenidos")
    except Exception as e:
        logger.warning(f"Error al detener procesos python: {str(e)}")
    
    # Esperar a que se liberen los puertos
    time.sleep(2)

def iniciar_servidor():
    """Inicia el servidor principal y lo monitorea"""
    # Variable para el proceso del servidor
    server_process = None
    
    try:
        # Detener procesos existentes
        detener_procesos_existentes()
        
        # Iniciar servidor
        logger.info("Iniciando servidor EcoSmart Advisor...")
        print("Iniciando servidor EcoSmart Advisor...")
        os.environ["PORT"] = "8080"
        
        with open("server_output.log", "w") as log_file:
            server_process = subprocess.Popen(
                ["python", "main.py"],
                stdout=log_file,
                stderr=log_file,
                env=os.environ.copy()
            )
        
        if server_process is None:
            logger.error("No se pudo iniciar el servidor")
            print("No se pudo iniciar el servidor")
            return
            
        logger.info(f"Servidor iniciado con PID: {server_process.pid}")
        print(f"Servidor iniciado con PID: {server_process.pid}")
        
        # Esperar a que el servidor esté disponible
        esperar_servidor_disponible()
        
        # Mantener el script ejecutándose
        while True:
            # Comprobar si el proceso sigue vivo
            if server_process.poll() is not None:
                logger.error(f"El servidor se detuvo inesperadamente con código: {server_process.returncode}")
                print(f"El servidor se detuvo inesperadamente con código: {server_process.returncode}")
                break
            time.sleep(5)
            
    except KeyboardInterrupt:
        logger.info("Deteniendo el servidor por interrupción del usuario...")
        print("Deteniendo el servidor...")
        if server_process is not None:
            server_process.terminate()
            logger.info("Servidor terminado correctamente.")
            print("Servidor terminado correctamente.")
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {str(e)}")
        print(f"Error al iniciar el servidor: {str(e)}")
        if server_process is not None:
            try:
                server_process.terminate()
                logger.info("Servidor terminado debido a error.")
                print("Servidor terminado debido a error.")
            except Exception as term_e:
                logger.error(f"Error al terminar el servidor: {str(term_e)}")
        sys.exit(1)

def esperar_servidor_disponible():
    """Espera a que el servidor esté disponible y responda a peticiones"""
    max_retries = 15
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8080/", timeout=1)
            if response.status_code == 200:
                logger.info("Servidor disponible en http://localhost:8080/")
                print("Servidor disponible en http://localhost:8080/")
                return True
        except Exception as e:
            if i < max_retries - 1:
                logger.info(f"Esperando a que el servidor esté disponible... ({i+1}/{max_retries})")
                print(f"Esperando a que el servidor esté disponible... ({i+1}/{max_retries})")
                time.sleep(1)
            else:
                logger.warning("El servidor no responde después del tiempo de espera. Verificar logs en server_output.log")
                print("El servidor no responde después del tiempo de espera. Verificar logs en server_output.log")
                with open("server_output.log", "r") as log_file:
                    tail_log = log_file.readlines()[-20:]
                    logger.info("\nÚltimas líneas del log del servidor:")
                    print("\nÚltimas líneas del log del servidor:")
                    for line in tail_log:
                        logger.info(line.strip())
                        print(line.strip())
                return False

if __name__ == "__main__":
    iniciar_servidor()