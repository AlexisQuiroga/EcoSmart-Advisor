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
    
    # Registrar blueprints (rutas)
    from ecosmart_advisor.app.routes import main_bp, diagnostico_bp, simulador_bp, chatbot_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(diagnostico_bp)
    app.register_blueprint(simulador_bp)
    app.register_blueprint(chatbot_bp)
    
    return app