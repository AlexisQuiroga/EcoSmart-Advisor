"""
Módulo para simular instalaciones de energía renovable
con diferentes parámetros y calcular su rendimiento.
"""
from ecosmart_advisor.app.services.clima_api import obtener_datos_clima

def simular_instalacion(datos):
    """
    Simula la instalación de un sistema de energía renovable
    y calcula su rendimiento esperado
    
    Args:
        datos (dict): Parámetros de la simulación (tipo, capacidad, ubicación, etc.)
        
    Returns:
        dict: Resultados de la simulación
    """
    # Extraer datos de la simulación
    tipo_instalacion = datos['tipo_instalacion']
    capacidad = float(datos['capacidad'])
    ubicacion = datos['ubicacion']
    consumo_mensual = float(datos['consumo_mensual'])
    descripcion_ubicacion = datos.get('descripcion_ubicacion', '')
    
    # Obtener datos climáticos
    clima = obtener_datos_clima(ubicacion)
    
    # Simular según el tipo de instalación
    if tipo_instalacion == 'solar':
        resultados = simular_solar(capacidad, clima, consumo_mensual)
    elif tipo_instalacion == 'eolica':
        resultados = simular_eolica(capacidad, clima, consumo_mensual)
    elif tipo_instalacion == 'termotanque_solar':
        resultados = simular_termotanque(capacidad, clima, consumo_mensual)
    else:
        return {'error': 'Tipo de instalación no válido'}
    
    # Agregar métricas ambientales
    resultados['metricas_ambientales'] = calcular_metricas_ambientales(resultados['generacion_anual'])
    
    # Agregar datos de cobertura
    resultados['cobertura'] = min(100, (resultados['generacion_mensual'] / consumo_mensual) * 100)
    
    # Agregar datos de ahorro económico
    # Asumiendo un precio promedio de 0.15 USD/kWh
    precio_kwh = 0.15
    resultados['ahorro_mensual_usd'] = resultados['generacion_mensual'] * precio_kwh
    resultados['ahorro_anual_usd'] = resultados['generacion_anual'] * precio_kwh
    
    # Calcular retorno de inversión
    if 'costo_estimado' in resultados and resultados['costo_estimado'] > 0:
        resultados['retorno_inversion_anos'] = resultados['costo_estimado'] / resultados['ahorro_anual_usd']
    else:
        resultados['retorno_inversion_anos'] = None
    
    return resultados

def simular_solar(capacidad_kw, clima, consumo_mensual):
    """
    Simula una instalación solar fotovoltaica
    
    Args:
        capacidad_kw (float): Capacidad en kW del sistema
        clima (dict): Datos climáticos
        consumo_mensual (float): Consumo mensual en kWh
        
    Returns:
        dict: Resultados de la simulación
    """
    # Extraer radiación solar
    radiacion_solar = clima['radiacion_solar']  # kWh/m²/día
    temperatura = clima['temperatura_promedio']  # °C
    
    # Factor de pérdida por temperatura
    factor_temperatura = 1 - max(0, (temperatura - 25) * 0.004)
    
    # Otras pérdidas del sistema (inversores, cables, etc.)
    otras_perdidas = 0.85  # 15% de pérdidas
    
    # Calcular superficie necesaria
    potencia_por_m2 = 0.185  # kWp por m² (aproximado para paneles modernos)
    superficie_paneles = capacidad_kw / potencia_por_m2
    
    # Calcular generación
    horas_sol_pico = radiacion_solar  # Las HSP equivalen a la radiación en kWh/m²/día
    generacion_diaria = capacidad_kw * horas_sol_pico * factor_temperatura * otras_perdidas
    generacion_mensual = generacion_diaria * 30  # Aproximado
    generacion_anual = generacion_diaria * 365
    
    # Estimar costo del sistema
    costo_por_kw = 1200  # USD/kW (varía según país y tecnología)
    costo_estimado = capacidad_kw * costo_por_kw
    
    # Retornar resultados
    return {
        'tipo': 'solar',
        'capacidad_kw': capacidad_kw,
        'superficie_m2': round(superficie_paneles, 1),
        'generacion_diaria': round(generacion_diaria, 1),
        'generacion_mensual': round(generacion_mensual, 1),
        'generacion_anual': round(generacion_anual, 1),
        'costo_estimado': round(costo_estimado, 0),
        'factor_capacidad': round(generacion_anual / (capacidad_kw * 8760) * 100, 1),  # Porcentaje
        'eficiencia_sistema': round(factor_temperatura * otras_perdidas * 100, 1),  # Porcentaje
        'detalle_clima': {
            'radiacion_solar': radiacion_solar,
            'temperatura': temperatura,
            'ubicacion': clima['ubicacion']
        }
    }

