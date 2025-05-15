"""
Módulo para recomendaciones de energía renovable utilizando Deepseek AI.
Este módulo se encarga de consultar modelos de IA para obtener recomendaciones
más precisas y personalizadas sobre sistemas de energía renovable.
"""
import os
import json
import requests
import logging
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Cargar variables de entorno
load_dotenv()

# Configurar la API de Deepseek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

logger.info("Inicializando módulo de recomendaciones con IA")

def evaluar_factores_energia_renovable(datos_usuario, clima):
    """
    Utiliza Deepseek AI para evaluar factores relevantes para la selección de 
    energía renovable y ajustar los cálculos basándose en datos reales.
    
    Args:
        datos_usuario (dict): Datos proporcionados por el usuario
        clima (dict): Datos climáticos de la ubicación
        
    Returns:
        dict: Factores ajustados y recomendaciones para cada tipo de energía
    """
    try:
        # Preparar información para la consulta
        prompt = construir_prompt_evaluacion(datos_usuario, clima)
        
        # Preparar payload para la API de Deepseek
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Eres un experto en energía renovable y climatolología. Tu tarea es analizar los datos proporcionados y generar recomendaciones precisas sobre sistemas de energía renovable basadas en ubicación, clima y condiciones específicas. Debes responder en formato JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "top_p": 0.95,
            "max_tokens": 2000
        }
        
        # Realizar la petición a la API
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        
        # Verificar la respuesta
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Buscar la sección de JSON en la respuesta (en caso de que venga con formato adicional)
            start_index = content.find('{')
            end_index = content.rfind('}') + 1
            
            if start_index >= 0 and end_index > start_index:
                json_content = content[start_index:end_index]
                resultado = json.loads(json_content)
                return resultado
            else:
                # Si no podemos encontrar JSON válido, devolver un mensaje de error
                logger.error("Error al procesar la respuesta de Deepseek: No se encontró JSON válido")
                return generar_respuesta_fallback()
        else:
            logger.error(f"Error en la petición a Deepseek: {response.status_code} - {response.text}")
            return generar_respuesta_fallback()
        
    except Exception as e:
        logger.error(f"Error al procesar la recomendación con Deepseek: {str(e)}")
        return generar_respuesta_fallback()

def construir_prompt_evaluacion(datos_usuario, clima):
    """
    Construye un prompt detallado para consultar a Deepseek AI.
    
    Args:
        datos_usuario (dict): Datos proporcionados por el usuario
        clima (dict): Datos climáticos de la ubicación
        
    Returns:
        str: Prompt estructurado para la consulta
    """
    # Extraer datos relevantes
    ubicacion = clima.get('ubicacion', 'Desconocida')
    latitud = clima.get('latitud', 0)
    longitud = clima.get('longitud', 0)
    radiacion_solar = clima.get('radiacion_solar', 0)
    velocidad_viento = clima.get('velocidad_viento', 0)
    temperatura = clima.get('temperatura_promedio', 0)
    
    # Datos del usuario
    superficie = datos_usuario.get('superficie_disponible', 0)
    consumo_mensual = datos_usuario.get('consumo_mensual', 0)
    tipo_vivienda = datos_usuario.get('tipo_vivienda', 'desconocido')
    objetivo = datos_usuario.get('objetivo', 'ahorro')
    descripcion_ubicacion = datos_usuario.get('descripcion_ubicacion', ubicacion)
    
    # Construir el prompt
    prompt = f"""
    Analiza los siguientes datos para recomendar el mejor sistema de energía renovable:
    
    UBICACIÓN Y CLIMA:
    - Ubicación: {descripcion_ubicacion}
    - Coordenadas: {latitud}, {longitud}
    - Radiación solar: {radiacion_solar} kWh/m²/día
    - Velocidad del viento: {velocidad_viento} m/s
    - Temperatura promedio: {temperatura} °C
    
    DATOS DEL USUARIO:
    - Tipo de vivienda: {tipo_vivienda}
    - Superficie disponible: {superficie} m²
    - Consumo mensual: {consumo_mensual} kWh
    - Objetivo principal: {objetivo}
    
    Basándote en estos datos, determina:
    1. Factores óptimos para cada tipo de energía (solar fotovoltaica, eólica, termotanque solar)
    2. Cuál es la mejor opción o combinación de opciones
    3. Los valores recomendados para: eficiencia del sistema, inclinación de paneles, orientación ideal y altura de torre (si aplica)
    4. Porcentaje de cobertura energética estimada para cada opción
    5. Una justificación técnica breve para cada recomendación
    
    REGLAS IMPORTANTES:
    - Debes considerar las condiciones climáticas específicas de la ubicación para todas las evaluaciones
    - La respuesta debe incluir valores numéricos específicos para todos los parámetros
    - Cada cálculo debe tener una justificación basada en los datos proporcionados
    - Para energía solar, considera radiación, temperatura y ubicación
    - Para energía eólica, considera velocidad del viento, rugosidad del terreno estimada por ubicación
    - Para termotanque solar, considera radiación y temperatura
    
    Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
    {{
        "mejor_opcion": "solar|eolica|termotanque_solar|combinacion",
        "justificacion": "Explicación concisa de la recomendación principal",
        "opciones": {{
            "solar": {{
                "viable": true|false,
                "eficiencia_sistema": 85,
                "inclinacion_paneles": 30,
                "orientacion": "Norte|Sur|Este|Oeste",
                "cobertura_estimada": 65,
                "justificacion": "Explicación técnica"
            }},
            "eolica": {{
                "viable": true|false,
                "altura_torre": 15,
                "potencia_recomendada": 2.5,
                "cobertura_estimada": 40,
                "justificacion": "Explicación técnica"
            }},
            "termotanque_solar": {{
                "viable": true|false,
                "eficiencia_sistema": 70,
                "inclinacion_optima": 35,
                "cobertura_estimada": 25,
                "justificacion": "Explicación técnica"
            }}
        }},
        "combinacion_recomendada": {{
            "opciones": ["solar", "termotanque_solar"],
            "cobertura_combinada": 85,
            "justificacion": "Explicación técnica"
        }}
    }}
    """
    
    return prompt

def generar_respuesta_fallback():
    """
    Genera una respuesta de fallback cuando hay un error en la consulta a Deepseek.
    
    Returns:
        dict: Respuesta predeterminada con valores conservadores
    """
    return {
        "mejor_opcion": "solar",
        "justificacion": "Recomendación generada con valores por defecto debido a un error en la consulta a la IA.",
        "opciones": {
            "solar": {
                "viable": True,
                "eficiencia_sistema": 75,
                "inclinacion_paneles": 30,
                "orientacion": "Norte",
                "cobertura_estimada": 60,
                "justificacion": "La energía solar es generalmente viable en la mayoría de las ubicaciones."
            },
            "eolica": {
                "viable": False,
                "altura_torre": 15,
                "potencia_recomendada": 2.0,
                "cobertura_estimada": 30,
                "justificacion": "La generación eólica requiere velocidades de viento sostenidas superiores a 4 m/s para ser eficiente."
            },
            "termotanque_solar": {
                "viable": True,
                "eficiencia_sistema": 65,
                "inclinacion_optima": 35,
                "cobertura_estimada": 20,
                "justificacion": "Los termotanques solares pueden complementar otros sistemas de energía renovable."
            }
        },
        "combinacion_recomendada": {
            "opciones": ["solar", "termotanque_solar"],
            "cobertura_combinada": 70,
            "justificacion": "La combinación de energía solar con termotanque solar suele ser complementaria para necesidades eléctricas y de agua caliente."
        }
    }