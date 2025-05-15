"""
Módulo de rutas para la aplicación EcoSmart Advisor
"""
import os
import json
import requests
from flask import Blueprint, render_template, request, jsonify, current_app, session
from ecosmart_advisor.app.services.clima_api import obtener_datos_clima
from ecosmart_advisor.app.services.energia_calculo import calcular_recomendacion, calcular_estimacion_sin_kwh
from ecosmart_advisor.app.services.simulador import simular_instalacion
from ecosmart_advisor.app.services.carousel_simple import generar_datos_carrusel as generar_datos_carrusel_simple
from ecosmart_advisor.app.services.carousel_content import generar_datos_carrusel as generar_datos_carrusel_content

import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ecosmart.log'
)

# Importar el chatbot original como fallback
from ecosmart_advisor.chatbot.chatbot import generar_respuesta_chatbot

# Variable global para usar chatbot con IA
USAR_IA_CHATBOT = False

# Definir una función alternativa para cuando no está disponible la IA
def generar_respuesta_ia_fallback(pregunta, historial_conversacion=None):
    """Función de fallback cuando no se puede importar el módulo IA"""
    texto = generar_respuesta_chatbot(pregunta)
    return {
        "respuesta": texto,
        "sugerencias": [
            "¿Qué sistema de energía renovable me conviene?",
            "¿Cuánto cuesta instalar paneles solares?",
            "¿Qué es un termotanque solar?"
        ]
    }

# Intentar importar el nuevo chatbot mejorado con IA
try:
    from ecosmart_advisor.chatbot.ai_chatbot import generar_respuesta_ia
    USAR_IA_CHATBOT = True
except ImportError:
    # Si falla la importación, usar la función de fallback
    generar_respuesta_ia = generar_respuesta_ia_fallback

# Blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ruta principal de la aplicación"""
    logger = logging.getLogger('index')
    
    # Generar datos actualizados para el carrusel utilizando carousel_content
    logger.info("Generando datos del carrusel para la página principal")
    
    # Verificar si tenemos la clave API de Unsplash configurada
    unsplash_key = os.environ.get("UNSPLASH_API_KEY")
    if unsplash_key:
        logger.info(f"UNSPLASH_API_KEY configurada (longitud: {len(unsplash_key)})")
    else:
        logger.warning("UNSPLASH_API_KEY no está configurada o está vacía")
    
    try:
        # Intentamos usar la versión de carousel_content que obtiene imágenes filtradas
        logger.info("Intentando generar datos con carousel_content...")
        carousel_data = generar_datos_carrusel_content()
        carousel_categories = list(carousel_data.keys())
        logger.info(f"Carrusel data obtenida correctamente: {carousel_categories}")
        
        # Verificar si tenemos alguna imagen de Unsplash o solo imágenes locales
        imagen_ejemplo = carousel_data[carousel_categories[0]].get('imagen_url', '')
        es_local = imagen_ejemplo.startswith('/static/')
        
        if es_local:
            logger.info("Usando imágenes locales (las imágenes remotas fallaron o no están disponibles)")
        else:
            logger.info("Usando imágenes filtradas de Unsplash sobre energías renovables")
            
    except Exception as e:
        logger.error(f"Error al generar datos con carousel_content: {str(e)}")
        
        # En caso de error, usamos la versión simple como fallback
        logger.info("Usando sistema de carrusel simple como fallback")
        carousel_data = generar_datos_carrusel_simple()
        carousel_categories = list(carousel_data.keys())
        logger.info(f"Carrusel simple data obtenida: {carousel_categories}")
    
    return render_template('index.html', carousel_data=carousel_data)

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
        
        # Agregar la descripción de la ubicación a los datos climáticos
        clima['descripcion_ubicacion'] = datos.get('descripcion_ubicacion', '')
        
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
        try:
            datos_simulacion = {
                'tipo_instalacion': request.form.get('tipo_instalacion'),
                'capacidad': request.form.get('capacidad'),
                'ubicacion': request.form.get('ubicacion'),
                'consumo_mensual': request.form.get('consumo_mensual'),
                'descripcion_ubicacion': request.form.get('descripcion_ubicacion', '')
            }
            
            # Validar campos mínimos necesarios
            campos_faltantes = []
            if not datos_simulacion['tipo_instalacion']:
                campos_faltantes.append('tipo_instalacion')
            if not datos_simulacion['ubicacion']:
                campos_faltantes.append('ubicacion')
                
            # Mostrar información de depuración
            print(f"Datos de simulación recibidos por POST: {datos_simulacion}")
            
            if campos_faltantes:
                return render_template('formulario_simulador.html', 
                                     error=f"Faltan campos requeridos: {', '.join(campos_faltantes)}")
            
            resultados = simular_instalacion(datos_simulacion)
            
            return render_template('resultado_simulacion.html', 
                                  resultados=resultados,
                                  datos=datos_simulacion)
        except Exception as e:
            print(f"Error en simulador: {str(e)}")
            return render_template('formulario_simulador.html', 
                                  error=f"Error al procesar la simulación: {str(e)}")
    
    # Si es GET, mostrar formulario del simulador
    return render_template('formulario_simulador.html')