def simular_eolica(capacidad_kw, clima, consumo_mensual):
    """
    Simula una instalación eólica
    
    Args:
        capacidad_kw (float): Capacidad en kW del aerogenerador
        clima (dict): Datos climáticos
        consumo_mensual (float): Consumo mensual en kWh
        
    Returns:
        dict: Resultados de la simulación
    """
    # Extraer velocidad del viento
    velocidad_viento = clima['velocidad_viento']  # m/s
    
    # Evaluar viabilidad según velocidad
    if velocidad_viento < 3.0:
        factor_viabilidad = 0.3  # Muy baja viabilidad
    elif velocidad_viento < 4.0:
        factor_viabilidad = 0.6  # Baja viabilidad
    elif velocidad_viento < 5.0:
        factor_viabilidad = 0.8  # Viabilidad media
    else:
        factor_viabilidad = 1.0  # Alta viabilidad
    
    # Velocidades características
    velocidad_arranque = 2.5  # m/s
    velocidad_nominal = 11.0  # m/s
    velocidad_corte = 25.0  # m/s
    
    # Calcular factor de capacidad estimado
    # Este cálculo es una aproximación, en la realidad depende de la distribución de Weibull del viento
    if velocidad_viento < velocidad_arranque:
        factor_capacidad = 0
    elif velocidad_viento > velocidad_nominal:
        factor_capacidad = 0.35 * factor_viabilidad  # Factor máximo para pequeños aerogeneradores
    else:
        # Interpolación para velocidades entre arranque y nominal
        factor_capacidad = (0.35 * factor_viabilidad) * ((velocidad_viento - velocidad_arranque) / 
                                                     (velocidad_nominal - velocidad_arranque))
    
    # Calcular generación
    horas_anuales = 8760  # horas en un año
    generacion_anual = capacidad_kw * factor_capacidad * horas_anuales
    generacion_mensual = generacion_anual / 12
    generacion_diaria = generacion_mensual / 30
    
    # Estimar costo del sistema
    costo_por_kw = 2000  # USD/kW (varía según país y tecnología)
    costo_estimado = capacidad_kw * costo_por_kw
    
    # Retornar resultados
    return {
        'tipo': 'eolica',
        'capacidad_kw': capacidad_kw,
        'generacion_diaria': round(generacion_diaria, 1),
        'generacion_mensual': round(generacion_mensual, 1),
        'generacion_anual': round(generacion_anual, 1),
        'costo_estimado': round(costo_estimado, 0),
        'factor_capacidad': round(factor_capacidad * 100, 1),  # Porcentaje
        'factor_viabilidad': round(factor_viabilidad, 2),
        'detalle_viento': {
            'velocidad_viento': velocidad_viento,
            'velocidad_arranque': velocidad_arranque,
            'velocidad_nominal': velocidad_nominal,
            'velocidad_corte': velocidad_corte,
            'ubicacion': clima['ubicacion']
        }
    }

def simular_termotanque(capacidad_litros, clima, consumo_mensual):
    """
    Simula una instalación de termotanque solar
    
    Args:
        capacidad_litros (float): Capacidad en litros del termotanque
        clima (dict): Datos climáticos
        consumo_mensual (float): Consumo mensual en kWh
        
    Returns:
        dict: Resultados de la simulación
    """
    # Extraer datos climáticos
    radiacion_solar = clima['radiacion_solar']  # kWh/m²/día
    temperatura = clima['temperatura_promedio']  # °C
    
    # Personas que pueden abastecerse con este termotanque
    personas_abastecidas = capacidad_litros / 50  # Asumiendo 50L/persona/día
    
    # Eficiencia del termotanque solar
    eficiencia_termotanque = 0.7  # 70% de eficiencia
    
    # Capacidad de captura (dependiendo de la radiación solar)
    factor_radiacion = min(1.0, radiacion_solar / 4.0)  # Normalizado para una radiación de referencia de 4 kWh/m²/día
    
    # Consumo típico de energía para calentamiento de agua
    # Estimamos 1 kWh para elevar 1L de agua a 45°C desde la temperatura ambiente
    energia_necesaria_diaria = capacidad_litros * 0.00116 * (45 - temperatura)
    
    # Energía aportada por el termotanque solar
    energia_aportada_diaria = energia_necesaria_diaria * eficiencia_termotanque * factor_radiacion
    
    # Calcular ahorro energético
    ahorro_mensual = energia_aportada_diaria * 30
    ahorro_anual = energia_aportada_diaria * 365
    
    # Estimar costo del sistema
    costo_base = 800  # USD (costo base del sistema)
    costo_por_litro = 2  # USD/litro
    costo_estimado = costo_base + capacidad_litros * costo_por_litro
    
    # Retornar resultados
    return {
        'tipo': 'termotanque_solar',
        'capacidad_litros': round(capacidad_litros, 0),
        'personas_abastecidas': round(personas_abastecidas, 1),
        'energia_necesaria_diaria': round(energia_necesaria_diaria, 1),
        'energia_aportada_diaria': round(energia_aportada_diaria, 1),
        'generacion_mensual': round(ahorro_mensual, 1),  # Para compatibilidad con otros tipos
        'generacion_anual': round(ahorro_anual, 1),
        'costo_estimado': round(costo_estimado, 0),
        'eficiencia': round(eficiencia_termotanque * factor_radiacion * 100, 1),  # Porcentaje
        'detalle_clima': {
            'radiacion_solar': radiacion_solar,
            'temperatura': temperatura,
            'ubicacion': clima['ubicacion']
        }
    }

def calcular_metricas_ambientales(generacion_anual):
    """
    Calcula métricas ambientales basadas en la generación anual
    
    Args:
        generacion_anual (float): Generación anual en kWh
        
    Returns:
        dict: Métricas ambientales
    """
    # Factores de conversión
    factor_co2 = 0.4  # kg CO2 por kWh (varía según matriz energética)
    factor_arboles = 0.06  # árboles equivalentes por kg CO2 (aproximación)
    
    # Calcular ahorro de CO2
    co2_evitado = generacion_anual * factor_co2
    
    # Calcular árboles equivalentes
    arboles_equivalentes = co2_evitado * factor_arboles
    
    # Calcular kilómetros no recorridos en auto (equivalente)
    # Aproximadamente 0.2 kg CO2 por km en auto promedio
    km_auto_equivalentes = co2_evitado / 0.2
    
    return {
        'co2_evitado': round(co2_evitado, 1),  # kg CO2/año
        'arboles_equivalentes': round(arboles_equivalentes, 1),  # árboles/año
        'km_auto_equivalentes': round(km_auto_equivalentes, 1)  # km/año
    }