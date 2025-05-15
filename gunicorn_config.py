import os
import multiprocessing

# Configuración de enlace y puerto
bind = f"0.0.0.0:{int(os.environ.get('PORT', 8080))}"

# Número de workers: 2-4 suele ser suficiente para entornos de Replit
workers = 2 
# Alternativa: usar un número basado en cores
# workers = multiprocessing.cpu_count() * 2 + 1

# Tiempo de espera máximo en segundos
timeout = 120

# Nivel de log
loglevel = 'info'

# Archivo de log
accesslog = 'gunicorn_access.log'
errorlog = 'gunicorn_error.log'

# Modo de captura de accesos
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Timeout para el worker
graceful_timeout = 10

# Para evitar reinicios en aplicaciones con muchos workers (en producción)
preload_app = True

# Cantidad máxima de peticiones simultaneas
worker_connections = 1000