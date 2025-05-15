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

# Rutas simples para el simulador sin Blueprint
# para evitar problemas de redirección

@main_bp.route('/simulador', methods=['GET', 'POST'])
def simulador():
    """
    Ruta para el simulador de energía renovable
    Permite al usuario jugar con distintas variables
    """
    import traceback
    import logging
    logger = logging.getLogger('simulador')
    logger.setLevel(logging.DEBUG)
    
    if request.method == 'POST':
        try:
            # Registrar información detallada
            logger.info("=== INICIO PROCESAMIENTO DE SIMULACIÓN ===")
            logger.info(f"Request method: {request.method}, Form data: {request.form}")
            
            # Añadir debug info
            form_debug = request.form.get('form_debug', '')
            if form_debug:
                logger.info(f"Formulario verificado: {form_debug}")
            
            # Obtener los datos del formulario
            tipo_instalacion = request.form.get('tipo_instalacion')
            capacidad = request.form.get('capacidad')
            latitud = request.form.get('latitud')
            longitud = request.form.get('longitud')
            
            # Crear la ubicación a partir de las coordenadas
            ubicacion = None
            if latitud and longitud:
                ubicacion = f"{latitud},{longitud}"
                logger.info(f"Ubicación construida a partir de coordenadas: {ubicacion}")
            else:
                ubicacion = request.form.get('ubicacion')
                logger.info(f"Usando campo de ubicación directamente: {ubicacion}")
            
            # Crear el diccionario de datos para la simulación
            datos_simulacion = {
                'tipo_instalacion': tipo_instalacion,
                'capacidad': capacidad,
                'ubicacion': ubicacion,
                'consumo_mensual': request.form.get('consumo_mensual'),
                'precio_kwh': request.form.get('precio_kwh', '0.15'),
                'presupuesto': request.form.get('presupuesto', ''),
                'descripcion_ubicacion': request.form.get('descripcion_ubicacion', ''),
                'latitud': latitud,
                'longitud': longitud
            }
            
            logger.info(f"Datos recibidos del formulario: {datos_simulacion}")
            
            # Validar campos mínimos necesarios
            campos_faltantes = []
            if not datos_simulacion['tipo_instalacion']:
                campos_faltantes.append('tipo_instalacion')
            if not datos_simulacion['ubicacion']:
                campos_faltantes.append('ubicacion')
            
            if campos_faltantes:
                logger.warning(f"Faltan campos requeridos: {campos_faltantes}")
                logger.warning(f"Redirigiendo a formulario por campos faltantes: {campos_faltantes}")
                error_msg = f"Faltan campos requeridos: {', '.join(campos_faltantes)}"
                return render_template('formulario_simulador.html', error=error_msg)
            
            # Aplicar valores predeterminados si no se proporcionan
            if not datos_simulacion['consumo_mensual']:
                datos_simulacion['consumo_mensual'] = '300'
                logger.info("Aplicando consumo mensual predeterminado: 300 kWh")
            
            # Validar datos numéricos
            try:
                if datos_simulacion['capacidad']:
                    capacidad = float(datos_simulacion['capacidad'])
                    if capacidad <= 0:
                        logger.warning(f"Capacidad inválida: {capacidad}")
                        return render_template('formulario_simulador.html', 
                                             error=f"La capacidad debe ser un número positivo.")
            except ValueError:
                logger.warning(f"Error al convertir capacidad: {datos_simulacion['capacidad']}")
                return render_template('formulario_simulador.html', 
                                     error=f"La capacidad debe ser un número válido.")
                                     
            try:
                if datos_simulacion['consumo_mensual']:
                    consumo = float(datos_simulacion['consumo_mensual'])
                    if consumo <= 0:
                        logger.warning(f"Consumo inválido: {consumo}")
                        return render_template('formulario_simulador.html', 
                                             error=f"El consumo mensual debe ser un número positivo.")
            except ValueError:
                logger.warning(f"Error al convertir consumo: {datos_simulacion['consumo_mensual']}")
                return render_template('formulario_simulador.html', 
                                     error=f"El consumo mensual debe ser un número válido.")
            
            logger.info("Llamando a simular_instalacion...")
            resultados = simular_instalacion(datos_simulacion)
            
            if not resultados:
                logger.error("La función simular_instalacion devolvió resultados vacíos o nulos")
                return render_template('formulario_simulador.html', 
                                     error="Error al procesar la simulación: no se obtuvieron resultados")
            
            logger.info(f"Resultados obtenidos (tipo: {type(resultados)}): {str(resultados)[:200]}...")
            
            # Verificamos que resultados sea un diccionario con los datos esperados
            if not isinstance(resultados, dict) or 'tipo' not in resultados:
                logger.error(f"Resultados incompletos o de tipo incorrecto: {type(resultados)}")
                return render_template('formulario_simulador.html', 
                                     error="Error al procesar la simulación: resultados incompletos")
            
            logger.info("=== FIN PROCESAMIENTO DE SIMULACIÓN ===")
            logger.info("Redirigiendo a la página de resultados de simulación")
            
            # Guardar datos importantes en la sesión en caso de error
            session['ultimo_resultado'] = {
                'tipo': resultados.get('tipo', ''),
                'capacidad_kw': resultados.get('capacidad_kw', 0),
                'generacion_mensual': resultados.get('generacion_mensual', 0)
            }
            
            # Finalmente, renderizamos la página de resultados
            logger.info(f"Enviando resultados a template, datos:{len(str(datos_simulacion))} bytes, resultados:{len(str(resultados))} bytes")
            return render_template('resultado_simulacion.html', 
                                  resultados=resultados,
                                  datos=datos_simulacion)
        except Exception as e:
            logger.error(f"Error en simulador: {str(e)}")
            logger.error(traceback.format_exc())
            return render_template('formulario_simulador.html', 
                                  error=f"Error al procesar la simulación: {str(e)}")
    
    # Si es GET, mostrar formulario del simulador
    return render_template('formulario_simulador.html')