@simulador_bp.route('/api', methods=['POST'])
def simulador_api():
    """API para el simulador (para uso con AJAX)"""
    try:
        datos = request.json
        if not datos:
            print("Error: Datos JSON vacíos o inválidos")
            return jsonify({"error": "Se requieren datos completos para la simulación"}), 400
            
        # Validar campos requeridos
        campos_requeridos = ['tipo_instalacion', 'capacidad', 'ubicacion', 'consumo_mensual']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos]
        
        if campos_faltantes:
            print(f"Error: Faltan campos requeridos: {campos_faltantes}")
            return jsonify({"error": f"Faltan campos requeridos: {', '.join(campos_faltantes)}"}), 400
            
        print(f"Recibidos datos para simulación API: {datos}")
        resultados = simular_instalacion(datos)
        print(f"Resultados de simulación: {resultados}")
        return jsonify(resultados)
    except Exception as e:
        print(f"Error en simulador API: {str(e)}")
        return jsonify({"error": f"Error en la simulación: {str(e)}"}), 500

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
            return jsonify({
                'respuesta': 'No se recibió ninguna pregunta. ¿En qué puedo ayudarte con las energías renovables?',
                'sugerencias': []
            })
        
        pregunta = request.json.get('pregunta', '')
        if not pregunta or pregunta.strip() == "":
            return jsonify({
                'respuesta': '¿En qué puedo ayudarte con las energías renovables?',
                'sugerencias': []
            })
        
        # Obtener historial de conversación de la sesión (si está disponible)
        historial = []
        if 'historial_chatbot' in session:
            historial = session['historial_chatbot']
        
        try:
            # Usamos la función generar_respuesta_ia en cualquier caso (puede ser la original o la fallback)
            resultado = generar_respuesta_ia(pregunta, historial)
            
            # Actualizar historial de conversación
            historial.append({"rol": "usuario", "contenido": pregunta})
            historial.append({"rol": "asistente", "contenido": resultado['respuesta']})
            
            # Limitar el historial a las últimas 10 interacciones (5 intercambios)
            historial = historial[-10:] if len(historial) > 10 else historial
            
            # Guardar historial en sesión
            session['historial_chatbot'] = historial
            
            return jsonify(resultado)
            
        except Exception as e:
            import logging
            logging.error(f"Error al procesar respuesta del chatbot: {str(e)}")
            
            # Respuesta de emergencia en caso de fallo total
            respuesta_texto = "Lo siento, pero estoy teniendo problemas para procesar tu pregunta. Por favor, intenta nuevamente con otra consulta relacionada con energías renovables."
            
            # Actualizar historial incluso con respuesta de emergencia
            historial.append({"rol": "usuario", "contenido": pregunta})
            historial.append({"rol": "asistente", "contenido": respuesta_texto})
            historial = historial[-10:] if len(historial) > 10 else historial
            session['historial_chatbot'] = historial
            
            # Sugerencias por defecto para emergencia
            sugerencias_default = [
                "¿Qué sistema de energía renovable me conviene?",
                "¿Cuánto cuesta instalar paneles solares?",
                "¿Qué es un termotanque solar?"
            ]
            
            return jsonify({
                'respuesta': respuesta_texto,
                'sugerencias': sugerencias_default
            })
        
    except Exception as e:
        import logging
        logging.error(f"Error al procesar consulta del chatbot: {str(e)}")
        return jsonify({
            'respuesta': 'Lo siento, pero estoy especializado en temas de energías renovables y en el uso de la plataforma EcoSmart Advisor. Por favor, reformula tu pregunta para que esté relacionada con estos temas.',
            'sugerencias': [
                "¿Qué sistema de energía renovable me conviene?",
                "¿Cuánto cuesta instalar paneles solares?",
                "¿Qué es un termotanque solar?"
            ]
        })