"""
Módulo de rutas para la aplicación EcoSmart Advisor
"""
import os
import requests
from flask import Blueprint, render_template, request, jsonify, current_app
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
            'latitud': request.form.get('latitud'),
            'longitud': request.form.get('longitud'),
            'tipo_vivienda': request.form.get('tipo_vivienda'),
            'consumo_mensual': request.form.get('consumo_mensual'),
            'superficie_disponible': request.form.get('superficie_disponible'),
            'objetivo': request.form.get('objetivo'),
            'equipos': request.form.getlist('equipos'),
            'descripcion_ubicacion': request.form.get('descripcion_ubicacion', '')
        }
        
        # Valor por defecto para los campos que ya no están en el formulario
        datos['provincia'] = 'No especificada'
        datos['ciudad'] = 'No especificada'
        datos['direccion'] = 'Seleccionada en mapa'
        
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

# Blueprint para las APIs
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/geocode', methods=['GET'])
def geocode():
    """API proxy para OpenCage Geocoder"""
    try:
        # Obtener la API key desde .env
        api_key = os.environ.get('OPENCAGE_API_KEY')
        
        # Si la API key no está disponible, intentamos cargarla explícitamente
        if not api_key:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get('OPENCAGE_API_KEY')
            
            if not api_key:
                return jsonify({
                    'error': 'API key no configurada',
                    'message': 'La API key de OpenCage no está disponible en el entorno'
                }), 500
        
        # Log para verificar la API key
        import logging
        logging.info(f"Usando API key de OpenCage: {api_key[:4]}...{api_key[-4:]}")
        
        # Obtener parámetros de búsqueda
        q = request.args.get('q', '')
        limit = request.args.get('limit', '5')
        
        if not q:
            return jsonify({'error': 'Parámetro de búsqueda requerido'}), 400
            
        # Preprocesar la consulta para optimizar resultados para Argentina
        if 'argentina' not in q.lower() and len(q.split(',')) > 1:
            q = f"{q}, Argentina"
        
        logging.info(f"Consulta a OpenCage: {q}")
            
        # Construir URL de la API
        url = 'https://api.opencagedata.com/geocode/v1/json'
        params = {
            'q': q,
            'key': api_key,
            'limit': limit,
            'countrycode': 'ar',  # Priorizar Argentina
            'language': 'es',     # Respuestas en español
            'no_annotations': 1   # Respuestas más ligeras
        }
        
        # Realizar la solicitud a OpenCage
        response = requests.get(url, params=params)
        data = response.json()
        
        # Verificar si hay errores
        if 'error' in data:
            logging.error(f"Error de OpenCage: {data['error']}")
            return jsonify({
                'error': 'Error en API de OpenCage',
                'message': data.get('error', {}).get('message', 'Error desconocido')
            }), 500
        
        # Log para ver la respuesta completa 
        logging.info(f"Respuesta de OpenCage: {len(data.get('results', []))} resultados")
        
        # Simplificar la respuesta para mejorar rendimiento
        results = []
        if 'results' in data:
            for result in data['results']:
                simplified = {
                    'formatted': result['formatted'],
                    'lat': result['geometry']['lat'],
                    'lng': result['geometry']['lng'],
                    'confidence': result.get('confidence', 0)
                }
                # Agregar componentes de dirección si están disponibles
                if 'components' in result:
                    comp = result['components']
                    simplified['components'] = {
                        'street': comp.get('road', ''),
                        'number': comp.get('house_number', ''),
                        'city': comp.get('city', comp.get('town', comp.get('village', ''))),
                        'state': comp.get('state', ''),
                        'country': comp.get('country', '')
                    }
                results.append(simplified)
                
        return jsonify({'results': results})
        
    except Exception as e:
        import logging
        logging.error(f"Error al procesar geocodificación con OpenCage: {str(e)}")
        # Incluir detalles del error para debugging
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Detalles: {error_details}")
        
        return jsonify({
            'error': 'Error al procesar la solicitud', 
            'message': str(e),
            'type': type(e).__name__
        }), 500

# Blueprint para el chatbot
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/', methods=['GET'])
def chatbot():
    """Redirige a la página principal donde está el chatbot flotante"""
    # Ya no mostramos una página separada para el chatbot
    from flask import redirect, url_for
    return redirect(url_for('main.index'))

@chatbot_bp.route('/consulta', methods=['POST'])
def consulta_chatbot():
    """Procesa consultas al chatbot"""
    try:
        if not request.json:
            return jsonify({'respuesta': 'No se recibió ninguna pregunta. ¿En qué puedo ayudarte con las energías renovables?'})
        
        pregunta = request.json.get('pregunta', '')
        if not pregunta or pregunta.strip() == "":
            return jsonify({'respuesta': '¿En qué puedo ayudarte con las energías renovables?'})
            
        respuesta = generar_respuesta_chatbot(pregunta)
        return jsonify({'respuesta': respuesta})
    except Exception as e:
        import logging
        logging.error(f"Error al procesar consulta del chatbot: {str(e)}")
        return jsonify({'respuesta': 'Lo siento, pero estoy especializado en temas de energías renovables y en el uso de la plataforma EcoSmart Advisor. Por favor, reformula tu pregunta para que esté relacionada con estos temas. Puedo ayudarte con información sobre paneles solares, energía eólica, termotanques solares, o cómo utilizar las diferentes herramientas de nuestra plataforma como el diagnóstico y el simulador.'})