"""
Módulo de rutas para la aplicación EcoSmart Advisor
"""
from flask import Blueprint, render_template, request, jsonify
from ecosmart_advisor.app.services.clima_api import obtener_datos_clima
from ecosmart_advisor.app.services.energia_calculo import calcular_recomendacion, calcular_estimacion_sin_kwh
from ecosmart_advisor.app.services.simulador import simular_instalacion
from ecosmart_advisor.chatbot.chatbot import generar_respuesta_chatbot

# Blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ruta principal de la aplicación"""
    return render_template('index.html')

# Blueprint para el diagnóstico
diagnostico_bp = Blueprint('diagnostico', __name__, url_prefix='/diagnostico')

@diagnostico_bp.route('/', methods=['GET', 'POST'])
def diagnostico():
    """
    Ruta para el diagnóstico de energía renovable.
    GET: Muestra el formulario
    POST: Procesa los datos y muestra recomendaciones
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        datos = {
            'ubicacion': request.form.get('ubicacion'),
            'tipo_vivienda': request.form.get('tipo_vivienda'),
            'consumo_mensual': request.form.get('consumo_mensual'),
            'superficie_disponible': request.form.get('superficie_disponible'),
            'objetivo': request.form.get('objetivo'),
            'equipos': request.form.getlist('equipos')
        }
        
        # Si no proporcionó consumo en kWh, estimarlo
        if not datos['consumo_mensual'] or datos['consumo_mensual'] == '0':
            datos['consumo_mensual'] = calcular_estimacion_sin_kwh(
                datos['tipo_vivienda'],
                datos['equipos']
            )
        
        # Obtener datos climáticos
        clima = obtener_datos_clima(datos['ubicacion'])
        
        # Calcular recomendación
        recomendacion = calcular_recomendacion(datos, clima)
        
        return render_template('resultado_diagnostico.html', 
                              recomendacion=recomendacion,
                              datos=datos,
                              clima=clima)
    
    # Si es GET, mostrar formulario
    return render_template('formulario_diagnostico.html')

@diagnostico_bp.route('/api', methods=['POST'])
def diagnostico_api():
    """API para el diagnóstico (para uso con AJAX)"""
    datos = request.json
    if not datos or 'ubicacion' not in datos:
        return jsonify({"error": "Se requiere ubicación para el diagnóstico"}), 400
    
    clima = obtener_datos_clima(datos['ubicacion'])
    recomendacion = calcular_recomendacion(datos, clima)
    return jsonify(recomendacion)

# Blueprint para el simulador
simulador_bp = Blueprint('simulador', __name__, url_prefix='/simulador')

@simulador_bp.route('/', methods=['GET', 'POST'])
def simulador():
    """
    Ruta para el simulador de energía renovable
    Permite al usuario jugar con distintas variables
    """
    if request.method == 'POST':
        datos_simulacion = {
            'tipo_instalacion': request.form.get('tipo_instalacion'),
            'capacidad': request.form.get('capacidad'),
            'ubicacion': request.form.get('ubicacion'),
            'consumo_mensual': request.form.get('consumo_mensual')
        }
        
        resultados = simular_instalacion(datos_simulacion)
        
        return render_template('resultado_simulacion.html', 
                              resultados=resultados,
                              datos=datos_simulacion)
    
    # Si es GET, mostrar formulario del simulador
    return render_template('formulario_simulador.html')

@simulador_bp.route('/api', methods=['POST'])
def simulador_api():
    """API para el simulador (para uso con AJAX)"""
    datos = request.json
    resultados = simular_instalacion(datos)
    return jsonify(resultados)

# Blueprint para el chatbot
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/', methods=['GET'])
def chatbot():
    """Muestra la interfaz del chatbot"""
    return render_template('chatbot.html')

@chatbot_bp.route('/consulta', methods=['POST'])
def consulta_chatbot():
    """Procesa consultas al chatbot"""
    if not request.json:
        return jsonify({'respuesta': 'No se recibió ninguna pregunta. ¿En qué puedo ayudarte con las energías renovables?'})
    
    pregunta = request.json.get('pregunta', '')
    respuesta = generar_respuesta_chatbot(pregunta)
    return jsonify({'respuesta': respuesta})