@main_bp.route('/simulador/api', methods=['POST'])
def simulador_api():
    """API para el simulador (para uso con AJAX)"""
    import logging
    logger = logging.getLogger('simulador_api')
    logger.setLevel(logging.DEBUG)
    
    try:
        # Intentar obtener datos JSON, con manejo de errores mejorado
        try:
            datos = request.json
            if datos is None:
                # Intentar obtener datos de formulario si no hay JSON
                logger.warning("No se recibieron datos JSON válidos, intentando obtener datos de formulario")
                datos = {
                    'tipo_instalacion': request.form.get('tipo_instalacion', 'solar'),
                    'capacidad': request.form.get('capacidad', '1'),
                    'ubicacion': request.form.get('ubicacion', '-34.61,-58.38'),
                    'consumo_mensual': request.form.get('consumo_mensual', '300'),
                    'descripcion_ubicacion': request.form.get('descripcion_ubicacion', 'Buenos Aires, Argentina')
                }
        except Exception as e:
            logger.error(f"Error al procesar datos de entrada: {str(e)}")
            datos = {}
        
        logger.info(f"Recibidos datos para simulación API: {datos}")
        
        # Verificar datos mínimos necesarios
        if not datos:
            logger.error("No se recibieron datos para la simulación")
            return jsonify({"error": "No se recibieron datos para la simulación"}), 400
            
        # Validar campos requeridos pero con valores por defecto si faltan
        campos_requeridos = ['tipo_instalacion', 'capacidad', 'ubicacion', 'consumo_mensual']
        valores_defecto = {
            'tipo_instalacion': 'solar',
            'capacidad': '1',
            'ubicacion': '-34.61,-58.38',
            'consumo_mensual': '300'
        }
        
        # Completar valores faltantes con valores por defecto
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                logger.warning(f"Campo requerido faltante: {campo}, usando valor por defecto")
                datos[campo] = valores_defecto[campo]
            
        # Ejecutar simulación con manejo robusto de errores
        logger.info("Ejecutando simulación...")
        resultados = simular_instalacion(datos)
        
        # Verificar si hay error en resultados
        if isinstance(resultados, dict) and 'error' in resultados:
            logger.error(f"Error en simulación: {resultados['error']}")
            return jsonify(resultados), 400
            
        logger.info(f"Simulación completada con éxito: {len(str(resultados))} bytes de resultados")
        return jsonify(resultados)
        
    except Exception as e:
        import traceback
        logger.error(f"Error general en simulador API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Error en la simulación: {str(e)}",
            "tipo": "error_general"
        }), 500

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