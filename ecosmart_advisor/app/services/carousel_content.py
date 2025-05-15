"""
Módulo para generar contenido aleatorio relevante para el carrusel de la página principal,
utilizando Deepseek AI para obtener información actualizada sobre energías renovables
e integrando una API de imágenes para mostrar contenido visual pertinente.
"""
import os
import random
import json
import requests
import hashlib
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar la API de Deepseek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Configurar API de imágenes (Unsplash)
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_API_KEY")  # Usar la clave de API de las variables de entorno
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Nota: Ya no usamos URLs predefinidas de Unsplash porque dependen de la API.
# En su lugar, usamos imágenes locales como fallback que están siempre disponibles.

# Caché para evitar generar el mismo contenido en cada solicitud
# Usaremos un tiempo de expiración para refrescar el contenido periódicamente
CONTENT_CACHE = {}  # Vaciar caché para forzar regeneración
CACHE_EXPIRY = 10  # Reducir temporalmente a 10 segundos para pruebas

# Temas predefinidos para las imágenes
IMAGE_TOPICS = {
    "energia_solar": "solar panels energy",
    "energia_eolica": "wind turbine energy", 
    "termotanque_solar": "solar water heater",
    "eficiencia_energetica": "energy efficiency home",
    "futuro_renovables": "renewable energy future",
    "energia_termica": "solar thermal energy system"
}

# Categorías para el carrusel
CAROUSEL_CATEGORIES = [
    "energia_solar",
    "energia_eolica", 
    "termotanque_solar",
    "eficiencia_energetica",
    "futuro_renovables",
    "energia_termica"
]

# Datos predeterminados para cada slide del carrusel con énfasis en los beneficios económicos y ambientales
DEFAULT_CAROUSEL_DATA = {
    "energia_solar": {
        "titulo": "Ahorro con Energía Solar",
        "texto_principal": "La inversión en paneles solares se recupera en un promedio de 4-6 años según la zona geográfica.",
        "dato_destacado": "Reduce hasta un 95% de tu factura eléctrica mensual generando tu propia energía limpia.",
        "color": "primary"
    },
    "energia_eolica": {
        "titulo": "Rentabilidad Eólica",
        "texto_principal": "La energía eólica tiene el menor costo de generación entre todas las renovables y continúa bajando.",
        "dato_destacado": "Un hogar con turbina pequeña puede ahorrar entre $200-600 USD mensuales en áreas con buen recurso.",
        "color": "success"
    },
    "termotanque_solar": {
        "titulo": "Beneficio Económico Inmediato",
        "texto_principal": "Los termotanques solares ofrecen el retorno de inversión más rápido entre todas las tecnologías renovables.",
        "dato_destacado": "Reduce hasta 85% el gasto en calentamiento de agua, con amortización en solo 2-3 años.",
        "color": "info"
    },
    "eficiencia_energetica": {
        "titulo": "Maximiza tu Inversión Verde",
        "texto_principal": "Cada peso invertido en eficiencia energética genera un retorno de hasta 3 veces la inversión inicial.",
        "dato_destacado": "Combinando renovables y eficiencia se puede lograr hasta 50% más ahorro que con renovables solas.",
        "color": "warning"
    },
    "futuro_renovables": {
        "titulo": "Independencia Energética",
        "texto_principal": "Las renovables ofrecen soberanía energética a hogares y empresas, protegiéndolos de aumentos de tarifas.",
        "dato_destacado": "Se prevé que para 2025 las renovables serán hasta 60% más baratas que los combustibles fósiles.",
        "color": "danger"
    },
    "energia_termica": {
        "titulo": "Valorización Inmobiliaria",
        "texto_principal": "Las propiedades con sistemas de energía renovable aumentan su valor de mercado entre un 4% y 8%.",
        "dato_destacado": "Los edificios con certificación energética se venden un 35% más rápido que propiedades similares.",
        "color": "primary"
    }
}

