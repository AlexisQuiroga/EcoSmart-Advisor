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
    import logging
    logger = logging.getLogger('simulador')
    logger.setLevel(logging.DEBUG)
    
    try:
        logger.info(f"Iniciando simulación con datos: {datos}")
        
        # Si datos es None o no es un diccionario, usar un diccionario vacío
        if not datos or not isinstance(datos, dict):
            logger.warning(f"Datos inválidos: {datos}, usando valores por defecto")
            datos = {}
        
        # Extraer datos de la simulación con validación
        tipo_instalacion = datos.get('tipo_instalacion')
        
        # Validar tipo de instalación
        tipos_validos = ['solar', 'eolica', 'termotanque_solar']
        if not tipo_instalacion or tipo_instalacion not in tipos_validos:
            logger.warning(f"Tipo de instalación no válido: {tipo_instalacion}, usando solar por defecto")
            tipo_instalacion = 'solar'
        
        # Asegurar que capacidad y consumo sean valores numéricos válidos
        try:
            capacidad_valor = datos.get('capacidad', '')
            capacidad = float(capacidad_valor) if capacidad_valor else 0
            if capacidad <= 0:
                logger.warning(f"Capacidad inválida: {capacidad}, usando valor por defecto")
                # Valores por defecto según tipo de instalación
                if tipo_instalacion == 'termotanque_solar':
                    capacidad = 200.0  # 200 litros por defecto
                else:
                    capacidad = 1.0  # 1 kW por defecto
        except (ValueError, TypeError) as e:
            logger.error(f"Error al convertir capacidad '{datos.get('capacidad')}': {str(e)}")
            if tipo_instalacion == 'termotanque_solar':
                capacidad = 200.0
            else:
                capacidad = 1.0
            
        try:
            consumo_valor = datos.get('consumo_mensual', '')
            consumo_mensual = float(consumo_valor) if consumo_valor else 0
            if consumo_mensual <= 0:
                logger.warning(f"Consumo mensual inválido: {consumo_mensual}, usando valor por defecto")
                consumo_mensual = 300.0  # 300 kWh por defecto
        except (ValueError, TypeError) as e:
            logger.error(f"Error al convertir consumo '{datos.get('consumo_mensual')}': {str(e)}")
            consumo_mensual = 300.0
            
        # Ubicación con validación
        ubicacion_default = '-34.61,-58.38'  # Buenos Aires como ubicación por defecto
        ubicacion = datos.get('ubicacion')
        
        if not ubicacion or not isinstance(ubicacion, str) or ubicacion.strip() == '':
            logger.warning(f"Ubicación inválida: {ubicacion}, usando Buenos Aires por defecto")
            ubicacion = ubicacion_default
            
        descripcion_ubicacion = datos.get('descripcion_ubicacion', 'Buenos Aires, Argentina')
        
        # Registro detallado para debug
        logger.info(f"Simulando instalación de tipo: {tipo_instalacion}")
        logger.info(f"Capacidad: {capacidad} {'kW' if tipo_instalacion != 'termotanque_solar' else 'litros'}")
        logger.info(f"Consumo mensual: {consumo_mensual} kWh")
        logger.info(f"Ubicación: {ubicacion}")
        
        # Obtener datos climáticos
        try:
            clima = obtener_datos_clima(ubicacion)
            logger.info(f"Datos climáticos obtenidos: {clima}")
        except Exception as e:
            logger.error(f"Error al obtener datos climáticos: {str(e)}")
            # Datos climáticos por defecto en caso de error
            clima = {
                'radiacion_solar': 4.5,  # kWh/m²/día
                'velocidad_viento': 4.0,  # m/s
                'temperatura_promedio': 18.0,  # °C
                'ubicacion': descripcion_ubicacion or 'No especificada',
                'latitud': None,
                'longitud': None,
                'fuente': 'datos_por_defecto'
            }
        
        # Simular según el tipo de instalación
        logger.info(f"Iniciando simulación de {tipo_instalacion}")
        if tipo_instalacion == 'solar':
            resultados = simular_solar(capacidad, clima, consumo_mensual)
        elif tipo_instalacion == 'eolica':
            resultados = simular_eolica(capacidad, clima, consumo_mensual)
        elif tipo_instalacion == 'termotanque_solar':
            resultados = simular_termotanque(capacidad, clima, consumo_mensual)
        else:
            logger.error(f"Tipo de instalación no implementado: {tipo_instalacion}")
            return {'error': f'Tipo de instalación no válido: {tipo_instalacion}'}
        
        # Verificar que resultados sea un diccionario
        if not resultados or not isinstance(resultados, dict):
            logger.error(f"Resultados inválidos de simulación: {resultados}")
            return {'error': 'Error en la simulación: resultados inválidos'}
        
        # Verificar que los campos necesarios estén presentes
        campos_necesarios = ['generacion_mensual', 'generacion_anual']
        for campo in campos_necesarios:
            if campo not in resultados:
                logger.error(f"Campo necesario '{campo}' no presente en resultados")
                resultados[campo] = 0  # Valor por defecto
        
        # Agregar métricas ambientales
        try:
            resultados['metricas_ambientales'] = calcular_metricas_ambientales(resultados.get('generacion_anual', 0))
        except Exception as e:
            logger.error(f"Error al calcular métricas ambientales: {str(e)}")
            resultados['metricas_ambientales'] = {
                'co2_evitado': 0,
                'arboles_equivalentes': 0,
                'km_auto_equivalentes': 0
            }
        
        # Agregar datos de cobertura con validación
        try:
            if consumo_mensual > 0 and resultados.get('generacion_mensual', 0) > 0:
                resultados['cobertura'] = min(100, (resultados['generacion_mensual'] / consumo_mensual) * 100)
            else:
                resultados['cobertura'] = 0
        except Exception as e:
            logger.error(f"Error al calcular cobertura: {str(e)}")
            resultados['cobertura'] = 0
        
        # Agregar datos de ahorro económico
        precio_kwh = 0.15  # USD/kWh
        try:
            resultados['ahorro_mensual_usd'] = resultados.get('generacion_mensual', 0) * precio_kwh
            resultados['ahorro_anual_usd'] = resultados.get('generacion_anual', 0) * precio_kwh
        except Exception as e:
            logger.error(f"Error al calcular ahorro económico: {str(e)}")
            resultados['ahorro_mensual_usd'] = 0
            resultados['ahorro_anual_usd'] = 0
        
        # Calcular retorno de inversión
        try:
            costo_estimado = resultados.get('costo_estimado', 0)
            ahorro_anual = resultados.get('ahorro_anual_usd', 0)
            
            if costo_estimado > 0 and ahorro_anual > 0:
                resultados['retorno_inversion_anos'] = costo_estimado / ahorro_anual
            else:
                resultados['retorno_inversion_anos'] = None
        except Exception as e:
            logger.error(f"Error al calcular retorno de inversión: {str(e)}")
            resultados['retorno_inversion_anos'] = None
        
        # Agregar descripción de ubicación a los resultados
        resultados['descripcion_ubicacion'] = descripcion_ubicacion
        
        logger.info(f"Simulación completada con éxito")
        return resultados
        
    except Exception as e:
        logger.critical(f"Error general en simulador: {str(e)}")
        logger.critical(f"Datos de entrada: {datos}")
        import traceback
        logger.critical(traceback.format_exc())
        
        # Crear una respuesta de emergencia para no romper la aplicación
        tipo = datos.get('tipo_instalacion', 'solar') if datos else 'solar'
        return {
            'error': f'Error en la simulación: {str(e)}',
            'tipo': tipo,
            'capacidad_kw': 1.0,
            'generacion_mensual': 0,
            'generacion_anual': 0,
            'costo_estimado': 0,
            'cobertura': 0,
            'ahorro_mensual_usd': 0,
            'ahorro_anual_usd': 0,
            'metricas_ambientales': {
                'co2_evitado': 0,
                'arboles_equivalentes': 0,
                'km_auto_equivalentes': 0
            },
            'descripcion_ubicacion': datos.get('descripcion_ubicacion', '') if datos else ''
        }

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
    import logging
    logger = logging.getLogger('simulador_solar')
    logger.setLevel(logging.DEBUG)
    
    # Validar parámetros de entrada
    logger.info(f"Simulando solar con capacidad={capacidad_kw}kW, consumo={consumo_mensual}kWh")
    logger.info(f"Datos clima: {clima}")
    
    # Extraer radiación solar con valores por defecto seguros
    radiacion_solar = clima.get('radiacion_solar', 4.5)  # kWh/m²/día
    temperatura = clima.get('temperatura_promedio', 18)  # °C
    
    logger.info(f"Radiación solar: {radiacion_solar}, Temperatura: {temperatura}")
    
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
    
    try:
        factor_capacidad = (generacion_anual / (capacidad_kw * 8760) * 100) if capacidad_kw > 0 else 0
    except Exception as e:
        logger.error(f"Error al calcular factor de capacidad: {str(e)}")
        factor_capacidad = 0
    
    try:
        eficiencia_sistema = factor_temperatura * otras_perdidas * 100
    except Exception as e:
        logger.error(f"Error al calcular eficiencia: {str(e)}")
        eficiencia_sistema = 85  # Valor por defecto
    
    # Crear detalle del clima seguro
    detalle_clima = {
        'radiacion_solar': radiacion_solar,
        'temperatura': temperatura,
        'ubicacion': clima.get('ubicacion', 'No especificada')
    }
    
    # Retornar resultados
    resultados = {
        'tipo': 'solar',
        'capacidad_kw': capacidad_kw,
        'superficie_m2': round(superficie_paneles, 1),
        'generacion_diaria': round(generacion_diaria, 1),
        'generacion_mensual': round(generacion_mensual, 1),
        'generacion_anual': round(generacion_anual, 1),
        'costo_estimado': round(costo_estimado, 0),
        'factor_capacidad': round(factor_capacidad, 1),  # Porcentaje
        'eficiencia_sistema': round(eficiencia_sistema, 1),  # Porcentaje
        'detalle_clima': detalle_clima
    }
    
    logger.info(f"Resultados solares generados: {resultados}")
    return resultados

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
    import logging
    logger = logging.getLogger('simulador_eolica')
    logger.setLevel(logging.DEBUG)
    
    # Validar parámetros de entrada
    logger.info(f"Simulando eólica con capacidad={capacidad_kw}kW, consumo={consumo_mensual}kWh")
    logger.info(f"Datos clima para eólica: {clima}")
    
    # Extraer velocidad del viento con valor por defecto seguro
    velocidad_viento = clima.get('velocidad_viento', 4.0)  # m/s
    logger.info(f"Velocidad del viento: {velocidad_viento} m/s")
    
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
    try:
        if velocidad_viento < velocidad_arranque:
            factor_capacidad = 0
        elif velocidad_viento > velocidad_nominal:
            factor_capacidad = 0.35 * factor_viabilidad  # Factor máximo para pequeños aerogeneradores
        else:
            # Interpolación para velocidades entre arranque y nominal
            factor_capacidad = (0.35 * factor_viabilidad) * ((velocidad_viento - velocidad_arranque) / 
                                                        (velocidad_nominal - velocidad_arranque))
    except Exception as e:
        logger.error(f"Error al calcular factor de capacidad eólico: {str(e)}")
        factor_capacidad = 0.15  # Valor conservador por defecto
    
    # Calcular generación
    horas_anuales = 8760  # horas en un año
    try:
        generacion_anual = capacidad_kw * factor_capacidad * horas_anuales
        generacion_mensual = generacion_anual / 12
        generacion_diaria = generacion_mensual / 30
    except Exception as e:
        logger.error(f"Error al calcular generación eólica: {str(e)}")
        # Valores conservadores por defecto
        generacion_anual = capacidad_kw * 0.15 * horas_anuales  # 15% factor de capacidad como fallback
        generacion_mensual = generacion_anual / 12
        generacion_diaria = generacion_mensual / 30
    
    # Estimar costo del sistema
    costo_por_kw = 2000  # USD/kW (varía según país y tecnología)
    costo_estimado = capacidad_kw * costo_por_kw
    
    # Crear detalle de viento seguro
    detalle_viento = {
        'velocidad_viento': velocidad_viento,
        'velocidad_arranque': velocidad_arranque,
        'velocidad_nominal': velocidad_nominal,
        'velocidad_corte': velocidad_corte,
        'ubicacion': clima.get('ubicacion', 'No especificada')
    }
    
    # Retornar resultados
    resultados = {
        'tipo': 'eolica',
        'capacidad_kw': capacidad_kw,
        'generacion_diaria': round(generacion_diaria, 1),
        'generacion_mensual': round(generacion_mensual, 1),
        'generacion_anual': round(generacion_anual, 1),
        'costo_estimado': round(costo_estimado, 0),
        'factor_capacidad': round(factor_capacidad * 100, 1),  # Porcentaje
        'factor_viabilidad': round(factor_viabilidad, 2),
        'detalle_viento': detalle_viento
    }
    
    logger.info(f"Resultados eólicos generados: {resultados}")
    return resultados

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
    import logging
    logger = logging.getLogger('simulador_termotanque')
    logger.setLevel(logging.DEBUG)
    
    # Validar parámetros de entrada
    logger.info(f"Simulando termotanque con capacidad={capacidad_litros}L, consumo={consumo_mensual}kWh")
    logger.info(f"Datos clima para termotanque: {clima}")
    
    # Extraer datos climáticos con valores por defecto seguros
    radiacion_solar = clima.get('radiacion_solar', 4.5)  # kWh/m²/día
    temperatura = clima.get('temperatura_promedio', 18)  # °C
    
    logger.info(f"Radiación solar: {radiacion_solar}, Temperatura: {temperatura}")
    
    try:
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
        
        # Calcular eficiencia total
        eficiencia_total = eficiencia_termotanque * factor_radiacion * 100
    except Exception as e:
        logger.error(f"Error en cálculos del termotanque: {str(e)}")
        # Valores por defecto conservadores en caso de error
        personas_abastecidas = capacidad_litros / 50
        energia_necesaria_diaria = capacidad_litros * 0.05  # Valor aproximado
        energia_aportada_diaria = energia_necesaria_diaria * 0.5  # 50% de eficiencia como fallback
        ahorro_mensual = energia_aportada_diaria * 30
        ahorro_anual = energia_aportada_diaria * 365
        costo_estimado = 800 + capacidad_litros * 2
        eficiencia_total = 50  # 50% como valor por defecto
    
    # Crear detalle del clima seguro
    detalle_clima = {
        'radiacion_solar': radiacion_solar,
        'temperatura': temperatura,
        'ubicacion': clima.get('ubicacion', 'No especificada')
    }
    
    # Retornar resultados
    resultados = {
        'tipo': 'termotanque_solar',
        'capacidad_litros': round(capacidad_litros, 0),
        'personas_abastecidas': round(personas_abastecidas, 1),
        'energia_necesaria_diaria': round(energia_necesaria_diaria, 1),
        'energia_aportada_diaria': round(energia_aportada_diaria, 1),
        'generacion_mensual': round(ahorro_mensual, 1),  # Para compatibilidad con otros tipos
        'generacion_anual': round(ahorro_anual, 1),
        'costo_estimado': round(costo_estimado, 0),
        'eficiencia': round(eficiencia_total, 1),  # Porcentaje
        'detalle_clima': detalle_clima
    }
    
    logger.info(f"Resultados termotanque generados: {resultados}")
    return resultados

