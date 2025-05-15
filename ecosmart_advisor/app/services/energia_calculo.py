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
    # Determinar consumo mensual
    if datos_usuario.get('consumo_mensual'):
        consumo_mensual = float(datos_usuario.get('consumo_mensual'))
    else:
        # Estimar consumo si no fue proporcionado
        tipo_vivienda = datos_usuario.get('tipo_vivienda', 'casa')
        equipos = datos_usuario.get('equipos', [])
        consumo_mensual = calcular_estimacion_sin_kwh(tipo_vivienda, equipos)
        
    # Guardar el consumo mensual en datos_usuario para el análisis de IA
    datos_usuario['consumo_mensual'] = consumo_mensual
    
    # Intentar obtener recomendaciones de IA primero
    try:
        # Consultar al modelo de IA para obtener recomendaciones más precisas
        recomendaciones_ia = evaluar_factores_energia_renovable(datos_usuario, clima)
        
        # Si se obtuvo una respuesta válida de la IA, procesarla
        if recomendaciones_ia and isinstance(recomendaciones_ia, dict):
            # Construir opciones viables basadas en la respuesta de IA
            opciones_viables = []
            
            # Extraer datos relevantes
            superficie = float(datos_usuario.get('superficie_disponible', 50))
            radiacion_solar = clima.get('radiacion_solar', 4.5)
            velocidad_viento = clima.get('velocidad_viento', 3.5)
            temperatura = clima.get('temperatura_promedio', 20)
            objetivo = datos_usuario.get('objetivo', 'cobertura')
            
            # Procesar opción solar si es viable
            if recomendaciones_ia['opciones']['solar']['viable']:
                solar_info = calcular_potencial_solar(
                    radiacion_solar,
                    superficie,
                    temperatura,
                    recomendaciones_ia['opciones']['solar']
                )
                
                eficiencia_estimada = recomendaciones_ia['opciones']['solar']['cobertura_estimada']
                generacion_mensual = solar_info['generacion_mensual']
                
                opciones_viables.append({
                    'tipo': 'solar',
                    'titulo': 'Sistema Solar Fotovoltaico',
                    'descripcion': solar_info['descripcion'],
                    'cobertura': eficiencia_estimada,
                    'generacion_mensual': generacion_mensual,
                    'ahorro_anual': generacion_mensual * 12 * 0.15,  # 0.15 USD/kWh estimado
                    'impacto_ambiental': generacion_mensual * 12 * 0.4,  # 0.4 kg CO2 por kWh
                    'detalle_tecnico': (f"Potencia recomendada: {solar_info['potencia_recomendada']} kWp, "
                                     f"Inclinación: {recomendaciones_ia['opciones']['solar']['inclinacion_paneles']}°, "
                                     f"Orientación: {recomendaciones_ia['opciones']['solar']['orientacion']}"),
                    'detalle': solar_info,
                    'viable': True
                })
            
            # Procesar opción eólica si es viable
            if recomendaciones_ia['opciones']['eolica']['viable']:
                eolica_info = calcular_potencial_eolico(
                    velocidad_viento,
                    superficie,
                    recomendaciones_ia['opciones']['eolica']
                )
                
                eficiencia_estimada = recomendaciones_ia['opciones']['eolica']['cobertura_estimada']
                generacion_mensual = eolica_info['generacion_mensual']
                
                opciones_viables.append({
                    'tipo': 'eolica',
                    'titulo': 'Aerogenerador Doméstico',
                    'descripcion': eolica_info['descripcion'],
                    'cobertura': eficiencia_estimada,
                    'generacion_mensual': generacion_mensual,
                    'ahorro_anual': generacion_mensual * 12 * 0.15,
                    'impacto_ambiental': generacion_mensual * 12 * 0.4,
                    'detalle_tecnico': (f"Potencia recomendada: {recomendaciones_ia['opciones']['eolica']['potencia_recomendada']} kW, "
                                    f"Altura torre: {recomendaciones_ia['opciones']['eolica']['altura_torre']} m"),
                    'detalle': eolica_info,
                    'viable': True
                })
            
            # Procesar opción termotanque si es viable
            if recomendaciones_ia['opciones']['termotanque_solar']['viable']:
                termotanque_info = calcular_potencial_termotanque(
                    radiacion_solar,
                    temperatura,
                    recomendaciones_ia['opciones']['termotanque_solar']
                )
                
                eficiencia_estimada = recomendaciones_ia['opciones']['termotanque_solar']['cobertura_estimada']
                ahorro_mensual = termotanque_info['ahorro_mensual']
                
                opciones_viables.append({
                    'tipo': 'termotanque_solar',
                    'titulo': 'Termotanque Solar',
                    'descripcion': termotanque_info['descripcion'],
                    'cobertura': eficiencia_estimada,
                    'generacion_mensual': ahorro_mensual,
                    'ahorro_anual': ahorro_mensual * 12 * 0.15,
                    'impacto_ambiental': ahorro_mensual * 12 * 0.4,
                    'detalle_tecnico': (f"Capacidad recomendada: {termotanque_info['capacidad_recomendada']} litros, "
                                    f"Inclinación: {recomendaciones_ia['opciones']['termotanque_solar']['inclinacion_optima']}°"),
                    'detalle': termotanque_info,
                    'viable': True
                })
            
            # Si no hay opciones viables, volver al método tradicional
            if not opciones_viables:
                return calcular_recomendacion_tradicional(datos_usuario, clima)
            
            # Ordenar según el objetivo del usuario
            if objetivo == 'ahorro':
                opciones_viables.sort(key=lambda x: x['ahorro_anual'], reverse=True)
            elif objetivo == 'ambiental':
                opciones_viables.sort(key=lambda x: x['impacto_ambiental'], reverse=True)
            else:  # Por defecto, ordenar por cobertura
                opciones_viables.sort(key=lambda x: x['cobertura'], reverse=True)
            
            # Evaluar posibles combinaciones según la IA
            combinaciones = []
            combinacion = recomendaciones_ia.get('combinacion_recomendada', {})
            
            if combinacion and combinacion.get('opciones') and len(combinacion.get('opciones', [])) > 1:
                tipos_combinados = combinacion['opciones']
                tipos_nombres = {
                    'solar': 'Sistema Solar Fotovoltaico',
                    'eolica': 'Aerogenerador',
                    'termotanque_solar': 'Termotanque Solar'
                }
                
                nombres_combinados = [tipos_nombres.get(tipo, tipo) for tipo in tipos_combinados]
                detalle_combinacion = f"{' y '.join(nombres_combinados)} - {combinacion.get('justificacion', '')}"
                
                combinaciones.append({
                    'tipos': tipos_combinados,
                    'cobertura': combinacion.get('cobertura_combinada', 0),
                    'detalle': detalle_combinacion
                })
            
            # Si no hay combinaciones explícitas de la IA pero tenemos múltiples opciones viables,
            # generar combinaciones como en el método tradicional
            if not combinaciones and len(opciones_viables) >= 2:
                # Buscar opciones viables por tipo
                solar_viable = next((op for op in opciones_viables if op['tipo'] == 'solar'), None)
                eolica_viable = next((op for op in opciones_viables if op['tipo'] == 'eolica'), None)
                termotanque_viable = next((op for op in opciones_viables if op['tipo'] == 'termotanque_solar'), None)
                
                # Combinar solar + termotanque
                if solar_viable and termotanque_viable:
                    cobertura_combinada = min(100, solar_viable['cobertura'] + termotanque_viable['cobertura'])
                    combinaciones.append({
                        'tipos': ['solar', 'termotanque_solar'],
                        'cobertura': cobertura_combinada,
                        'detalle': 'Paneles solares para electricidad y termotanque solar para agua caliente'
                    })
                
                # Combinar eólica + termotanque
                if eolica_viable and termotanque_viable:
                    cobertura_combinada = min(100, eolica_viable['cobertura'] + termotanque_viable['cobertura'])
                    combinaciones.append({
                        'tipos': ['eolica', 'termotanque_solar'],
                        'cobertura': cobertura_combinada,
                        'detalle': 'Aerogenerador para electricidad y termotanque solar para agua caliente'
                    })
            
            # Determinar recomendación principal basada en la mejor_opcion de la IA
            mejor_opcion = recomendaciones_ia.get('mejor_opcion', '')
            
            if mejor_opcion == 'combinacion' and combinaciones:
                # Si la IA recomienda una combinación, usar la primera combinación
                principal = {
                    'tipo': 'combinacion',
                    'cobertura': combinaciones[0]['cobertura'],
                    'combinacion': combinaciones[0]
                }
            else:
                # Buscar la mejor opción según la IA, o usar la primera por cobertura
                if mejor_opcion in ['solar', 'eolica', 'termotanque_solar']:
                    principal = next((op for op in opciones_viables if op['tipo'] == mejor_opcion), opciones_viables[0])
                else:
                    principal = opciones_viables[0]
            
            # Preparar la respuesta consolidada
            recomendacion = {
                'mensaje': f"Se identificaron {len(opciones_viables)} opciones viables de energía renovable para tu ubicación.",
                'opciones': opciones_viables,
                'combinaciones': combinaciones,
                'principal': principal,
                'justificacion': recomendaciones_ia.get('justificacion', '')
            }
            
            return recomendacion
    except Exception as e:
        print(f"Error al procesar recomendaciones de IA: {str(e)}")
        # En caso de error, usamos el método tradicional como fallback
    
    # Si llegamos a este punto, usar el método tradicional
    return calcular_recomendacion_tradicional(datos_usuario, clima)