def buscar_imagen_unsplash(tema, categoria=None):
    """
    Busca imágenes en Unsplash relacionadas con energías renovables.
    Aplica un filtro específico para garantizar que sean sobre energías renovables.
    
    Args:
        tema (str): Tema de búsqueda específico para Unsplash
        categoria (str, optional): Categoría del tema (usado para fallback)
        
    Returns:
        str: URL de la imagen
    """
    # Mapeo de fallback con imágenes locales por si falla la API
    imagenes_fallback = {
        "energia_solar": "/static/images/carousel/energia_solar.jpg",
        "energia_eolica": "/static/images/carousel/energia_eolica.jpg",
        "termotanque_solar": "/static/images/carousel/termotanque_solar.jpg",
        "eficiencia_energetica": "/static/images/carousel/eficiencia_energetica.jpg",
        "futuro_renovables": "/static/images/carousel/futuro_renovable.jpg",
        "energia_termica": "/static/images/carousel/energia_termica.jpg"
    }
    
    # Filtros para asegurar que solo se muestren imágenes de energías renovables
    filtros_renovables = [
        "renewable energy",
        "clean energy",
        "green energy",
        "sustainable energy"
    ]
    
    # Si no hay API key o no hay tema, usar fallback
    if not UNSPLASH_ACCESS_KEY:
        print(f"No se encontró UNSPLASH_API_KEY en las variables de entorno")
        if categoria and categoria in imagenes_fallback:
            print(f"Sin API key - Usando imagen local para {categoria}")
            return imagenes_fallback[categoria]
        return "/static/images/carousel/energia_eolica.jpg"
    
    if not tema:
        print(f"No se proporcionó tema de búsqueda")
        if categoria and categoria in imagenes_fallback:
            print(f"Sin tema - Usando imagen local para {categoria}")
            return imagenes_fallback[categoria]
        return "/static/images/carousel/energia_eolica.jpg"
    
    # Verificar el formato de la API key (mostrar solo los primeros 5 caracteres por seguridad)
    if UNSPLASH_ACCESS_KEY:
        print(f"API key encontrada: {UNSPLASH_ACCESS_KEY[:5]}..." + "*" * 10)
    
    try:
        # Agregar un filtro aleatorio relacionado con energías renovables
        filtro = random.choice(filtros_renovables)
        tema_filtrado = f"{tema} {filtro}"
        
        print(f"Buscando imágenes de: {tema_filtrado}")
        
        # Parámetros para la API de Unsplash
        params = {
            "query": tema_filtrado,
            "per_page": 1,
            "orientation": "landscape",
            "content_filter": "high", 
            "client_id": UNSPLASH_ACCESS_KEY
        }
        
        # Realizar la petición a la API
        response = requests.get(UNSPLASH_API_URL, params=params, timeout=5)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Tomar la primera imagen del resultado
                imagen_url = data["results"][0]["urls"]["regular"]
                print(f"Imagen encontrada: {imagen_url}")
                return imagen_url
            else:
                print("No se encontraron imágenes en Unsplash")
        else:
            print(f"Error en la API de Unsplash: {response.status_code}")
    
    except Exception as e:
        print(f"Error al buscar imagen en Unsplash: {str(e)}")
    
    # En caso de error, usar imagen local como fallback
    if categoria and categoria in imagenes_fallback:
        print(f"Fallback - Usando imagen local para {categoria}")
        return imagenes_fallback[categoria]
    
    print("Usando imagen genérica de fallback")
    return "/static/images/carousel/energia_eolica.jpg"