def calcular_metricas_ambientales(generacion_anual):
    """
    Calcula métricas ambientales basadas en la generación anual
    
    Args:
        generacion_anual (float): Generación anual en kWh
        
    Returns:
        dict: Métricas ambientales
    """
    import logging
    logger = logging.getLogger('metricas_ambientales')
    logger.setLevel(logging.DEBUG)
    
    logger.info(f"Calculando métricas ambientales para generación anual: {generacion_anual} kWh")
    
    try:
        # Validar entrada
        if generacion_anual is None or not isinstance(generacion_anual, (int, float)) or generacion_anual < 0:
            logger.warning(f"Valor de generación anual inválido: {generacion_anual}, usando valor por defecto")
            generacion_anual = 0
        
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
        
        metricas = {
            'co2_evitado': round(co2_evitado, 1),  # kg CO2/año
            'arboles_equivalentes': round(arboles_equivalentes, 1),  # árboles/año
            'km_auto_equivalentes': round(km_auto_equivalentes, 1)  # km/año
        }
        
        logger.info(f"Métricas calculadas: CO2={co2_evitado}kg, árboles={arboles_equivalentes}, km={km_auto_equivalentes}")
        return metricas
        
    except Exception as e:
        logger.error(f"Error al calcular métricas ambientales: {str(e)}")
        # Retornar valores por defecto seguros
        return {
            'co2_evitado': 0,  # kg CO2/año
            'arboles_equivalentes': 0,  # árboles/año
            'km_auto_equivalentes': 0  # km/año
        }