def calcular_recomendacion_tradicional(datos_usuario, clima):
    """
    Método tradicional para calcular recomendaciones cuando falla la IA
    
    Args:
        datos_usuario (dict): Datos proporcionados por el usuario
        clima (dict): Datos climáticos de la ubicación
        
    Returns:
        dict: Recomendación detallada de sistema(s) de energía renovable
    """
    # Extraer datos relevantes
    if datos_usuario.get('consumo_mensual'):
        consumo_mensual = float(datos_usuario.get('consumo_mensual'))
    else:
        # Estimar consumo si no fue proporcionado
        tipo_vivienda = datos_usuario.get('tipo_vivienda', 'casa')
        equipos = datos_usuario.get('equipos', [])
        consumo_mensual = calcular_estimacion_sin_kwh(tipo_vivienda, equipos)
    
    superficie = float(datos_usuario.get('superficie_disponible', 50))
    radiacion_solar = clima.get('radiacion_solar', 4.5)
    velocidad_viento = clima.get('velocidad_viento', 3.5)
    temperatura = clima.get('temperatura_promedio', 20)
    objetivo = datos_usuario.get('objetivo', 'cobertura')
    
    # Calcular potencial para cada tipo de energía
    potencial_solar = calcular_potencial_solar(radiacion_solar, superficie, temperatura)
    potencial_eolico = calcular_potencial_eolico(velocidad_viento, superficie)
    potencial_termotanque = calcular_potencial_termotanque(radiacion_solar, temperatura)
    
    # Calcular qué porcentaje del consumo podría cubrir cada sistema
    cobertura_solar = min(100, (potencial_solar['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_eolica = min(100, (potencial_eolico['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_termotanque = min(100, (potencial_termotanque['ahorro_mensual'] / consumo_mensual) * 100)  # Ya no limitamos al 30%
    
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
            'titulo': 'Sistema Solar Fotovoltaico',
            'descripcion': "Sistema solar fotovoltaico con paneles de alta eficiencia.",
            'cobertura': round(cobertura_solar),
            'generacion_mensual': potencial_solar['generacion_mensual'],
            'ahorro_anual': potencial_solar['generacion_mensual'] * 12 * 0.15,  # 0.15 USD/kWh estimado
            'impacto_ambiental': potencial_solar['generacion_mensual'] * 12 * 0.4,  # 0.4 kg CO2 por kWh
            'detalle_tecnico': f"Potencia recomendada: {potencial_solar['potencia_recomendada']} kWp",
            'detalle': potencial_solar,
            'viable': True
        })
    
    if es_viable_eolica:
        opciones_viables.append({
            'tipo': 'eolica',
            'titulo': 'Aerogenerador Doméstico',
            'descripcion': "Aerogenerador de pequeña escala para generación residencial.",
            'cobertura': round(cobertura_eolica),
            'generacion_mensual': potencial_eolico['generacion_mensual'],
            'ahorro_anual': potencial_eolico['generacion_mensual'] * 12 * 0.15,
            'impacto_ambiental': potencial_eolico['generacion_mensual'] * 12 * 0.4,
            'detalle_tecnico': f"Potencia recomendada: {potencial_eolico['potencia_recomendada']} kW",
            'detalle': potencial_eolico,
            'viable': True
        })
    
    if es_viable_termotanque:
        opciones_viables.append({
            'tipo': 'termotanque_solar',
            'titulo': 'Termotanque Solar',
            'descripcion': "Sistema de calentamiento de agua mediante energía solar.",
            'cobertura': round(cobertura_termotanque),
            'generacion_mensual': potencial_termotanque['ahorro_mensual'],
            'ahorro_anual': potencial_termotanque['ahorro_mensual'] * 12 * 0.15,
            'impacto_ambiental': potencial_termotanque['ahorro_mensual'] * 12 * 0.4,
            'detalle_tecnico': f"Capacidad recomendada: {potencial_termotanque.get('capacidad_recomendada', 200)} litros",
            'detalle': potencial_termotanque,
            'viable': True
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

def calcular_potencial_solar(radiacion_solar, superficie, temperatura, parametros_ia=None):
    """
    Calcula el potencial de generación solar fotovoltaica
    
    Args:
        radiacion_solar (float): kWh/m²/día
        superficie (float): Metros cuadrados disponibles
        temperatura (float): Temperatura promedio anual en °C
        parametros_ia (dict, optional): Parámetros optimizados por IA
        
    Returns:
        dict: Detalles del potencial solar fotovoltaico
    """
    # Usar parámetros de IA si están disponibles, de lo contrario usar valores por defecto
    if parametros_ia and isinstance(parametros_ia, dict):
        # Eficiencia del panel ajustada por IA
        eficiencia_sistema = parametros_ia.get('eficiencia_sistema', 75) / 100  # Convertir de porcentaje a decimal
        
        # Ajustar el factor de utilización según la inclinación y orientación recomendadas
        factor_utilizacion = 0.7  # Base de 70%
        
        # Mejorar el factor de utilización si tenemos recomendaciones específicas
        if 'inclinacion_paneles' in parametros_ia and 'orientacion' in parametros_ia:
            # Un sistema bien optimizado en inclinación y orientación puede mejorar el factor
            factor_utilizacion = 0.85
        
        inclinacion = parametros_ia.get('inclinacion_paneles', 30)
        orientacion = parametros_ia.get('orientacion', 'Norte')
        
        # Descripción técnica con recomendaciones de IA
        descripcion = (f"Sistema solar fotovoltaico con paneles optimizados a {inclinacion}° de inclinación "
                     f"y orientación {orientacion}, con una eficiencia del sistema del {eficiencia_sistema*100:.0f}%.")
    else:
        # Valores por defecto (sistema no optimizado)
        eficiencia_panel = 0.18  # 18% de eficiencia (paneles monocristalinos modernos)
        factor_utilizacion = 0.7  # 70% del espacio disponible
        
        # Factor de pérdida por temperatura
        # Los paneles pierden eficiencia a temperaturas elevadas (aprox. 0.4% por cada °C sobre 25°C)
        factor_temperatura = 1 - max(0, (temperatura - 25) * 0.004)
        
        # Otras pérdidas del sistema (inversores, cables, etc.)
        otras_perdidas = 0.85  # 15% de pérdidas
        
        # Eficiencia del sistema como un todo
        eficiencia_sistema = eficiencia_panel * factor_temperatura * otras_perdidas
        
        # Descripción genérica
        descripcion = "Sistema solar fotovoltaico con paneles monocristalinos de alta eficiencia."
    
    # Superficie utilizable
    superficie_paneles = superficie * factor_utilizacion
    
    # Calcular potencia instalable (kWp)
    potencia_por_m2 = 0.185  # kWp por m² (aproximado para paneles modernos)
    potencia_instalable = superficie_paneles * potencia_por_m2
    
    # Calcular generación mensual
    horas_sol_pico = radiacion_solar  # Las HSP equivalen a la radiación en kWh/m²/día
    generacion_diaria = potencia_instalable * horas_sol_pico * eficiencia_sistema
    generacion_mensual = generacion_diaria * 30  # Aproximado
    
    # Retornar detalles
    resultado = {
        'potencia_recomendada': round(potencia_instalable, 2),  # kWp
        'generacion_diaria': round(generacion_diaria, 1),  # kWh/día
        'generacion_mensual': round(generacion_mensual, 1),  # kWh/mes
        'superficie_paneles': round(superficie_paneles, 1),  # m²
        'cantidad_paneles': round(superficie_paneles / 1.7),  # Asumiendo 1.7m² por panel
        'descripcion': descripcion,
        'viable': True if generacion_mensual > 30 else False  # Viabilidad mínima
    }
    
    return resultado

def calcular_potencial_eolico(velocidad_viento, superficie, parametros_ia=None):
    """
    Calcula el potencial de generación eólica para pequeña escala
    
    Args:
        velocidad_viento (float): Velocidad promedio del viento en m/s
        superficie (float): Metros cuadrados disponibles (usado para estimar limitaciones)
        parametros_ia (dict, optional): Parámetros optimizados por IA
        
    Returns:
        dict: Detalles del potencial eólico
    """
    # Para pequeña escala, el tamaño del aerogenerador depende más de reglamentaciones 
    # y disponibilidad que de la superficie
    
    # Usar recomendaciones de IA si están disponibles
    if parametros_ia and isinstance(parametros_ia, dict):
        # Potencia recomendada por IA
        potencia_recomendada = parametros_ia.get('potencia_recomendada', 2.0)
        
        # Altura de torre recomendada
        altura_torre = parametros_ia.get('altura_torre', 15)
        
        # Factor de mejora basado en la altura de la torre
        # La velocidad del viento aumenta con la altura
        factor_altura = (altura_torre / 10) ** 0.14  # Ley de potencia para perfil de viento
        
        # Velocidad de viento ajustada según altura
        velocidad_ajustada = velocidad_viento * factor_altura
        
        # Descripción técnica con recomendaciones de IA
        descripcion = (f"Aerogenerador de {potencia_recomendada} kW montado a una altura de {altura_torre} metros "
                     f"para aprovechar mejor los vientos de la zona.")
        
        # Determinar factor de viabilidad según velocidad ajustada
        if velocidad_ajustada < 3.0:
            factor_viabilidad = 0.3  # Muy baja viabilidad
        elif velocidad_ajustada < 4.0:
            factor_viabilidad = 0.6  # Baja viabilidad
        elif velocidad_ajustada < 5.0:
            factor_viabilidad = 0.8  # Viabilidad media
        else:
            factor_viabilidad = 1.0  # Alta viabilidad
            
        # Usar potencia recomendada por IA
        potencia_maxima = potencia_recomendada
        
    else:
        # Método tradicional
        
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
        
        # Altura de torre estándar
        altura_torre = 15  # metros
        
        # Velocidad ajustada (estándar)
        velocidad_ajustada = velocidad_viento
        
        # Descripción genérica
        descripcion = f"Aerogenerador doméstico con torre de {altura_torre} metros de altura."
    
    # Calcular generación usando la fórmula de la ley cúbica del viento
    # Para simplificar, usamos una fórmula empírica para aerogeneradores pequeños
    
    # Generación aproximada para un aerogenerador
    if velocidad_ajustada < 2.5:
        generacion_nominal = 0  # Por debajo de la velocidad de arranque
    else:
        # ESTA ES UNA CORRECCIÓN IMPORTANTE: La versión anterior sobreestimaba la generación eólica
        # Usamos un factor más realista (0.1 en lugar de 0.2) y una curva de potencia más conservadora
        generacion_nominal = potencia_maxima * (0.1 * (velocidad_ajustada ** 3) / (11 ** 3))
        generacion_nominal = min(generacion_nominal, potencia_maxima)  # No exceder la potencia máxima
    
    # Factor de capacidad (porcentaje del tiempo que genera a potencia nominal)
    # Ajustamos el factor de capacidad a valores más realistas para pequeños aerogeneradores
    factor_capacidad = 0.15 * factor_viabilidad  # 15% en lugar de 25%
    
    # Generación diaria y mensual
    generacion_diaria = generacion_nominal * 24 * factor_capacidad
    generacion_mensual = generacion_diaria * 30
    
    return {
        'potencia_recomendada': round(potencia_maxima, 2),  # kW
        'generacion_diaria': round(generacion_diaria, 1),  # kWh/día
        'generacion_mensual': round(generacion_mensual, 1),  # kWh/mes
        'factor_viabilidad': round(factor_viabilidad, 2),  # 0-1
        'velocidad_minima': 2.5,  # m/s (velocidad de arranque típica)
        'velocidad_nominal': 11,  # m/s (velocidad a potencia nominal)
        'altura_torre': altura_torre,  # metros
        'descripcion': descripcion,
        'viable': True if generacion_mensual > 30 and velocidad_ajustada >= 2.5 else False
    }

def calcular_potencial_termotanque(radiacion_solar, temperatura, parametros_ia=None):
    """
    Calcula el potencial de ahorro con un termotanque solar
    
    Args:
        radiacion_solar (float): kWh/m²/día
        temperatura (float): Temperatura promedio anual en °C
        parametros_ia (dict, optional): Parámetros optimizados por IA
        
    Returns:
        dict: Detalles del potencial de ahorro con termotanque solar
    """
    # Consumo típico de agua caliente por persona
    consumo_agua_caliente_diario = 50  # litros/persona/día
    personas_promedio = 4  # asumimos una familia típica
    
    # Consumo total de agua caliente
    consumo_total = consumo_agua_caliente_diario * personas_promedio  # litros/día
    
    # Energía necesaria para calentar el agua
    calor_especifico = 0.00116  # kWh/kg°C
    temperatura_deseada = 45  # °C
    energia_necesaria = consumo_total * calor_especifico * (temperatura_deseada - temperatura)
    
    # Usar parámetros de IA si están disponibles
    if parametros_ia and isinstance(parametros_ia, dict):
        # Eficiencia del sistema ajustada por IA
        eficiencia_sistema = parametros_ia.get('eficiencia_sistema', 70) / 100  # Convertir de porcentaje a decimal
        
        # Inclinación óptima
        inclinacion_optima = parametros_ia.get('inclinacion_optima', 35)
        
        # Factor de optimización por inclinación
        # Una inclinación óptima puede mejorar significativamente el rendimiento
        factor_optimizacion = 1.15  # Hasta 15% de mejora con inclinación optimizada
        
        # Capacidad de captura optimizada
        factor_radiacion = min(1.0, radiacion_solar / 3.5) * factor_optimizacion
        
        # Descripción técnica con recomendaciones de IA
        descripcion = (f"Termotanque solar con inclinación optimizada de {inclinacion_optima}° "
                     f"y eficiencia del sistema del {eficiencia_sistema*100:.0f}%, "
                     f"ideal para el clima de la zona.")
    else:
        # Valores por defecto (sistema no optimizado)
        eficiencia_sistema = 0.7  # 70% de eficiencia
        
        # Capacidad de captura (dependiendo de la radiación solar)
        factor_radiacion = min(1.0, radiacion_solar / 4.0)  # Normalizado para una radiación de referencia de 4 kWh/m²/día
        
        # Descripción genérica
        descripcion = "Termotanque solar para calentamiento de agua de uso doméstico."
    
    # Energía aportada por el termotanque solar
    energia_aportada = energia_necesaria * eficiencia_sistema * factor_radiacion
    
    # Convertir a kWh mensuales (equivalente eléctrico)
    ahorro_mensual = energia_aportada * 30
    
    # Calcular capacidad recomendada del termotanque
    capacidad_recomendada = consumo_total * 1.2  # 20% más de la demanda diaria
    
    # Retornar detalles
    resultado = {
        'consumo_agua_caliente': consumo_total,  # litros/día
        'energia_necesaria': round(energia_necesaria, 1),  # kWh/día
        'energia_aportada': round(energia_aportada, 1),  # kWh/día
        'ahorro_mensual': round(ahorro_mensual, 1),  # kWh/mes
        'eficiencia': round(eficiencia_sistema * factor_radiacion, 2),  # eficiencia ajustada
        'capacidad_recomendada': round(capacidad_recomendada),  # litros
        'personas': personas_promedio,
        'descripcion': descripcion,
        'viable': True if ahorro_mensual > 20 else False
    }
    
    return resultado

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