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
UNSPLASH_ACCESS_KEY = "qPLQJ_PnZYDNjrKzQl49uJxWIhTwR0WczNHSvs55U-4"  # Clave demo para desarrollo
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# URL de imágenes predefinidas por tema (como alternativa si la API falla)
IMAGENES_PREDEFINIDAS = {
    "energia_solar": [
        "https://images.unsplash.com/photo-1559302995-f54c122559b9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    ],
    "energia_eolica": [
        "https://images.unsplash.com/photo-1548337138-e87d889cc369?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1467533003447-e295ff1b0435?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    ],
    "termotanque_solar": [
        "https://images.unsplash.com/photo-1525558134239-d9d9e7a59a75?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1584276433291-76b422994066?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    ],
    "eficiencia_energetica": [
        "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1515269048104-99a0a0a82652?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    ],
    "futuro_renovables": [
        "https://images.unsplash.com/photo-1590272456521-1bbe160a18ce?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    ],
    "energia_termica": [
        "https://images.unsplash.com/photo-1553434006-dc322885d7d6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1469048071019-6ac1aa26c008?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    ]
}

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
    },
    "energia_termica": {
        "titulo": "Energía Solar Térmica",
        "texto_principal": "Los sistemas solares térmicos aprovechan el calor del sol para distintas aplicaciones energéticas.",
        "dato_destacado": "Por cada m² de captador solar térmico se evita la emisión de una tonelada de CO2 al año.",
        "color": "primary"
    }
}

def buscar_imagen_unsplash(tema, categoria=None):
    """
    Busca una imagen relacionada con el tema en Unsplash o devuelve una predefinida.
    
    Args:
        tema (str): Tema de búsqueda (ej: 'solar panels')
        categoria (str, optional): Categoría del tema para usar imágenes predefinidas
        
    Returns:
        str: URL de la imagen
    """
    print(f"Buscando imagen para tema: {tema}, categoría: {categoria}")
    try:
        # Crear un hash del tema + timestamp redondeado (para cambiar cada cierto tiempo)
        # Esto permite obtener diferentes imágenes en cada carga, pero no en cada solicitud
        seed = f"{tema}_{int(time.time() / (60 * 10))}"  # Cambia cada 10 minutos
        hash_obj = hashlib.md5(seed.encode())
        seed_hash = int(hash_obj.hexdigest(), 16) % 100  # Valor entre 0-99
        
        # Intentar usar la API de Unsplash
        # Parámetros de búsqueda
        params = {
            'query': tema,
            'orientation': 'landscape',
            'per_page': 30,        # Traer varias opciones para seleccionar aleatoriamente
            'content_filter': 'high',
            'client_id': UNSPLASH_ACCESS_KEY
        }
        
        try:
            response = requests.get(UNSPLASH_API_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    # Usar el hash para seleccionar una imagen específica para este periodo de tiempo
                    # Así obtenemos variedad pero estabilidad durante un periodo
                    index = seed_hash % len(results)
                    selected_image = results[index]
                    
                    # Obtener URL de la imagen en resolución media (mejor para carrusel)
                    return selected_image['urls']['regular']
        except Exception as api_error:
            print(f"Error en la API de Unsplash: {str(api_error)}")
        
        # Si falla la API, usar imágenes predefinidas si tenemos la categoría
        if categoria and categoria in IMAGENES_PREDEFINIDAS:
            # Seleccionar imagen predefinida usando el mismo hash para consistencia
            imagenes = IMAGENES_PREDEFINIDAS[categoria]
            if imagenes:
                index = seed_hash % len(imagenes)
                imagen_seleccionada = imagenes[index]
                print(f"Usando imagen predefinida para {categoria}: {imagen_seleccionada[:30]}...")
                return imagen_seleccionada
        
        # Si no tenemos imágenes predefinidas para esta categoría, intentar buscar en otros temas
        print(f"No se encontraron imágenes para categoría {categoria}, usando imágenes de otra categoría")
        for cat, urls in IMAGENES_PREDEFINIDAS.items():
            if urls:
                index = seed_hash % len(urls)
                imagen_seleccionada = urls[index]
                print(f"Usando imagen de categoría alternativa {cat}: {imagen_seleccionada[:30]}...")
                return imagen_seleccionada
                
        # Si todo falla, devolver string vacío (no None para evitar problemas de tipo)
        return ""
    
    except Exception as e:
        print(f"Error al buscar imagen en Unsplash: {str(e)}")
        return ""

def generar_datos_carrusel():
    """
    Genera datos aleatorios y actualizados para el carrusel utilizando Deepseek AI
    y busca imágenes relevantes para cada tema.
    
    Returns:
        dict: Datos actualizados para el carrusel con URLs de imágenes
    """
    print("---- Generando nuevos datos para el carrusel ----")
    try:
        # Crear un identificador único basado en la hora (actualizado cada 10 segundos para pruebas)
        cache_key = int(time.time() / CACHE_EXPIRY)
        
        # Si tenemos datos en caché y no han expirado, usarlos
        if cache_key in CONTENT_CACHE:
            return CONTENT_CACHE[cache_key]
        
        # Seleccionar categorías aleatorias para actualizar (al menos 3)
        num_categorias = random.randint(3, 5)
        categorias_seleccionadas = random.sample(CAROUSEL_CATEGORIES, num_categorias)
        
        # Generar datos actualizados para el carrusel
        carousel_data = DEFAULT_CAROUSEL_DATA.copy()
        
        # Añadir campo de imagen a todos los elementos
        for categoria in CAROUSEL_CATEGORIES:
            carousel_data[categoria]['imagen_url'] = ""  # String vacío en lugar de None
        
        # Actualizar solo las categorías seleccionadas con contenido nuevo
        for categoria in categorias_seleccionadas:
            # No actualizar si Deepseek no está disponible
            if not DEEPSEEK_API_KEY and categoria != categorias_seleccionadas[0]:
                continue
                
            # Generar datos actualizados para esta categoría
            datos_categoria = generar_datos_categoria(categoria)
            carousel_data[categoria] = datos_categoria
            
            # Buscar una imagen relevante para la categoría
            tema_imagen = IMAGE_TOPICS.get(categoria)
            if tema_imagen:
                imagen_url = buscar_imagen_unsplash(tema_imagen, categoria)
                carousel_data[categoria]['imagen_url'] = imagen_url
        
        # Guardar en caché
        CONTENT_CACHE[cache_key] = carousel_data
        
        return carousel_data
    
    except Exception as e:
        print(f"Error al generar datos del carrusel: {str(e)}")
        return DEFAULT_CAROUSEL_DATA

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