def generar_datos_carrusel():
    """
    Genera datos para el carrusel con imágenes dinámicas de Unsplash filtradas 
    para asegurar que sean relacionadas con energías renovables.
    
    Returns:
        dict: Datos para el carrusel con URLs de imágenes
    """
    print("---- Generando datos para el carrusel con imágenes filtradas de energías renovables ----")
    
    try:
        # Crear datos dinámicos para cada categoría
        carousel_data = {}
        
        # Procesar cada categoría
        for categoria in CAROUSEL_CATEGORIES:
            # Intentar generar datos dinámicos de texto para esta categoría
            datos_categoria = generar_datos_categoria(categoria)
            
            # Si no se pudieron generar datos, usar los predeterminados
            if not datos_categoria:
                datos_categoria = DEFAULT_CAROUSEL_DATA[categoria].copy()
            
            # Obtener el tema específico para la búsqueda de imágenes
            tema_imagen = IMAGE_TOPICS.get(categoria)
            
            # Buscar una imagen con el filtro de energías renovables aplicado
            imagen_url = buscar_imagen_unsplash(tema_imagen, categoria)
            
            # Añadir la URL de la imagen
            datos_categoria["imagen_url"] = imagen_url
            
            # Asegurar que tenga color
            if "color" not in datos_categoria:
                colores = ["primary", "success", "info", "warning", "danger"]
                datos_categoria["color"] = random.choice(colores)
            
            # Agregar los datos a la colección principal
            carousel_data[categoria] = datos_categoria
            
        return carousel_data
    
    except Exception as e:
        print(f"Error al generar datos del carrusel: {str(e)}")
        # En caso de error, devolver datos mínimos con imágenes locales
        datos_minimos = DEFAULT_CAROUSEL_DATA.copy()
        for categoria in CAROUSEL_CATEGORIES:
            datos_minimos[categoria]['imagen_url'] = f"/static/images/carousel/{categoria}.jpg" if categoria != "futuro_renovables" else "/static/images/carousel/futuro_renovable.jpg"
        return datos_minimos

