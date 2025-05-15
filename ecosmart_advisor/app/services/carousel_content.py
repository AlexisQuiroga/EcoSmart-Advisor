"""
Módulo para generar contenido relevante para el carrusel de la página principal
utilizando Deepseek AI para obtener información actualizada sobre energías renovables.
"""
import os
import random
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar la API de Deepseek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Categorías para el carrusel
CAROUSEL_CATEGORIES = [
    "energia_solar",
    "energia_eolica", 
    "termotanque_solar",
    "eficiencia_energetica",
    "futuro_renovables"
]

# Datos predeterminados para cada slide del carrusel
DEFAULT_CAROUSEL_DATA = {
    "energia_solar": {
        "titulo": "Energía Solar Fotovoltaica",
        "texto_principal": "Los paneles solares convierten la luz solar en electricidad limpia y renovable.",
        "dato_destacado": "Los paneles modernos tienen una vida útil de más de 25 años con mínimo mantenimiento.",
        "color": "primary"
    },
    "energia_eolica": {
        "titulo": "Energía Eólica",
        "texto_principal": "La energía eólica aprovecha la fuerza del viento para generar electricidad sin emisiones.",
        "dato_destacado": "Un solo aerogenerador puede abastecer a cientos de hogares con energía limpia.",
        "color": "success"
    },
    "termotanque_solar": {
        "titulo": "Termotanque Solar",
        "texto_principal": "Los termotanques solares calientan agua usando la radiación solar, sin consumir electricidad.",
        "dato_destacado": "Puede reducir hasta un 70% del consumo energético para calentar agua.",
        "color": "info"
    },
    "eficiencia_energetica": {
        "titulo": "Eficiencia Energética",
        "texto_principal": "Complementa tus sistemas renovables con prácticas eficientes para maximizar el ahorro.",
        "dato_destacado": "Combinar energías renovables con eficiencia puede reducir hasta un 90% tu factura.",
        "color": "warning"
    },
    "futuro_renovables": {
        "titulo": "El Futuro Renovable",
        "texto_principal": "Las energías renovables son la clave para un futuro sostenible y libre de emisiones.",
        "dato_destacado": "Se espera que para 2050, más del 85% de la electricidad mundial sea renovable.",
        "color": "danger"
    }
}

def generar_datos_carrusel():
    """
    Genera datos actualizados para el carrusel utilizando Deepseek AI
    o devuelve datos predeterminados si la IA no está disponible.
    
    Returns:
        dict: Datos actualizados para el carrusel
    """
    try:
        if not DEEPSEEK_API_KEY:
            print("API key de Deepseek no disponible, usando datos predeterminados")
            return DEFAULT_CAROUSEL_DATA
        
        # Seleccionar una categoría aleatoria para actualizar
        categoria = random.choice(CAROUSEL_CATEGORIES)
        
        # Generar datos actualizados para esa categoría
        datos_categoria = generar_datos_categoria(categoria)
        
        # Actualizar los datos del carrusel con la información nueva
        carousel_data = DEFAULT_CAROUSEL_DATA.copy()
        carousel_data[categoria] = datos_categoria
        
        return carousel_data
    
    except Exception as e:
        print(f"Error al generar datos del carrusel: {str(e)}")
        return DEFAULT_CAROUSEL_DATA

def generar_datos_categoria(categoria):
    """
    Genera datos actualizados para una categoría específica del carrusel
    utilizando Deepseek AI.
    
    Args:
        categoria (str): Categoría para la que generar datos (e.g., "energia_solar")
        
    Returns:
        dict: Datos actualizados para la categoría
    """
    # Tema específico basado en la categoría
    temas = {
        "energia_solar": "energía solar fotovoltaica",
        "energia_eolica": "energía eólica",
        "termotanque_solar": "calentadores solares de agua (termotanques solares)",
        "eficiencia_energetica": "eficiencia energética en hogares",
        "futuro_renovables": "futuro de las energías renovables y tendencias"
    }
    
    tema = temas.get(categoria, "energías renovables")
    
    # Construir prompt para la IA
    prompt = f"""
    Genera información actualizada y verificable sobre {tema} para un carrusel 
    informativo en una aplicación web de asesoramiento en energías renovables.
    Debe tener:
    
    1. Un título corto (5-7 palabras)
    2. Un texto principal informativo (25-35 palabras) con datos reales y actualizados
    3. Un dato destacado interesante (preferiblemente numérico) sobre ahorro, eficiencia o impacto ambiental
    
    Proporciona solo la información solicitada en formato JSON con las claves "titulo", "texto_principal", "dato_destacado".
    No incluyas comillas adicionales, explicaciones, introducciones ni otros elementos.
    La información debe ser completamente precisa, educativa y basada en datos actuales.
    """
    
    try:
        # Preparar payload para la API de Deepseek
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Eres un especialista en energías renovables que proporciona información precisa, actualizada y educativa en español."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        # Realizar la petición a la API
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=10)
        
        # Verificar la respuesta
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Parsear el JSON de la respuesta
            resultado = json.loads(content)
            
            # Asegurarse de que todas las claves necesarias están presentes
            required_keys = ["titulo", "texto_principal", "dato_destacado"]
            if all(key in resultado for key in required_keys):
                # Añadir el color del tema predeterminado
                resultado["color"] = DEFAULT_CAROUSEL_DATA[categoria]["color"]
                return resultado
        
        # Si algo falla, usar los datos predeterminados para esta categoría
        return DEFAULT_CAROUSEL_DATA[categoria]
    
    except Exception as e:
        print(f"Error al generar datos para la categoría {categoria}: {str(e)}")
        return DEFAULT_CAROUSEL_DATA[categoria]

# Función auxiliar para obtener todos los datos del carrusel para pruebas
def obtener_todos_datos_carrusel():
    """
    Genera datos para todas las categorías del carrusel. Útil para pruebas iniciales.
    
    Returns:
        dict: Datos completos para todas las categorías del carrusel
    """
    resultado = {}
    
    for categoria in CAROUSEL_CATEGORIES:
        try:
            datos = generar_datos_categoria(categoria)
            resultado[categoria] = datos
        except Exception as e:
            print(f"Error generando datos para {categoria}: {str(e)}")
            resultado[categoria] = DEFAULT_CAROUSEL_DATA[categoria]
    
    return resultado