"""
Script para iniciar el servidor EcoSmart Advisor a través de un workflow
"""
import os
import sys
import time
import subprocess
import requests

# Detener procesos existentes
try:
    subprocess.run("pkill -f 'gunicorn'", shell=True)
    print("Procesos gunicorn anteriores detenidos")
except:
    pass

try:
    subprocess.run("pkill -f 'python main.py'", shell=True)
    print("Procesos python anteriores detenidos")
except:
    pass

# Esperar a que se liberen los puertos
time.sleep(2)

# Iniciar servidor
print("Iniciando servidor EcoSmart Advisor...")
os.environ["PORT"] = "8080"

try:
    with open("server_output.log", "w") as log_file:
        server_process = subprocess.Popen(
            ["python", "main.py"],
            stdout=log_file,
            stderr=log_file,
            env=os.environ.copy()
        )
    
    print(f"Servidor iniciado con PID: {server_process.pid}")
    
    # Esperar a que el servidor esté disponible
    max_retries = 15
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8080/", timeout=1)
            if response.status_code == 200:
                print("Servidor disponible en http://localhost:8080/")
                break
        except:
            if i < max_retries - 1:
                print(f"Esperando a que el servidor esté disponible... ({i+1}/{max_retries})")
                time.sleep(1)
            else:
                print("El servidor no responde después del tiempo de espera. Verificar logs en server_output.log")
                with open("server_output.log", "r") as log_file:
                    print("\nÚltimas líneas del log del servidor:")
                    tail = log_file.readlines()[-20:]
                    for line in tail:
                        print(line.strip())
    
    # Mantener el script ejecutándose
    while True:
        # Comprobar si el proceso sigue vivo
        if server_process.poll() is not None:
            print(f"El servidor se detuvo inesperadamente con código: {server_process.returncode}")
            break
        time.sleep(5)

except KeyboardInterrupt:
    print("Deteniendo el servidor...")
    if 'server_process' in locals():
        server_process.terminate()
except Exception as e:
    print(f"Error al iniciar el servidor: {str(e)}")
    sys.exit(1)