def generar_datos_categoria(categoria):
    """
    Genera datos aleatorios para una categoría específica del carrusel
    utilizando Deepseek AI o fuentes de datos alternativas.
    
    Args:
        categoria (str): Categoría para la que generar datos (e.g., "energia_solar")
        
    Returns:
        dict: Datos actualizados para la categoría, incluyendo imagen
    """
    # Tema específico basado en la categoría
    temas = {
        "energia_solar": "energía solar fotovoltaica",
        "energia_eolica": "energía eólica",
        "termotanque_solar": "calentadores solares de agua (termotanques solares)",
        "eficiencia_energetica": "eficiencia energética en hogares",
        "futuro_renovables": "futuro de las energías renovables y tendencias",
        "energia_termica": "sistemas de energía solar térmica"
    }
    
    tema = temas.get(categoria, "energías renovables")
    
    # Crear un factor de aleatoriedad para que cada vez se solicite un enfoque ligeramente diferente
    enfoques = [
        "impacto ambiental",
        "beneficios económicos",
        "avances tecnológicos recientes",
        "adopción global",
        "aplicaciones prácticas",
        "impacto en la reducción de CO2",
        "tendencias futuras",
        "casos de éxito",
        "eficiencia energética",
        "autonomía energética"
    ]
    
    # Seleccionar un enfoque aleatorio para el prompt
    enfoque = random.choice(enfoques)
    
    # Hacer que cada prompt sea ligeramente diferente para obtener variedad de respuestas
    prompt = f"""
    Genera información actualizada y verificable sobre {tema} con énfasis en {enfoque} 
    para un carrusel informativo en una aplicación web de asesoramiento en energías renovables.
    Debe tener exactamente:
    
    1. Un título corto e impactante (5-7 palabras)
    2. Un texto principal informativo (25-35 palabras) con datos reales y actualizados de 2024-2025
    3. Un dato destacado interesante (preferiblemente numérico) sobre ahorro, eficiencia o impacto ambiental
    
    Proporciona solo la información solicitada en formato JSON con las claves "titulo", "texto_principal", "dato_destacado".
    No incluyas comillas adicionales, explicaciones, introducciones ni otros elementos.
    La información debe ser completamente precisa, educativa y basada en datos actuales o proyecciones.
    Asegúrate de que el contenido sea sorprendente y no obvio.
    """
    
    try:
        # Intentar usar Deepseek para generar contenido
        if DEEPSEEK_API_KEY:
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
                "temperature": 0.8,  # Ligeramente más alto para mayor variedad
                "response_format": {"type": "json_object"}
            }
            
            # Realizar la petición a la API
            response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=10)
            
            # Verificar la respuesta
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parsear el JSON de la respuesta
                try:
                    resultado = json.loads(content)
                    
                    # Verificar que todas las claves necesarias están presentes
                    required_keys = ["titulo", "texto_principal", "dato_destacado"]
                    if all(key in resultado for key in required_keys):
                        # Añadir el color del tema predeterminado o uno aleatorio
                        colores = ['primary', 'secondary', 'success', 'danger', 'warning', 'info']
                        resultado["color"] = random.choice(colores)
                        
                        # Añadir campo para la URL de la imagen (se completará después)
                        resultado["imagen_url"] = ""  # String vacío en lugar de None
                        
                        return resultado
                except Exception as e:
                    print(f"Error al procesar respuesta de Deepseek: {str(e)}")
        
        # Si no se pudo generar con Deepseek, usar datos alternativos aleatorios
        # Banco de datos predefinidos por categoría
        datos_alternativos = {
            "energia_solar": [
                {
                    "titulo": "Revolución Fotovoltaica 2025",
                    "texto_principal": "Las nuevas células solares de perovskita alcanzan eficiencias del 29% en condiciones reales y costos 40% menores que los paneles tradicionales.",
                    "dato_destacado": "Un sistema de 5kW puede evitar la emisión de más de 4 toneladas de CO2 anualmente, equivalente a plantar 200 árboles."
                },
                {
                    "titulo": "Solar Bifacial: Doble Generación",
                    "texto_principal": "Los paneles bifaciales aprovechan la luz reflejada en su cara posterior, aumentando la producción entre 10-30% sin ocupar más espacio.",
                    "dato_destacado": "El retorno de inversión de un sistema residencial solar ha disminuido a solo 4-6 años en zonas con buena radiación."
                },
                {
                    "titulo": "Autonomía Solar Total",
                    "texto_principal": "La integración de paneles solares con baterías de estado sólido permite alcanzar independencia energética del 95% en hogares eficientes.",
                    "dato_destacado": "El precio de los sistemas de almacenamiento ha caído un 85% en la última década, haciendo viable la autosuficiencia."
                }
            ],
            "energia_eolica": [
                {
                    "titulo": "Aerogeneradores Urbanos Silenciosos",
                    "texto_principal": "Los micro-aerogeneradores de eje vertical revolucionan la energía urbana con niveles de ruido por debajo de 35dB y funcionamiento con brisas ligeras.",
                    "dato_destacado": "Un aerogenerador doméstico puede producir hasta 400kWh/mes en zonas con velocidad media de viento de 5.5 m/s."
                },
                {
                    "titulo": "Turbinas Flotantes Sin Límites",
                    "texto_principal": "Los parques eólicos flotantes instalados en aguas profundas están transformando el potencial eólico global con capacidad de captar vientos 60% más fuertes.",
                    "dato_destacado": "La energía eólica offshore puede generar 18 veces más energía que su equivalente terrestre en la misma superficie."
                },
                {
                    "titulo": "Viento: Energía 24/7",
                    "texto_principal": "Las nuevas turbinas híbridas integran almacenamiento hidráulico comprimido, permitiendo suministro constante incluso en períodos sin viento.",
                    "dato_destacado": "La energía eólica crea 1,5 veces más empleos por unidad de electricidad generada que las plantas de combustibles fósiles."
                }
            ],
            "termotanque_solar": [
                {
                    "titulo": "Agua Caliente 100% Solar",
                    "texto_principal": "Los termotanques solares de última generación logran eficiencias térmicas superiores al 92% incluso en días parcialmente nublados gracias a los tubos de vacío mejorados.",
                    "dato_destacado": "Un termotanque solar para una familia de 4 personas puede ahorrar hasta 4.500 kWh anuales, equivalente a €900 en factura energética."
                },
                {
                    "titulo": "Inteligencia Solar Térmica",
                    "texto_principal": "Los nuevos sistemas combinan sensores IoT con aprendizaje automático para optimizar la captación solar, aumentando la eficiencia hasta un 35% respecto a modelos convencionales.",
                    "dato_destacado": "El 70% de la energía doméstica destinada a calentar agua puede ser generada con energía solar térmica en casi cualquier clima."
                },
                {
                    "titulo": "Calor Solar Garantizado",
                    "texto_principal": "Los termotanques solares híbridos integran respaldo eléctrico inteligente que se activa solo cuando es necesario, asegurando disponibilidad continua con mínimo consumo.",
                    "dato_destacado": "La vida útil promedio de un termotanque solar de calidad supera los 25 años, con retorno de inversión en solo 3-5 años."
                }
            ],
            "eficiencia_energetica": [
                {
                    "titulo": "Hogares Inteligentes Ahorran 60%",
                    "texto_principal": "La combinación de sensores IoT, termostatos inteligentes y sistemas de gestión energética logra reducir el consumo doméstico hasta un 60% sin sacrificar confort.",
                    "dato_destacado": "Por cada euro invertido en eficiencia energética, se obtiene un retorno de 3€ en ahorro a lo largo de la vida útil de las soluciones."
                },
                {
                    "titulo": "Aislamiento Revolucionario 2025",
                    "texto_principal": "Los nuevos materiales aerogel ultraligeros ofrecen aislamiento 3 veces superior al convencional con solo 1/3 del grosor, permitiendo rehabilitaciones energéticas sin perder espacio habitable.",
                    "dato_destacado": "Mejorar el aislamiento puede reducir las necesidades de calefacción y refrigeración hasta en un 70%, disminuyendo drásticamente la huella de carbono."
                },
                {
                    "titulo": "Iluminación Zero-Energy",
                    "texto_principal": "Las nuevas luminarias LED autónomas integran microcélulas solares y sensores de presencia, eliminando por completo el consumo eléctrico en iluminación durante el día.",
                    "dato_destacado": "La iluminación representa aproximadamente el 15% del consumo eléctrico en hogares y hasta el 40% en oficinas, con potencial de ahorro del 90% con tecnología avanzada."
                }
            ],
            "futuro_renovables": [
                {
                    "titulo": "Renovables 2030: 80% Global",
                    "texto_principal": "Proyecciones actualizadas indican que las energías renovables alcanzarán el 80% de la generación global en 2030, superando todas las previsiones anteriores gracias a la aceleración tecnológica.",
                    "dato_destacado": "El costo de generación renovable ha caído un 90% en la última década, siendo ya más económico que cualquier fuente fósil en el 95% del mundo."
                },
                {
                    "titulo": "Energía Espacial Inminente",
                    "texto_principal": "La primera central solar espacial de 500MW iniciará operaciones en 2026, transmitiendo energía continuamente mediante microondas a receptores terrestres sin importar condiciones climáticas.",
                    "dato_destacado": "Una central solar en órbita puede generar energía 24/7 con eficiencia 5 veces superior a sus equivalentes terrestres al no tener atmósfera ni ciclo día-noche."
                },
                {
                    "titulo": "Comunidades Energéticas: Revolución",
                    "texto_principal": "El modelo de comunidades energéticas con blockchain integrado está transformando el mercado eléctrico, permitiendo intercambios P2P sin intermediarios con ahorros del 40%.",
                    "dato_destacado": "Para 2030, se proyecta que el 60% de los hogares europeos participarán en alguna forma de comunidad energética local."
                }
            ]
        }
        
        # Si la categoría no tiene datos alternativos, usar los predeterminados
        if categoria not in datos_alternativos:
            resultado = DEFAULT_CAROUSEL_DATA[categoria].copy()
        else:
            # Seleccionar una entrada aleatoria del banco de datos
            resultado = random.choice(datos_alternativos[categoria]).copy()
            # Mantener el color predeterminado
            resultado["color"] = DEFAULT_CAROUSEL_DATA[categoria]["color"]
            # Añadir campo para URL de imagen
            resultado["imagen_url"] = ""  # String vacío en lugar de None
        
        return resultado
        
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