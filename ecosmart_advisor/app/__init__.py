"""
Módulo de inicialización de la aplicación Flask
"""
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    """
    Función para crear y configurar la instancia de la aplicación Flask
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configuración secreta de la aplicación
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')
    
    # Desactivar caché de plantillas (para desarrollo)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Registrar blueprints (rutas)
    from ecosmart_advisor.app.routes import main_bp, diagnostico_bp, chatbot_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(diagnostico_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(api_bp)
    
    # Simulador movido a main_bp para evitar problemas con las redirecciones
    
    return app