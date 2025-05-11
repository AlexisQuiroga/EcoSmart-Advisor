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
    # Información sobre tecnologías renovables
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
    
    # Información sobre la funcionalidad de la página
    "simulador": (
        "El simulador de EcoSmart Advisor te permite probar diferentes escenarios "
        "de instalación de energías renovables. Puedes ajustar variables como la capacidad "
        "de paneles solares, potencia del aerogenerador o tamaño del termotanque, y ver "
        "estimaciones realistas de generación, ahorro económico e impacto ambiental. "
        "Para usar el simulador, haz clic en el botón 'Usar Simulador' en la página principal."
    ),
    "diagnóstico": (
        "La herramienta de diagnóstico analiza tu ubicación, consumo energético y condiciones "
        "locales para recomendarte el sistema de energía renovable más adecuado para tu caso. "
        "Introduce datos como tu ubicación, consumo mensual, presupuesto y superficie disponible, "
        "y el sistema calculará qué opción te ofrece mejor relación costo-beneficio."
    ),
    "ubicación": (
        "Para obtener recomendaciones precisas, el sistema necesita conocer tu ubicación. "
        "Puedes introducir tu provincia, ciudad y calle, o utilizar el mapa interactivo "
        "para seleccionar tu ubicación exacta. Esto nos permite obtener datos precisos de "
        "radiación solar, velocidad del viento y clima para tu zona específica."
    ),
    
    "funcionalidades": (
        "EcoSmart Advisor ofrece tres herramientas principales: 1) El Diagnóstico analiza tu ubicación, "
        "consumo y necesidades para recomendarte el sistema de energía renovable más adecuado. "
        "2) El Simulador te permite experimentar con diferentes configuraciones de sistemas y ver "
        "resultados personalizados en tiempo real. 3) El Chatbot (donde estás ahora) responde preguntas "
        "educativas sobre energías renovables y te guía en el uso de la aplicación."
    ),
    "chatbot": (
        "Soy el asistente virtual de EcoSmart Advisor. Estoy aquí para responder tus preguntas "
        "sobre energías renovables, ayudarte a entender cómo funcionan las diferentes tecnologías, "
        "y guiarte en el uso de nuestra plataforma. Puedes hacerme preguntas sobre paneles solares, "
        "energía eólica, termotanques solares, o cómo utilizar las herramientas de esta página."
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
    
    # Manejar preguntas de ejemplo específicas que mostramos en la interfaz
    preguntas_ejemplo = {
        "¿qué sistema de energía renovable me conviene?": 
            "Para determinar qué sistema de energía renovable te conviene, necesitamos considerar varios factores: tu ubicación geográfica, consumo energético, presupuesto disponible y espacio. En general, los paneles solares son versátiles y funcionan bien en la mayoría de las regiones con buena exposición solar. Los sistemas eólicos son mejores en áreas con vientos constantes. Los termotanques solares son una excelente opción si buscas reducir el consumo para calentar agua. Te recomiendo usar nuestra herramienta de diagnóstico que analizará tu situación particular y te dará una recomendación personalizada.",
        
        "¿cuánto cuesta instalar paneles solares?": 
            "El costo de instalar paneles solares varía según la capacidad del sistema, calidad de los componentes y tu ubicación. En promedio, un sistema residencial de 3-5 kW puede costar entre $1,000 y $3,000 USD por kW instalado, incluyendo paneles, inversor, estructura, instalación y trámites. Los factores que más influyen son: capacidad total (kW), tipo y eficiencia de los paneles, tipo de instalación (techo o suelo), complejidad del montaje y costos laborales locales. El retorno de inversión suele ser de 4-7 años, dependiendo de las tarifas eléctricas de tu zona.",
        
        "¿cuánto puedo ahorrar con energía renovable?": 
            "El ahorro con energía renovable depende de varios factores: tu consumo actual, costo de la electricidad en tu zona, tamaño y tipo del sistema instalado. En promedio, un sistema solar bien dimensionado puede reducir tu factura eléctrica entre un 50% y 90%. Un termotanque solar puede reducir el costo de calentar agua en 70-80%. Con sistemas de baterías, el ahorro puede ser aún mayor. A largo plazo, considerando que estos sistemas duran 25-30 años y las tarifas eléctricas tienden a aumentar, el ahorro acumulado puede superar varias veces la inversión inicial.",
        
        "¿qué es un termotanque solar?": 
            "Un termotanque solar es un sistema que utiliza la energía del sol para calentar agua sin consumir electricidad o gas. Consta de colectores solares (donde el agua o un fluido caloportador se calienta) y un tanque aislado térmicamente para almacenar el agua caliente. Existen dos tipos principales: circulación natural (termosifón) donde el agua circula por diferencia de densidad, y circulación forzada que usa una pequeña bomba. Son muy eficientes, pudiendo reducir hasta un 80% del consumo energético para calentar agua y tienen una vida útil de 15-20 años con mínimo mantenimiento.",
            
        "¿qué sistema de energía renovable es más económico?": 
            "El sistema de energía renovable más económico en términos de inversión inicial suele ser el termotanque solar, con costos desde $800-1,500 USD para una familia pequeña. Ofrece un excelente retorno de inversión (2-4 años) al reducir significativamente el consumo para calentar agua. Los paneles solares fotovoltaicos tienen una inversión inicial mayor ($3,000-9,000 USD para sistemas residenciales), pero generan electricidad para todos tus equipos con retornos de inversión de 4-7 años. Los sistemas eólicos domésticos suelen tener costos similares a los solares pero requieren condiciones de viento específicas. La opción más económica para tu caso específico dependerá de tu consumo, ubicación y necesidades particulares.",
            
        "¿para qué sirve el simulador?": 
            "El simulador de EcoSmart Advisor te permite probar diferentes configuraciones de sistemas de energía renovable sin compromiso y ver resultados personalizados en tiempo real. Puedes ajustar parámetros como la capacidad de paneles solares, potencia de aerogeneradores o tamaño de termotanques, y obtener estimaciones de generación energética, ahorro económico e impacto ambiental. El simulador toma en cuenta tu ubicación geográfica, consumo energético y datos climáticos locales para brindarte resultados precisos. Es una herramienta ideal para explorar opciones antes de decidirte por una inversión específica."
    }
    
    # Verificar si la pregunta es una de las preguntas de ejemplo o muy similar
    for ejemplo, respuesta in preguntas_ejemplo.items():
        if pregunta_limpia == ejemplo.lower() or pregunta_limpia in ejemplo.lower() or ejemplo.lower() in pregunta_limpia:
            print(f"Coincidencia con pregunta de ejemplo: {ejemplo}")
            return respuesta
    
    # Creamos un sistema de puntuación para seleccionar la mejor respuesta
    mejores_coincidencias = {}
    
    # Verificar primero en la base de conocimiento para palabras clave exactas
    for palabra_clave, respuesta in CONOCIMIENTO_BASE.items():
        if palabra_clave.lower() == pregunta_limpia:  # Coincidencia exacta
            print(f"Coincidencia exacta con palabra clave: {palabra_clave}")
            return respuesta
        elif palabra_clave.lower() in pregunta_limpia:  # Palabras clave en la pregunta
            palabras_clave = palabra_clave.lower().split()
            palabras_pregunta = pregunta_limpia.split()
            # Calcular un puntaje basado en la proporción de palabras que coinciden
            proporcion = len(palabras_clave) / len(palabras_pregunta) if palabras_pregunta else 0
            mejores_coincidencias[palabra_clave] = proporcion * 0.8  # 80% de confianza si contiene la palabra clave
            print(f"Coincidencia parcial con: {palabra_clave}, puntuación: {proporcion * 0.8}")
    
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
                print(f"Coincidencia exacta con término relacionado: {termino_relacionado} -> {tema}")
            elif termino_relacionado in palabra:  # El término relacionado es parte de la palabra
                if tema in mejores_coincidencias:
                    mejores_coincidencias[tema] += 0.3  # Aumentar la puntuación
                else:
                    mejores_coincidencias[tema] = 0.3  # 30% de confianza
                print(f"Coincidencia parcial con término relacionado: {termino_relacionado} -> {tema}")
    
    # Determinar la mejor coincidencia
    mejor_tema = None
    mejor_puntuacion = 0.3  # Bajamos el umbral mínimo para considerar una coincidencia como relevante
    
    print(f"Mejores coincidencias: {mejores_coincidencias}")
    
    for tema, puntuacion in mejores_coincidencias.items():
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_tema = tema
    
    print(f"Mejor tema encontrado: {mejor_tema}, puntuación: {mejor_puntuacion if mejor_tema else 0}")
    
    # Si encontramos una buena coincidencia, devolver la respuesta correspondiente
    if mejor_tema:
        print(f"Retornando respuesta para: {mejor_tema}")
        return CONOCIMIENTO_BASE[mejor_tema]
    
    # Verificar casos especiales
    respuesta_especial = verificar_casos_especiales(pregunta_limpia)
    if respuesta_especial:
        print("Encontrada respuesta especial")
        return respuesta_especial
    
    # Si no hay coincidencias suficientemente buenas, generar una respuesta genérica
    print("No se encontraron coincidencias suficientes, utilizando respuesta genérica")
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
        "fotovoltaicos": "paneles solares",
        "solares": "paneles solares",
        
        # Eólico
        "aerogenerador": "energía eólica",
        "turbina": "energía eólica",
        "viento": "energía eólica",
        "molino": "energía eólica",
        "eolica": "energía eólica",
        "eolico": "energía eólica",
        "aerogeneradores": "energía eólica",
        "turbinas": "energía eólica",
        "eólico": "energía eólica",
        "eólica": "energía eólica",
        
        # Termotanque
        "calentador": "termotanque solar",
        "termotanque": "termotanque solar",
        "agua caliente": "termotanque solar",
        "calefon": "termotanque solar",
        "termica": "termotanque solar",
        "termico": "termotanque solar",
        "calentadores": "termotanque solar",
        "termotanques": "termotanque solar",
        "térmico": "termotanque solar",
        "térmica": "termotanque solar",
        
        # Baterías
        "bateria": "baterías",
        "acumulador": "baterías",
        "almacenamiento": "baterías",
        "almacenar": "baterías",
        "litio": "baterías",
        "powerwall": "baterías",
        "baterias": "baterías",
        "acumuladores": "baterías",
        
        # Retorno de inversión
        "inversion": "retorno inversión",
        "recuperar": "retorno inversión",
        "amortizar": "retorno inversión",
        "roi": "retorno inversión",
        "rentabilidad": "retorno inversión",
        "rendimiento": "retorno inversión",
        "ganancia": "retorno inversión",
        
        # Costos e instalación
        "costo": "costos",
        "precio": "costos",
        "vale": "costos",
        "valen": "costos",
        "cuesta": "costos",
        "cuestan": "costos",
        "instalacion": "instalación",
        "instalar": "instalación",
        "montar": "instalación",
        "colocar": "instalación",
        
        # Mantenimiento
        "limpiar": "mantenimiento",
        "limpieza": "mantenimiento",
        "cuidado": "mantenimiento",
        "servicio": "mantenimiento",
        "reparar": "mantenimiento",
        "duracion": "mantenimiento",
        "duran": "mantenimiento",
        
        # Ahorro
        "ahorrar": "ahorro",
        "economizar": "ahorro",
        "economico": "ahorro",
        "economica": "ahorro",
        "beneficio": "ahorro",
        "conviene": "ahorro",
        
        # Impacto ambiental
        "ambiente": "impacto ambiental",
        "ecologico": "impacto ambiental",
        "ecologia": "impacto ambiental",
        "contaminacion": "impacto ambiental",
        "carbono": "impacto ambiental",
        "co2": "impacto ambiental",
        "sostenible": "impacto ambiental",
        "planeta": "impacto ambiental",
        "huella": "impacto ambiental",
        "verde": "impacto ambiental",
        "emisiones": "impacto ambiental",
        
        # Funcionalidades de la aplicación
        "diagnóstico": "funcionalidades",
        "diagnostico": "funcionalidades",
        "simulador": "funcionalidades",
        "simulacion": "funcionalidades",
        "chatbot": "funcionalidades",
        "asistente": "funcionalidades",
        "herramienta": "funcionalidades",
        "app": "funcionalidades",
        "aplicación": "funcionalidades",
        "aplicacion": "funcionalidades",
        "cuanto tarda": "retorno inversión",
        "años": "retorno inversión",
        
        # Simulador
        "simular": "simulador",
        "simulacion": "simulador",
        "probar": "simulador",
        "escenario": "simulador",
        "ajustar": "simulador",
        "calcular": "simulador",
        "usar simulador": "simulador",
        "como usar el simulador": "simulador",
        "para que sirve el simulador": "simulador",
        
        # Diagnóstico
        "diagnosticar": "diagnóstico",
        "analizar": "diagnóstico",
        "recomendar": "diagnóstico",
        "recomendacion": "diagnóstico",
        "que me conviene": "diagnóstico",
        "que sistema": "diagnóstico",
        "para que sirve el diagnostico": "diagnóstico",
        "como funciona el diagnostico": "diagnóstico",
        
        # Ubicación
        "coordenadas": "ubicación",
        "direccion": "ubicación", 
        "geolocalizacion": "ubicación",
        "mapa": "ubicación",
        "provincia": "ubicación",
        "ciudad": "ubicación",
        "seleccionar ubicacion": "ubicación",
        "como elegir ubicacion": "ubicación",
        
        # Chatbot
        "asistente": "chatbot",
        "bot": "chatbot",
        "ayudante": "chatbot",
        "preguntar": "chatbot",
        "responder": "chatbot",
        "para que sirve el chat": "chatbot",
        "como usar el chat": "chatbot",
        
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
    # Verificar si la pregunta está completamente fuera de tema
    palabras_energia = ["energia", "energía", "renovable", "solar", "eolica", "eólica", 
                       "panel", "termotanque", "simulador", "diagnóstico", "ubicación", 
                       "consumo", "ahorro", "electricidad", "instalación", "viento", "sol"]
    
    es_tema_relacionado = False
    pregunta_lower = pregunta.lower()
    for palabra in palabras_energia:
        if palabra in pregunta_lower:
            es_tema_relacionado = True
            break
    
    if not es_tema_relacionado:
        return (
            "Lo siento, pero estoy especializado en temas de energías renovables y "
            "en el uso de la plataforma EcoSmart Advisor. Por favor, reformula tu "
            "pregunta para que esté relacionada con estos temas. Puedo ayudarte con "
            "información sobre paneles solares, energía eólica, termotanques solares, "
            "o cómo utilizar las diferentes herramientas de nuestra plataforma como "
            "el diagnóstico y el simulador."
        )
    else:
        # Ofrecer una respuesta más orientativa con ejemplos de preguntas específicas
        preguntas_sugeridas = [
            "¿Qué sistema de energía renovable me conviene?",
            "¿Cuánto cuesta instalar paneles solares?",
            "¿Qué es un termotanque solar?",
            "¿Cuánto puedo ahorrar con energía renovable?",
            "¿Para qué sirve el simulador?"
        ]
        
        # Seleccionar 3 preguntas sugeridas aleatorias
        import random
        muestra_preguntas = random.sample(preguntas_sugeridas, min(3, len(preguntas_sugeridas)))
        
        sugerencias = "<br>".join([f"• {p}" for p in muestra_preguntas])
        
        return (
            "Gracias por tu interés en energías renovables. Para darte información "
            "más precisa, te invito a ser más específico en tu pregunta o a probar "
            "con alguna de estas consultas:<br><br>" + sugerencias + "<br><br>"
            "También puedes utilizar nuestro diagnóstico inteligente o el simulador "
            "para obtener recomendaciones personalizadas según tu ubicación y consumo energético."
        )