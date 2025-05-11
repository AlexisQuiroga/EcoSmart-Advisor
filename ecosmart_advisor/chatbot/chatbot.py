"""
Módulo para el chatbot educativo de energías renovables
basado en un sistema de reglas para responder preguntas de usuarios.
No requiere APIs externas de IA.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Base de conocimiento para respuestas sin IA
CONOCIMIENTO_BASE = {
    "paneles solares": (
        "Los paneles solares fotovoltaicos convierten la luz solar en electricidad. "
        "Su rendimiento depende de la radiación solar de tu ubicación, la orientación "
        "e inclinación de la instalación, y el tipo de panel. Una instalación doméstica "
        "típica puede generar entre 3-8 kWh diarios por kW instalado."
    ),
    "energía eólica": (
        "Los aerogeneradores convierten la energía cinética del viento en electricidad. "
        "Para instalaciones domésticas, se necesita una velocidad promedio mínima de "
        "3-4 m/s para que sean viables. Son complementarios a la energía solar, ya que "
        "pueden generar energía durante la noche o en días nublados."
    ),
    "termotanque solar": (
        "Los termotanques solares utilizan la radiación solar para calentar agua, "
        "reduciendo el consumo de gas o electricidad. Son simples y efectivos, con capacidades "
        "típicas entre 150-300 litros, suficientes para una familia de 3-6 personas. Pueden "
        "ahorrar hasta un 80% en el consumo energético para calentamiento de agua."
    ),
    "baterías": (
        "Las baterías permiten almacenar la energía generada durante el día para usarla "
        "durante la noche o en momentos de mayor demanda. Existen distintos tipos como las de "
        "plomo-ácido (más económicas) o las de litio (más eficientes y durables). Su capacidad "
        "se mide en kWh y su vida útil en ciclos de carga-descarga."
    ),
    "retorno inversión": (
        "El tiempo de retorno de inversión (payback) para sistemas renovables varía según "
        "la tecnología, ubicación y costo de la energía convencional. En general, los sistemas "
        "solares tienen un retorno de 4-8 años, los termotanques solares de 2-5 años, y los "
        "sistemas eólicos de 5-10 años. Después de ese período, la energía generada es prácticamente gratuita."
    ),
    "mantenimiento": (
        "Los sistemas de energía renovable requieren poco mantenimiento. Los paneles solares "
        "necesitan limpieza ocasional y revisión de conexiones, los aerogeneradores requieren "
        "mantenimiento mecánico periódico, y los termotanques solares necesitan verificación "
        "anual del fluido caloportador y limpieza de colectores."
    ),
    "incentivos": (
        "Muchos países ofrecen incentivos para instalaciones de energía renovable, como "
        "deducciones fiscales, subsidios, financiamiento preferencial o programas de medición "
        "neta (net metering) que permiten vender el excedente a la red eléctrica. Consulta "
        "con tu proveedor local o instituciones gubernamentales sobre los programas disponibles."
    ),
    "instalación": (
        "La instalación debe ser realizada por profesionales certificados para garantizar "
        "seguridad y eficiencia. El proceso incluye evaluación del sitio, diseño del sistema, "
        "obtención de permisos, instalación del equipo y conexión a la red o sistema eléctrico "
        "existente. El tiempo de instalación varía de 1-3 días para sistemas simples hasta 1-2 "
        "semanas para sistemas más complejos."
    ),
    "ahorro": (
        "El ahorro depende del tipo y tamaño del sistema, tu consumo energético y las tarifas "
        "locales. Un sistema solar típico puede reducir tu factura eléctrica entre 50-90%. "
        "Un termotanque solar puede reducir el costo de calentar agua en 70-80%. Estos ahorros "
        "aumentan a medida que suben los precios de la energía convencional."
    ),
    "impacto ambiental": (
        "Las energías renovables reducen significativamente la huella de carbono. Un sistema "
        "solar doméstico típico puede evitar la emisión de 1-4 toneladas de CO2 anualmente, "
        "equivalente a plantar 50-200 árboles. Además, reducen la contaminación del aire y "
        "agua asociada con los combustibles fósiles y disminuyen la dependencia energética."
    )
}

def generar_respuesta_chatbot(pregunta):
    """
    Genera una respuesta educativa a preguntas sobre energía renovable
    usando un sistema basado en coincidencia de palabras clave y reglas.
    También devuelve sugerencias de preguntas relacionadas.
    
    Args:
        pregunta (str): Pregunta del usuario
        
    Returns:
        str: Respuesta educativa
    """
    # Validar que la pregunta no sea None
    if pregunta is None:
        return "Por favor, ingresa una pregunta sobre energías renovables para que pueda ayudarte."
    
    # Limpiar y preparar la pregunta
    pregunta_limpia = pregunta.lower().strip()
    
    # Creamos un sistema de puntuación para seleccionar la mejor respuesta
    mejores_coincidencias = {}
    
    # Verificar primero en la base de conocimiento para palabras clave exactas
    for palabra_clave, respuesta in CONOCIMIENTO_BASE.items():
        if palabra_clave == pregunta_limpia:  # Coincidencia exacta
            return respuesta
        elif palabra_clave in pregunta_limpia:  # Palabras clave en la pregunta
            palabras_clave = palabra_clave.split()
            palabras_pregunta = pregunta_limpia.split()
            # Calcular un puntaje basado en la proporción de palabras que coinciden
            proporcion = len(palabras_clave) / len(palabras_pregunta) if palabras_pregunta else 0
            mejores_coincidencias[palabra_clave] = proporcion * 0.8  # 80% de confianza si contiene la palabra clave
    
    # Buscar coincidencias en palabras relacionadas
    palabras_pregunta = pregunta_limpia.split()
    palabras_relacionadas_puntuacion = {}
    
    for palabra in palabras_pregunta:
        for termino_relacionado, tema in get_palabras_relacionadas().items():
            if palabra == termino_relacionado:  # Coincidencia exacta con un término relacionado
                if tema in mejores_coincidencias:
                    mejores_coincidencias[tema] += 0.6  # Aumentar la puntuación si ya existe
                else:
                    mejores_coincidencias[tema] = 0.6  # 60% de confianza
            elif termino_relacionado in palabra:  # El término relacionado es parte de la palabra
                if tema in mejores_coincidencias:
                    mejores_coincidencias[tema] += 0.3  # Aumentar la puntuación
                else:
                    mejores_coincidencias[tema] = 0.3  # 30% de confianza
    
    # Determinar la mejor coincidencia
    mejor_tema = None
    mejor_puntuacion = 0.4  # Umbral mínimo para considerar una coincidencia como relevante
    
    for tema, puntuacion in mejores_coincidencias.items():
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_tema = tema
    
    # Si encontramos una buena coincidencia, devolver la respuesta correspondiente
    if mejor_tema:
        return CONOCIMIENTO_BASE[mejor_tema]
    
    # Verificar casos especiales
    respuesta_especial = verificar_casos_especiales(pregunta_limpia)
    if respuesta_especial:
        return respuesta_especial
    
    # Si no hay coincidencias suficientemente buenas, generar una respuesta genérica
    return respuesta_generica(pregunta_limpia)

def get_palabras_relacionadas():
    """
    Devuelve un diccionario de palabras relacionadas con los temas de la base de conocimiento
    
    Returns:
        dict: Diccionario de palabras relacionadas a términos en la base de conocimiento
    """
    # Mapeo de palabras relacionadas a términos en la base de conocimiento
    return {
        # Solar
        "fotovoltaica": "paneles solares",
        "fotovoltaico": "paneles solares",
        "placa": "paneles solares",
        "placas": "paneles solares",
        "panel": "paneles solares",
        "solar": "paneles solares",
        "sol": "paneles solares",
        "techo": "paneles solares",
        
        # Eólico
        "aerogenerador": "energía eólica",
        "turbina": "energía eólica",
        "viento": "energía eólica",
        "molino": "energía eólica",
        "eolica": "energía eólica",
        "eolico": "energía eólica",
        
        # Termotanque
        "calentador": "termotanque solar",
        "termotanque": "termotanque solar",
        "agua caliente": "termotanque solar",
        "calefon": "termotanque solar",
        "termica": "termotanque solar",
        "termico": "termotanque solar",
        
        # Baterías
        "bateria": "baterías",
        "acumulador": "baterías",
        "almacenamiento": "baterías",
        "almacenar": "baterías",
        "litio": "baterías",
        "powerwall": "baterías",
        
        # Retorno de inversión
        "inversion": "retorno inversión",
        "recuperar": "retorno inversión",
        "amortizar": "retorno inversión",
        "roi": "retorno inversión",
        "rentabilidad": "retorno inversión",
        "rentable": "retorno inversión",
        "pagar": "retorno inversión",
        "cuanto tarda": "retorno inversión",
        "años": "retorno inversión",
        
        # Mantenimiento
        "mantenimiento": "mantenimiento",
        "limpiar": "mantenimiento",
        "limpieza": "mantenimiento",
        "duración": "mantenimiento",
        "dura": "mantenimiento",
        "vida util": "mantenimiento",
        "reparar": "mantenimiento",
        "cuidados": "mantenimiento",
        
        # Incentivos
        "incentivo": "incentivos",
        "subsidio": "incentivos",
        "fiscal": "incentivos",
        "impuesto": "incentivos",
        "descuento": "incentivos",
        "financiamiento": "incentivos",
        "credito": "incentivos",
        "prestamo": "incentivos",
        "ayuda": "incentivos",
        
        # Instalación
        "instalar": "instalación",
        "montar": "instalación",
        "colocar": "instalación",
        "implementar": "instalación",
        "instalacion": "instalación",
        "proceso": "instalación",
        "requisitos": "instalación",
        
        # Ahorro
        "ahorro": "ahorro",
        "ahorrar": "ahorro",
        "factura": "ahorro",
        "consumo": "ahorro",
        "economizar": "ahorro",
        "reducir": "ahorro",
        "reduccion": "ahorro",
        "bajar": "ahorro",
        "euro": "ahorro",
        "dinero": "ahorro",
        
        # Impacto ambiental
        "ambiental": "impacto ambiental",
        "huella": "impacto ambiental",
        "carbono": "impacto ambiental",
        "co2": "impacto ambiental",
        "contaminacion": "impacto ambiental",
        "contaminar": "impacto ambiental",
        "medioambiente": "impacto ambiental",
        "ambiente": "impacto ambiental",
        "ecologia": "impacto ambiental",
        "ecologico": "impacto ambiental",
        "planeta": "impacto ambiental"
    }

def verificar_casos_especiales(pregunta):
    """
    Verifica casos especiales o preguntas compuestas que requieren respuestas más específicas
    
    Args:
        pregunta (str): Pregunta limpia del usuario
        
    Returns:
        str: Respuesta específica o None si no aplica
    """
    # Preguntas sobre comparación y recomendaciones
    if any(palabra in pregunta for palabra in ["mejor", "recomendable", "recomiendas", "conviene"]) and "sistema" in pregunta:
        return ("La mejor opción depende de varios factores específicos de tu ubicación y necesidades. "
                "En general, los sistemas solares fotovoltaicos son los más versátiles y fáciles de instalar "
                "en entornos urbanos. Los sistemas eólicos son más efectivos en zonas rurales o costeras "
                "con buena exposición al viento. Los termotanques solares ofrecen excelente relación "
                "costo-beneficio para calentar agua. Te recomendamos usar nuestro diagnóstico "
                "personalizado para obtener una recomendación específica para tu caso.")
    
    # Funcionamiento de paneles solares
    if "como funciona" in pregunta and any(palabra in pregunta for palabra in ["panel", "solar", "fotovoltaico"]):
        return ("Los paneles solares fotovoltaicos funcionan convirtiendo la luz solar en electricidad "
                "mediante el efecto fotoeléctrico. Están compuestos por células solares de silicio que, "
                "al recibir fotones de luz, generan un flujo de electrones (corriente continua). "
                "Esta electricidad luego pasa por un inversor que la convierte en corriente alterna "
                "utilizable en el hogar. La eficiencia típica de conversión está entre 15-22% "
                "dependiendo de la tecnología del panel.")
                
    # Funcionamiento de energía eólica
    if "como funciona" in pregunta and any(palabra in pregunta for palabra in ["eolica", "eolico", "viento", "aerogenerador", "turbina"]):
        return ("Los aerogeneradores convierten la energía cinética del viento en electricidad. "
                "Las palas del aerogenerador, diseñadas aerodinámicamente, giran cuando el viento "
                "las empuja, moviendo un eje conectado a un generador. Este generador transforma "
                "la energía mecánica en electricidad. Los sistemas domésticos suelen comenzar a "
                "generar con vientos de 3-4 m/s y alcanzan su máxima potencia con vientos de "
                "11-15 m/s, dependiendo del modelo.")
    
    # Preguntas sobre costos específicos
    if any(palabra in pregunta for palabra in ["costo", "precio", "vale", "valor"]):
        if "panel" in pregunta or "solar" in pregunta or "fotovoltaico" in pregunta:
            return ("El costo de los sistemas solares fotovoltaicos varía según la capacidad y calidad. "
                    "Una instalación doméstica típica (3-5 kW) puede costar entre $1,000-$1,500 por kW "
                    "instalado, incluyendo paneles, inversor y montaje. Para una casa promedio, esto "
                    "significa una inversión de $3,000-$7,500. Los sistemas premium con baterías y "
                    "monitorización avanzada pueden costar más. Sin embargo, con los incentivos y el "
                    "ahorro en la factura eléctrica, el retorno de inversión suele ser de 4-8 años.")
        elif "eolico" in pregunta or "eolica" in pregunta or "viento" in pregunta:
            return ("Los sistemas eólicos domésticos tienen un costo aproximado de $2,000-$5,000 por "
                    "kW de capacidad instalada. Un sistema pequeño (1-3 kW) para una casa puede costar "
                    "entre $3,000-$15,000 dependiendo del fabricante, altura de la torre y equipamiento "
                    "adicional. Son generalmente más costosos que los sistemas solares para la misma "
                    "capacidad, pero pueden ser más eficientes en ubicaciones con buen recurso eólico.")
        elif "termotanque" in pregunta or "agua caliente" in pregunta:
            return ("Un sistema de termotanque solar para una familia típica (150-300 litros) "
                    "cuesta entre $800-$2,500 dependiendo de la capacidad, tipo de colector (plano o "
                    "tubos de vacío) y si incluye un sistema de respaldo. Son una de las inversiones "
                    "en energía renovable con mejor retorno, generalmente entre 2-5 años, especialmente "
                    "si sustituyen a sistemas eléctricos de calentamiento de agua.")
    
    # No se encontró un caso especial
    return None

def buscar_respuesta_relacionada(pregunta):
    """
    Busca respuestas basadas en palabras relacionadas o sinónimos
    
    Args:
        pregunta (str): Pregunta limpia del usuario
        
    Returns:
        str: Respuesta relacionada o None si no hay coincidencias
    """
    # Mapeo de palabras relacionadas a términos en la base de conocimiento
    palabras_relacionadas = {
        # Solar
        "fotovoltaic": "paneles solares",
        "fotovoltaico": "paneles solares",
        "placas solares": "paneles solares",
        "panel solar": "paneles solares",
        "energia solar": "paneles solares",
        
        # Eólico
        "aerogenerador": "energía eólica",
        "turbina": "energía eólica",
        "viento": "energía eólica",
        "molino": "energía eólica",
        
        # Termotanque
        "calentador solar": "termotanque solar",
        "agua caliente solar": "termotanque solar",
        "calefon solar": "termotanque solar",
        
        # Baterías
        "acumulador": "baterías",
        "almacenamiento": "baterías",
        "litio": "baterías",
        "powerwall": "baterías",
        
        # Retorno de inversión
        "recuperar inversion": "retorno inversión",
        "amortizar": "retorno inversión",
        "roi": "retorno inversión",
        "rentabilidad": "retorno inversión",
        "cuanto tarda": "retorno inversión",
        
        # Mantenimiento
        "limpieza": "mantenimiento",
        "duracion": "mantenimiento",
        "vida util": "mantenimiento",
        "reparar": "mantenimiento",
        
        # Incentivos
        "subsidio": "incentivos",
        "beneficio fiscal": "incentivos",
        "descuento": "incentivos",
        "financiamiento": "incentivos",
        "credito": "incentivos",
        
        # Instalación
        "montar": "instalación",
        "colocar": "instalación",
        "instalar": "instalación",
        "implementar": "instalación",
        
        # Ahorro
        "reduccion factura": "ahorro",
        "bajar consumo": "ahorro",
        "economizar": "ahorro",
        "ahorrar": "ahorro",
        
        # Impacto ambiental
        "huella": "impacto ambiental",
        "carbono": "impacto ambiental",
        "co2": "impacto ambiental",
        "contaminacion": "impacto ambiental",
        "medioambiente": "impacto ambiental",
        "ambiente": "impacto ambiental"
    }
    
    # Buscar coincidencias en el mapeo
    for palabra, termino in palabras_relacionadas.items():
        if palabra in pregunta:
            return CONOCIMIENTO_BASE.get(termino)
    
    # Añadir lógica para preguntas compuestas
    if ("mejor" in pregunta or "recomendable" in pregunta or "recomiendas" in pregunta) and "sistema" in pregunta:
        return ("La mejor opción depende de varios factores específicos de tu ubicación y necesidades. "
                "En general, los sistemas solares fotovoltaicos son los más versátiles y fáciles de instalar "
                "en entornos urbanos. Los sistemas eólicos son más efectivos en zonas rurales o costeras "
                "con buena exposición al viento. Los termotanques solares ofrecen excelente relación "
                "costo-beneficio para calentar agua. Te recomendamos usar nuestro diagnóstico "
                "personalizado para obtener una recomendación específica para tu caso.")
    
    if "como funciona" in pregunta and "panel" in pregunta:
        return ("Los paneles solares fotovoltaicos funcionan convirtiendo la luz solar en electricidad "
                "mediante el efecto fotoeléctrico. Están compuestos por células solares de silicio que, "
                "al recibir fotones de luz, generan un flujo de electrones (corriente continua). "
                "Esta electricidad luego pasa por un inversor que la convierte en corriente alterna "
                "utilizable en el hogar. La eficiencia típica de conversión está entre 15-22% "
                "dependiendo de la tecnología del panel.")
                
    if "como funciona" in pregunta and ("eolica" in pregunta or "viento" in pregunta):
        return ("Los aerogeneradores convierten la energía cinética del viento en electricidad. "
                "Las palas del aerogenerador, diseñadas aerodinámicamente, giran cuando el viento "
                "las empuja, moviendo un eje conectado a un generador. Este generador transforma "
                "la energía mecánica en electricidad. Los sistemas domésticos suelen comenzar a "
                "generar con vientos de 3-4 m/s y alcanzan su máxima potencia con vientos de "
                "11-15 m/s, dependiendo del modelo.")
    
    # No se encontró ninguna coincidencia relacionada
    return None

def respuesta_generica(pregunta):
    """
    Genera una respuesta genérica cuando no se encuentra información específica
    
    Args:
        pregunta (str): Pregunta del usuario
        
    Returns:
        str: Respuesta genérica contextualizada
    """
    # Detectar el tipo de pregunta para dar una respuesta más contextualizada
    if "costo" in pregunta or "precio" in pregunta or "valor" in pregunta:
        return (
            "El costo de los sistemas de energía renovable varía según el tipo, "
            "capacidad, calidad y región. Los paneles solares domésticos pueden costar "
            "entre $1,000-$3,000 por kW instalado, los termotanques solares entre "
            "$800-$2,500, y los sistemas eólicos pequeños entre $2,000-$5,000 por kW. "
            "Estos valores son aproximados y es recomendable solicitar cotizaciones "
            "a proveedores locales para mayor precisión."
        )
    elif "tiempo" in pregunta or "duración" in pregunta or "vida útil" in pregunta:
        return (
            "La vida útil de los sistemas de energía renovable es considerable. "
            "Los paneles solares tienen una garantía típica de 25 años, pero pueden "
            "funcionar por 30-40 años con una reducción gradual de eficiencia. "
            "Los aerogeneradores duran unos 20-25 años, y los termotanques solares "
            "entre 15-30 años dependiendo del modelo y mantenimiento. Esto hace que "
            "sean inversiones a largo plazo con excelente retorno."
        )
    elif "mejor" in pregunta or "recomendable" in pregunta or "conviene" in pregunta:
        return (
            "La mejor solución depende de varios factores: tu ubicación geográfica, "
            "consumo energético, espacio disponible, presupuesto y objetivos específicos. "
            "En áreas con buena radiación solar, los sistemas fotovoltaicos suelen ser "
            "la opción más versátil. En zonas ventosas, los sistemas eólicos pueden ser "
            "más eficientes. Los termotanques solares ofrecen excelente retorno de inversión "
            "para calentar agua. Una evaluación personalizada es la mejor manera de determinar "
            "qué sistema se adapta mejor a tus necesidades."
        )
    else:
        return (
            "Gracias por tu pregunta sobre energías renovables. Para brindarte "
            "información más precisa y personalizada, te recomendamos usar "
            "nuestro diagnóstico inteligente o el simulador, donde podrás obtener "
            "recomendaciones específicas para tu situación particular. "
            "También puedes reformular tu pregunta con más detalles sobre "
            "qué tipo de sistema te interesa (solar, eólico, termotanque solar) "
            "o qué aspecto específico quieres conocer (costos, rendimiento, instalación)."
        )