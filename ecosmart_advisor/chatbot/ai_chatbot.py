"""
Módulo para el chatbot educativo de energías renovables con Deepseek AI.
Genera respuestas más naturales y contextualizadas usando IA, con
sistema de reglas como fallback.
"""
import os
import json
import requests
import logging
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Importar el chatbot original para usar como fallback
from .chatbot import generar_respuesta_chatbot as respuesta_fallback

# Cargar variables de entorno
load_dotenv()

# Configurar la API de Deepseek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

logger.info("Inicializando chatbot educativo con IA")

def generar_respuesta_ia(pregunta, historial_conversacion=None):
    """
    Genera una respuesta usando Deepseek AI para preguntas sobre energía renovable.
    
    Args:
        pregunta (str): Pregunta del usuario
        historial_conversacion (list, optional): Historial de la conversación
        
    Returns:
        dict: Respuesta con texto y sugerencias de preguntas
    """
    # Validar que la pregunta no sea None
    if pregunta is None:
        return {
            "respuesta": "Por favor, ingresa una pregunta sobre energías renovables para que pueda ayudarte.",
            "sugerencias": []
        }
    
    # Si no hay historial, inicializarlo
    if historial_conversacion is None:
        historial_conversacion = []
    
    try:
        # Construir el prompt para Deepseek
        prompt = construir_prompt(pregunta, historial_conversacion)
        
        # Preparar payload para la API de Deepseek
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        # Construir los mensajes incluyendo el historial
        messages = [
            {
                "role": "system", 
                "content": (
                    "Eres un asistente virtual especializado en energías renovables para EcoSmart Advisor. "
                    "Tu objetivo es educar a los usuarios sobre energías renovables (solar, eólica, termotanque solar) "
                    "y guiarlos en el uso de la plataforma. "
                    "Responde en español de manera concisa, precisa y educativa. "
                    "Incluye datos técnicos relevantes pero presentados de forma accesible. "
                    "Tus respuestas no deben exceder los 200 palabras. "
                    "Si te preguntan sobre precios, da rangos aproximados actualizados. "
                    "Sugiere usar las herramientas de diagnóstico y simulación de la plataforma "
                    "cuando sea apropiado. Mantén un tono amigable y profesional. "
                    "Enfócate solo en responder la pregunta sin agregar información innecesaria."
                )
            }
        ]
        
        # Añadir el historial de conversación
        for mensaje in historial_conversacion[-6:]:  # Incluir sólo los últimos 6 mensajes
            messages.append({
                "role": "user" if mensaje["rol"] == "usuario" else "assistant",
                "content": mensaje["contenido"]
            })
        
        # Añadir la pregunta actual
        messages.append({"role": "user", "content": pregunta})
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 500
        }
        
        # Realizar la petición a la API
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=10)
        
        # Verificar la respuesta
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Generar sugerencias de preguntas relacionadas
            sugerencias = generar_sugerencias_preguntas(pregunta, content)
            
            return {
                "respuesta": content,
                "sugerencias": sugerencias
            }
        else:
            logger.error(f"Error en la petición a Deepseek: {response.status_code} - {response.text}")
            # Usar el sistema de fallback
            return {
                "respuesta": respuesta_fallback(pregunta),
                "sugerencias": generar_sugerencias_preguntas(pregunta)
            }
        
    except Exception as e:
        logger.error(f"Error al procesar la respuesta con Deepseek: {str(e)}")
        # Usar el sistema de fallback
        return {
            "respuesta": respuesta_fallback(pregunta),
            "sugerencias": generar_sugerencias_preguntas(pregunta)
        }

def construir_prompt(pregunta, historial):
    """
    Construye un prompt detallado para la consulta a Deepseek AI.
    
    Args:
        pregunta (str): Pregunta del usuario
        historial (list): Historial de la conversación
        
    Returns:
        str: Prompt para la consulta
    """
    # El prompt ya está incorporado en el mensaje del sistema
    return pregunta

def generar_sugerencias_preguntas(pregunta, respuesta=None):
    """
    Genera sugerencias de preguntas relacionadas basadas en la pregunta y respuesta.
    
    Args:
        pregunta (str): Pregunta del usuario
        respuesta (str, optional): Respuesta generada
        
    Returns:
        list: Lista de preguntas sugeridas
    """
    # Sugerencias básicas predeterminadas
    sugerencias_default = [
        "¿Cuánto cuesta instalar paneles solares?",
        "¿Qué sistema de energía renovable me conviene?",
        "¿Cómo funciona el termotanque solar?",
        "¿Cuál es el retorno de inversión de la energía solar?",
        "¿Qué mantenimiento requieren los sistemas eólicos?"
    ]
    
    try:
        # Si tenemos una respuesta de la IA, usarla para generar sugerencias más relevantes
        if respuesta and DEEPSEEK_API_KEY:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
            
            # Crear un prompt específico para generar sugerencias
            sugerencias_prompt = (
                f"Basándote en esta pregunta del usuario: '{pregunta}' "
                f"y en tu respuesta: '{respuesta[:200]}...', "
                f"genera exactamente 3 preguntas de seguimiento relacionadas que el usuario podría querer hacer a continuación. "
                f"Las preguntas deben ser cortas (máximo 10 palabras cada una), específicas y directamente relacionadas con energías renovables. "
                f"Responde SOLAMENTE con las 3 preguntas en formato JSON como array: [\"pregunta 1\", \"pregunta 2\", \"pregunta 3\"] "
                f"sin texto adicional, explicaciones o comillas adicionales."
            )
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Eres un asistente que genera preguntas de seguimiento concisas sobre energías renovables."},
                    {"role": "user", "content": sugerencias_prompt}
                ],
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 200,
                "response_format": {"type": "json_object"}
            }
            
            # Realizar la petición a la API
            response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=5)
            
            # Verificar la respuesta
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Intentar extraer el JSON
                try:
                    # Buscar el array JSON en la respuesta
                    start_index = content.find('[')
                    end_index = content.rfind(']') + 1
                    
                    if start_index >= 0 and end_index > start_index:
                        json_content = content[start_index:end_index]
                        sugerencias = json.loads(json_content)
                        
                        # Verificar que sean al menos 3 sugerencias
                        if isinstance(sugerencias, list) and len(sugerencias) >= 3:
                            return sugerencias[:3]  # Limitar a 3 sugerencias
                except Exception as e:
                    logger.error(f"Error al procesar sugerencias: {str(e)}")
        
        # Si no pudimos generar sugerencias personalizadas, usar las predeterminadas
        return sugerencias_default[:3]
        
    except Exception as e:
        logger.error(f"Error al generar sugerencias: {str(e)}")
        return sugerencias_default[:3]