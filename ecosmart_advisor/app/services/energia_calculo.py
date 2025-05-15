"""
Módulo para realizar cálculos relacionados con energía renovable,
recomendaciones y estimaciones.
"""
import os
from .ai_recommender import evaluar_factores_energia_renovable

def calcular_recomendacion(datos_usuario, clima):
    """
    Calcula la recomendación de energía renovable según datos del usuario y clima
    
    Args:
        datos_usuario (dict): Datos proporcionados por el usuario
        clima (dict): Datos climáticos de la ubicación
        
    Returns:
        dict: Recomendación detallada de sistema(s) de energía renovable
    """
    # Extraer datos relevantes
    consumo_mensual = float(datos_usuario['consumo_mensual'])
    superficie = float(datos_usuario['superficie_disponible'])
    radiacion_solar = clima['radiacion_solar']
    velocidad_viento = clima['velocidad_viento']
    temperatura = clima['temperatura_promedio']
    objetivo = datos_usuario['objetivo']
    
    # Calcular potencial para cada tipo de energía
    potencial_solar = calcular_potencial_solar(radiacion_solar, superficie, temperatura)
    potencial_eolico = calcular_potencial_eolico(velocidad_viento, superficie)
    potencial_termotanque = calcular_potencial_termotanque(radiacion_solar, temperatura)
    
    # Calcular qué porcentaje del consumo podría cubrir cada sistema
    cobertura_solar = min(100, (potencial_solar['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_eolica = min(100, (potencial_eolico['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_termotanque = min(30, (potencial_termotanque['ahorro_mensual'] / consumo_mensual) * 100)
    
    # Determinar viabilidad de cada opción
    umbral_viabilidad_solar = 15  # % mínimo de cobertura para considerarse viable
    umbral_viabilidad_eolica = 15  # % mínimo de cobertura para considerarse viable
    umbral_viabilidad_termotanque = 5  # % mínimo de cobertura para considerarse viable
    
    es_viable_solar = cobertura_solar >= umbral_viabilidad_solar
    es_viable_eolica = cobertura_eolica >= umbral_viabilidad_eolica
    es_viable_termotanque = cobertura_termotanque >= umbral_viabilidad_termotanque
    
    # Ordenar opciones viables según objetivo del usuario
    opciones_viables = []
    
    if es_viable_solar:
        opciones_viables.append({
            'tipo': 'solar',
            'cobertura': cobertura_solar,
            'generacion_mensual': potencial_solar['generacion_mensual'],
            'ahorro_anual': potencial_solar['generacion_mensual'] * 12 * 0.15,  # 0.15 USD/kWh estimado
            'impacto_ambiental': potencial_solar['generacion_mensual'] * 12 * 0.4,  # 0.4 kg CO2 por kWh
            'detalle': potencial_solar
        })
    
    if es_viable_eolica:
        opciones_viables.append({
            'tipo': 'eolica',
            'cobertura': cobertura_eolica,
            'generacion_mensual': potencial_eolico['generacion_mensual'],
            'ahorro_anual': potencial_eolico['generacion_mensual'] * 12 * 0.15,
            'impacto_ambiental': potencial_eolico['generacion_mensual'] * 12 * 0.4,
            'detalle': potencial_eolico
        })
    
    if es_viable_termotanque:
        opciones_viables.append({
            'tipo': 'termotanque_solar',
            'cobertura': cobertura_termotanque,
            'generacion_mensual': potencial_termotanque['ahorro_mensual'],
            'ahorro_anual': potencial_termotanque['ahorro_mensual'] * 12 * 0.15,
            'impacto_ambiental': potencial_termotanque['ahorro_mensual'] * 12 * 0.4,
            'detalle': potencial_termotanque
        })
    
    # Ordenar según el objetivo del usuario
    if objetivo == 'ahorro':
        opciones_viables.sort(key=lambda x: x['ahorro_anual'], reverse=True)
    elif objetivo == 'ambiental':
        opciones_viables.sort(key=lambda x: x['impacto_ambiental'], reverse=True)
    else:  # Por defecto, ordenar por cobertura
        opciones_viables.sort(key=lambda x: x['cobertura'], reverse=True)
    
    # Evaluar posibles combinaciones si hay múltiples opciones viables
    combinaciones = []
    if len(opciones_viables) >= 2:
        # Combinar solar + termotanque
        if es_viable_solar and es_viable_termotanque:
            cobertura_combinada = min(100, cobertura_solar + cobertura_termotanque)
            combinaciones.append({
                'tipos': ['solar', 'termotanque_solar'],
                'cobertura': cobertura_combinada,
                'detalle': 'Paneles solares para electricidad y termotanque solar para agua caliente'
            })
        
        # Combinar eólica + termotanque
        if es_viable_eolica and es_viable_termotanque:
            cobertura_combinada = min(100, cobertura_eolica + cobertura_termotanque)
            combinaciones.append({
                'tipos': ['eolica', 'termotanque_solar'],
                'cobertura': cobertura_combinada,
                'detalle': 'Aerogenerador para electricidad y termotanque solar para agua caliente'
            })
    
    # Preparar la respuesta consolidada
    if not opciones_viables:
        recomendacion = {
            'mensaje': "Basado en la información proporcionada, no se recomienda ninguna solución de energía renovable. Considera aumentar la superficie disponible o implementar medidas de eficiencia energética para reducir el consumo.",
            'opciones': [],
            'combinaciones': [],
            'principal': None
        }
    else:
        recomendacion = {
            'mensaje': f"Se identificaron {len(opciones_viables)} opciones viables de energía renovable para tu ubicación.",
            'opciones': opciones_viables,
            'combinaciones': combinaciones,
            'principal': opciones_viables[0]  # La mejor opción según criterio de ordenamiento
        }
    
    return recomendacion

def calcular_potencial_solar(radiacion_solar, superficie, temperatura):
    """
    Calcula el potencial de generación solar fotovoltaica
    
    Args:
        radiacion_solar (float): kWh/m²/día
        superficie (float): Metros cuadrados disponibles
        temperatura (float): Temperatura promedio anual en °C
        
    Returns:
        dict: Detalles del potencial solar fotovoltaico
    """
    # Eficiencia del panel (varía según tecnología)
    eficiencia_panel = 0.18  # 18% de eficiencia (paneles monocristalinos modernos)
    
    # Factor de pérdida por temperatura
    # Los paneles pierden eficiencia a temperaturas elevadas (aprox. 0.4% por cada °C sobre 25°C)
    factor_temperatura = 1 - max(0, (temperatura - 25) * 0.004)
    
    # Otras pérdidas del sistema (inversores, cables, etc.)
    otras_perdidas = 0.85  # 15% de pérdidas
    
    # Superficie utilizable (no todo el espacio se puede aprovechar)
    factor_utilizacion = 0.7  # 70% del espacio disponible
    superficie_paneles = superficie * factor_utilizacion
    
    # Calcular potencia instalable (kWp)
    potencia_por_m2 = 0.185  # kWp por m² (aproximado para paneles modernos)
    potencia_instalable = superficie_paneles * potencia_por_m2
    
    # Calcular generación mensual
    horas_sol_pico = radiacion_solar  # Las HSP equivalen a la radiación en kWh/m²/día
    generacion_diaria = potencia_instalable * horas_sol_pico * eficiencia_panel * factor_temperatura * otras_perdidas
    generacion_mensual = generacion_diaria * 30  # Aproximado
    
    # Retornar detalles
    return {
        'potencia_instalable': round(potencia_instalable, 2),  # kWp
        'generacion_diaria': round(generacion_diaria, 1),  # kWh/día
        'generacion_mensual': round(generacion_mensual, 1),  # kWh/mes
        'superficie_paneles': round(superficie_paneles, 1),  # m²
        'cantidad_paneles': round(superficie_paneles / 1.7),  # Asumiendo 1.7m² por panel
    }

def calcular_potencial_eolico(velocidad_viento, superficie):
    """
    Calcula el potencial de generación eólica para pequeña escala
    
    Args:
        velocidad_viento (float): Velocidad promedio del viento en m/s
        superficie (float): Metros cuadrados disponibles (usado para estimar limitaciones)
        
    Returns:
        dict: Detalles del potencial eólico
    """
    # Para pequeña escala, el tamaño del aerogenerador depende más de reglamentaciones 
    # y disponibilidad que de la superficie
    
    # Factores determinantes para eólica doméstica:
    # 1. Velocidad del viento
    if velocidad_viento < 3.0:
        factor_viabilidad = 0.3  # Muy baja viabilidad
    elif velocidad_viento < 4.0:
        factor_viabilidad = 0.6  # Baja viabilidad
    elif velocidad_viento < 5.0:
        factor_viabilidad = 0.8  # Viabilidad media
    else:
        factor_viabilidad = 1.0  # Alta viabilidad
    
    # Tamaño del aerogenerador (para aplicaciones domésticas)
    # Asumimos que con suficiente superficie, podemos instalar hasta un aerogenerador de 3kW
    potencia_maxima = min(3.0, superficie / 30)  # 1kW por cada 10m² como límite aproximado
    
    # Calcular generación usando la fórmula de la ley cúbica del viento
    # P = 0.5 * ρ * A * Cp * V³ * η
    # Donde:
    # - ρ es la densidad del aire (aprox. 1.225 kg/m³)
    # - A es el área del rotor
    # - Cp es el coeficiente de potencia (teóricamente máximo 0.593, Límite de Betz)
    # - V³ es el cubo de la velocidad del viento
    # - η es la eficiencia del generador
    
    # Para simplificar, usamos una fórmula empírica para aerogeneradores pequeños
    # donde estos factores ya están contemplados en una curva de potencia
    
    # Generación aproximada para un aerogenerador de 1kW nominal (a 11 m/s)
    if velocidad_viento < 2.5:
        generacion_nominal = 0  # Por debajo de la velocidad de arranque
    else:
        # Aproximación simplificada de la curva de potencia
        generacion_nominal = potencia_maxima * (0.2 * (velocidad_viento ** 3) / (11 ** 3))
        generacion_nominal = min(generacion_nominal, potencia_maxima)  # No exceder la potencia máxima
    
    # Factor de capacidad (porcentaje del tiempo que genera a potencia nominal)
    factor_capacidad = 0.25 * factor_viabilidad
    
    # Generación diaria y mensual
    generacion_diaria = generacion_nominal * 24 * factor_capacidad
    generacion_mensual = generacion_diaria * 30
    
    return {
        'potencia_instalable': round(potencia_maxima, 2),  # kW
        'generacion_diaria': round(generacion_diaria, 1),  # kWh/día
        'generacion_mensual': round(generacion_mensual, 1),  # kWh/mes
        'factor_viabilidad': round(factor_viabilidad, 2),  # 0-1
        'velocidad_minima': 2.5,  # m/s (velocidad de arranque típica)
        'velocidad_nominal': 11,  # m/s (velocidad a potencia nominal)
    }

def calcular_potencial_termotanque(radiacion_solar, temperatura):
    """
    Calcula el potencial de ahorro con un termotanque solar
    
    Args:
        radiacion_solar (float): kWh/m²/día
        temperatura (float): Temperatura promedio anual en °C
        
    Returns:
        dict: Detalles del potencial de ahorro con termotanque solar
    """
    # Consumo típico de agua caliente por persona
    consumo_agua_caliente_diario = 50  # litros/persona/día
    personas_promedio = 4  # asumimos una familia típica
    
    # Consumo total de agua caliente
    consumo_total = consumo_agua_caliente_diario * personas_promedio  # litros/día
    
    # Energía necesaria para calentar el agua
    # E = m * c * ΔT
    # Donde:
    # - m es la masa (litros de agua)
    # - c es el calor específico del agua (0.00116 kWh/kg°C)
    # - ΔT es el incremento de temperatura (asumimos de temperatura ambiente a 45°C)
    
    calor_especifico = 0.00116  # kWh/kg°C
    temperatura_deseada = 45  # °C
    energia_necesaria = consumo_total * calor_especifico * (temperatura_deseada - temperatura)
    
    # Eficiencia del termotanque solar
    eficiencia_termotanque = 0.7  # 70% de eficiencia
    
    # Capacidad de captura (dependiendo de la radiación solar)
    factor_radiacion = min(1.0, radiacion_solar / 4.0)  # Normalizado para una radiación de referencia de 4 kWh/m²/día
    
    # Energía aportada por el termotanque solar
    energia_aportada = energia_necesaria * eficiencia_termotanque * factor_radiacion
    
    # Convertir a kWh mensuales (equivalente eléctrico)
    ahorro_mensual = energia_aportada * 30
    
    # Retornar detalles
    return {
        'consumo_agua_caliente': consumo_total,  # litros/día
        'energia_necesaria': round(energia_necesaria, 1),  # kWh/día
        'energia_aportada': round(energia_aportada, 1),  # kWh/día
        'ahorro_mensual': round(ahorro_mensual, 1),  # kWh/mes
        'eficiencia': round(eficiencia_termotanque * factor_radiacion, 2),  # eficiencia ajustada
        'personas': personas_promedio
    }

def calcular_estimacion_sin_kwh(tipo_vivienda, equipos):
    """
    Estima el consumo mensual en kWh cuando el usuario no proporciona este dato
    
    Args:
        tipo_vivienda (str): Tipo de vivienda (casa, apartamento, etc.)
        equipos (list): Lista de equipos eléctricos
        
    Returns:
        float: Consumo estimado en kWh/mes
    """
    # Consumo base según tipo de vivienda
    consumos_base = {
        'casa_pequena': 250,
        'casa_mediana': 350,
        'casa_grande': 450,
        'apartamento': 200,
        'oficina': 300,
        'comercio': 500,
        'otro': 300
    }
    
    # Si no se especifica el tipo, usar una casa mediana por defecto
    consumo_base = consumos_base.get(tipo_vivienda, 350)
    
    # Adicionales por cada equipo
    adicionales_equipo = {
        'aire_acondicionado': 150,
        'calefaccion_electrica': 200,
        'bomba_calor': 100,
        'refrigerador': 50,
        'lavadora': 30,
        'secadora': 80,
        'lavavajillas': 30,
        'horno_electrico': 40,
        'computadoras': 25,
        'iluminacion_led': 15,
        'iluminacion_tradicional': 40,
        'piscina': 120,
        'jacuzzi': 80,
        'otro': 30
    }
    
    # Sumar consumo de equipos
    consumo_equipos = sum(adicionales_equipo.get(equipo, 0) for equipo in equipos)
    
    # Retornar estimación total
    return consumo_base + consumo_equipos