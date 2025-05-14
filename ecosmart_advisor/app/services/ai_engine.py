"""
Módulo que implementa el motor de IA para recomendaciones avanzadas
y personalización de sugerencias de energía renovable.
Implementa una versión local basada en reglas y lógica sin
dependencia de APIs externas de IA.
"""
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def obtener_recomendacion_ia(datos_usuario, datos_clima, resultados_tecnicos):
    """
    Utiliza un sistema basado en reglas para generar recomendaciones personalizadas
    basadas en los datos del usuario, clima y cálculos técnicos.
    
    Args:
        datos_usuario (dict): Datos proporcionados por el usuario
        datos_clima (dict): Datos climáticos de la ubicación
        resultados_tecnicos (dict): Resultados de los cálculos técnicos
        
    Returns:
        dict: Recomendación personalizada y explicación
    """
    # Utilizamos nuestro sistema basado en reglas para todas las recomendaciones
    return generar_recomendacion_avanzada(datos_usuario, datos_clima, resultados_tecnicos)

def generar_recomendacion_avanzada(datos_usuario, datos_clima, resultados_tecnicos):
    """
    Sistema avanzado basado en reglas que analiza los datos y genera
    recomendaciones personalizadas sin usar APIs externas de IA.
    
    Args:
        datos_usuario (dict): Datos proporcionados por el usuario
        datos_clima (dict): Datos climáticos de la ubicación
        resultados_tecnicos (dict): Resultados de los cálculos técnicos
        
    Returns:
        dict: Recomendación detallada y personalizada
    """
    # Obtener datos relevantes para el análisis
    radiacion_solar = datos_clima.get('radiacion_solar', 0)
    velocidad_viento = datos_clima.get('velocidad_viento', 0)
    temperatura = datos_clima.get('temperatura_promedio', 15)
    objetivo = datos_usuario.get('objetivo', 'equilibrado')
    tipo_vivienda = datos_usuario.get('tipo_vivienda', 'casa_mediana')
    superficie = float(datos_usuario.get('superficie_disponible', 0))
    
    # Mejores opciones basadas en datos climáticos
    mejores_opciones = []
    
    # Verificar condiciones para energía solar
    if radiacion_solar >= 4.0:
        mejores_opciones.append('solar')
    elif radiacion_solar >= 3.0:
        mejores_opciones.append('solar_condiciones')
    
    # Verificar condiciones para energía eólica
    if velocidad_viento >= 4.5:
        mejores_opciones.append('eolica')
    elif velocidad_viento >= 3.5:
        mejores_opciones.append('eolica_condiciones')
    
    # Verificar condiciones para termotanque solar
    if radiacion_solar >= 3.0 and temperatura >= 15:
        mejores_opciones.append('termotanque')
    
    # Si no hay opciones claras, añadir opción por defecto
    if not mejores_opciones:
        if radiacion_solar >= velocidad_viento:
            mejores_opciones.append('solar_basico')
        else:
            mejores_opciones.append('hibrido')
    
    # Determinar recomendación principal basada en el objetivo del usuario
    recomendacion_principal = ""
    justificacion = ""
    ventajas = []
    desventajas = []
    consejos = []
    
    if objetivo == 'ahorro':
        # Priorizar opción con mejor retorno económico
        if 'solar' in mejores_opciones:
            recomendacion_principal = "Sistema solar fotovoltaico"
            justificacion = f"Con una radiación solar de {radiacion_solar} kWh/m²/día en su ubicación, un sistema solar fotovoltaico ofrece el mejor retorno de inversión para su objetivo de maximizar el ahorro económico."
            ventajas = [
                "Excelente relación costo-beneficio a largo plazo",
                "Reducción significativa en su factura eléctrica",
                "Bajo mantenimiento y larga vida útil (25+ años)",
                f"Buenas condiciones de radiación solar en su ubicación ({radiacion_solar} kWh/m²/día)"
            ]
            desventajas = [
                "Inversión inicial considerable",
                "Generación variable dependiendo de las condiciones climáticas",
                "Requiere suficiente espacio en techo o terreno orientado adecuadamente"
            ]
            consejos = [
                "Considere comenzar con un sistema pequeño y escalable",
                "Verifique incentivos fiscales o subsidios disponibles en su región",
                "Implemente medidas de eficiencia energética complementarias para maximizar el ahorro"
            ]
        elif 'eolica' in mejores_opciones:
            recomendacion_principal = "Sistema eólico doméstico"
            justificacion = f"Con una velocidad de viento promedio de {velocidad_viento} m/s en su ubicación, un sistema eólico doméstico ofrece una buena oportunidad de ahorro energético."
            ventajas = [
                "Generación durante el día y la noche",
                "Buen complemento para días nublados",
                f"Buenas condiciones de viento en su ubicación ({velocidad_viento} m/s)",
                "Potencial para alta generación en regiones ventosas"
            ]
            desventajas = [
                "Mayor mantenimiento que los paneles solares",
                "Puede generar ruido y vibraciones",
                "Rendimiento muy variable según la ubicación exacta"
            ]
            consejos = [
                "Considere un estudio de viento local antes de la inversión",
                "Verifique regulaciones locales sobre altura y ruido",
                "Analice la posibilidad de un sistema híbrido solar-eólico para mayor estabilidad"
            ]
        else:
            recomendacion_principal = "Termotanque solar + Sistema fotovoltaico básico"
            justificacion = f"Basado en su objetivo de ahorro y las condiciones climáticas (radiación solar: {radiacion_solar} kWh/m²/día, temperatura: {temperatura}°C), una combinación de termotanque solar para agua caliente y un sistema fotovoltaico básico ofrece el mejor balance costo-beneficio."
            ventajas = [
                "Excelente relación costo-beneficio para agua caliente sanitaria",
                "Complementado con generación eléctrica para otros consumos",
                "Menor inversión inicial que un sistema completo",
                "Rápido retorno de inversión del termotanque solar (3-5 años)"
            ]
            desventajas = [
                "No cubre el 100% de las necesidades energéticas",
                "Requiere espacio para ambos sistemas",
                "Puede requerir sistema de respaldo en días con poca radiación"
            ]
            consejos = [
                "Priorice el dimensionamiento adecuado del termotanque según su consumo de agua caliente",
                "Considere expandir el sistema fotovoltaico progresivamente",
                "Implemente medidas de eficiencia energética en paralelo"
            ]
    
    elif objetivo == 'ambiental':
        # Priorizar opción con mejor impacto ambiental
        if 'solar' in mejores_opciones and 'termotanque' in mejores_opciones:
            recomendacion_principal = "Sistema híbrido integral (fotovoltaico + termotanque solar)"
            justificacion = f"Para maximizar su impacto ambiental positivo, un sistema híbrido que combine energía solar fotovoltaica con termotanque solar aprovecha las buenas condiciones de radiación solar de su ubicación ({radiacion_solar} kWh/m²/día) y reduce su huella de carbono tanto en consumo eléctrico como en calentamiento de agua."
            ventajas = [
                "Máxima reducción de emisiones de CO2",
                "Aprovechamiento integral de la energía solar",
                "Cobertura de necesidades eléctricas y térmicas",
                "Mayor independencia energética"
            ]
            desventajas = [
                "Mayor inversión inicial",
                "Requiere más espacio para la instalación",
                "Mayor complejidad en la instalación y mantenimiento"
            ]
            consejos = [
                "Considere añadir un sistema de baterías para maximizar el autoconsumo",
                "Complemente con medidas de reducción de consumo energético",
                "Considere compartir su experiencia para promover las energías renovables en su comunidad"
            ]
        elif 'eolica' in mejores_opciones:
            recomendacion_principal = "Sistema eólico con almacenamiento"
            justificacion = f"Dadas las buenas condiciones de viento en su ubicación (velocidad promedio: {velocidad_viento} m/s) y su objetivo ambiental, un sistema eólico con almacenamiento de energía ofrece una excelente solución para reducir su huella de carbono."
            ventajas = [
                "Alta reducción de emisiones de CO2",
                "Generación las 24 horas cuando hay viento",
                "Menor impacto visual que grandes instalaciones de paneles",
                "Complementario a otras fuentes renovables"
            ]
            desventajas = [
                "Mayor costo de mantenimiento",
                "Rendimiento variable según condiciones de viento",
                "Las baterías tienen impacto ambiental en su fabricación"
            ]
            consejos = [
                "Investigue aerogeneradores con materiales reciclables",
                "Planifique el reciclaje de componentes al final de su vida útil",
                "Considere complementar con paneles solares para un sistema híbrido"
            ]
        else:
            recomendacion_principal = "Sistema solar fotovoltaico con maximización de capacidad"
            justificacion = f"Para lograr el mayor impacto ambiental positivo en su ubicación, un sistema solar fotovoltaico dimensionado para maximizar la generación aprovechará las condiciones de radiación solar disponibles ({radiacion_solar} kWh/m²/día)."
            ventajas = [
                "Significativa reducción de emisiones de CO2",
                "Tecnología madura y probada",
                "Larga vida útil con mínima degradación",
                "Posibilidad de inyectar excedentes a la red (donde esté disponible)"
            ]
            desventajas = [
                "Generación limitada a horas diurnas",
                "Requiere superficie considerable para maximizar capacidad",
                "Variabilidad estacional en la generación"
            ]
            consejos = [
                "Utilice la máxima superficie disponible para paneles solares",
                "Considere paneles bifaciales para mayor eficiencia",
                "Implemente un sistema de monitoreo para optimizar el desempeño"
            ]
    
    else:  # objetivo equilibrado
        # Buscar balance entre factores
        if 'solar' in mejores_opciones:
            recomendacion_principal = "Sistema solar fotovoltaico balanceado"
            justificacion = f"Un sistema solar fotovoltaico ofrece el mejor equilibrio entre inversión, rendimiento y sostenibilidad para su ubicación, que cuenta con una radiación solar de {radiacion_solar} kWh/m²/día."
            ventajas = [
                "Buen balance entre inversión y retorno económico",
                "Tecnología probada y ampliamente disponible",
                "Escalable según sus necesidades y presupuesto",
                "Bajo mantenimiento y operación silenciosa"
            ]
            desventajas = [
                "Generación limitada a horas con luz solar",
                "Eficiencia afectada por sombras y orientación",
                "Puede requerir complementos para total independencia energética"
            ]
            consejos = [
                "Dimensione el sistema según su consumo promedio",
                "Considere añadir almacenamiento progresivamente",
                "Evalúe su tejado o terreno para la instalación óptima"
            ]
        elif 'eolica' in mejores_opciones:
            recomendacion_principal = "Sistema eólico doméstico adaptado"
            justificacion = f"Considerando su objetivo de equilibrio y las condiciones de viento favorables en su ubicación (velocidad promedio: {velocidad_viento} m/s), un sistema eólico doméstico ofrece una buena combinación de rendimiento e inversión."
            ventajas = [
                "Generación potencial durante 24 horas",
                "Aprovechamiento de un recurso abundante en su zona",
                "Complementario a otras fuentes de energía",
                "Menor superficie requerida que paneles solares"
            ]
            desventajas = [
                "Mayor variabilidad en la generación",
                "Requiere estudios de viento más detallados",
                "Posibles restricciones municipales"
            ]
            consejos = [
                "Comience con un sistema pequeño y evalúe resultados",
                "Instale en el punto más alto y despejado posible",
                "Considere combinar con un pequeño sistema solar"
            ]
        else:
            recomendacion_principal = "Sistema híbrido escalonado"
            justificacion = f"Para lograr un balance óptimo entre inversión, rendimiento y adaptabilidad, un enfoque escalonado que combine inicialmente un termotanque solar y posteriormente un sistema fotovoltaico se adapta mejor a sus condiciones climáticas y objetivos."
            ventajas = [
                "Inversión inicial más accesible",
                "Posibilidad de expandir progresivamente",
                "Combinación de soluciones para distintas necesidades energéticas",
                "Adaptabilidad a cambios en consumo o presupuesto"
            ]
            desventajas = [
                "Implementación más prolongada en el tiempo",
                "Puede requerir modificaciones en etapas posteriores",
                "Menor eficiencia que un sistema diseñado integralmente desde el inicio"
            ]
            consejos = [
                "Comience con un termotanque solar para agua caliente",
                "Planifique la instalación fotovoltaica en una segunda fase",
                "Prepare la infraestructura eléctrica pensando en futuras ampliaciones"
            ]
    
    # Consideraciones especiales según el tipo de vivienda
    consideraciones_especiales = ""
    if tipo_vivienda == 'apartamento':
        consideraciones_especiales = "Al residir en un apartamento, es fundamental verificar las normativas del edificio y contemplar soluciones más compactas. Considere sistemas tipo 'balcón solar' o participar en instalaciones comunitarias si la instalación individual presenta limitaciones."
    elif tipo_vivienda == 'casa_pequena':
        consideraciones_especiales = "Para una casa pequeña, priorice la eficiencia del espacio. Utilice paneles de alta eficiencia y considere soluciones integradas que combinen múltiples funciones en espacios reducidos."
    elif tipo_vivienda == 'comercio':
        consideraciones_especiales = "Los locales comerciales suelen tener alto consumo durante horas diurnas, lo que los hace ideales para aprovechamiento solar directo. Analice la curva de consumo de su negocio para optimizar el dimensionamiento del sistema."
    
    # Armar la respuesta final
    return {
        "recomendacion_principal": recomendacion_principal,
        "justificacion": justificacion,
        "ventajas": ventajas,
        "desventajas": desventajas,
        "consejos_adicionales": consejos,
        "consideraciones_especiales": consideraciones_especiales
    }

def generar_recomendacion_simple(datos_usuario, datos_clima, resultados_tecnicos):
    """
    Genera una recomendación simple basada en reglas para casos de fallback
    
    Args:
        datos_usuario (dict): Datos proporcionados por el usuario
        datos_clima (dict): Datos climáticos de la ubicación
        resultados_tecnicos (dict): Resultados de los cálculos técnicos
        
    Returns:
        dict: Recomendación simplificada
    """
    # Obtener algunos datos clave
    radiacion_solar = datos_clima.get('radiacion_solar', 0)
    velocidad_viento = datos_clima.get('velocidad_viento', 0)
    objetivo = datos_usuario.get('objetivo', 'equilibrado')
    
    # Lógica simple basada en condiciones climáticas
    if radiacion_solar > 4.0 and velocidad_viento < 3.0:
        sistema = "Sistema solar fotovoltaico"
        ventajas = [
            "Alta radiación solar en su ubicación", 
            "Tecnología madura y confiable",
            "Bajo mantenimiento"
        ]
        desventajas = [
            "Producción variable según clima",
            "Requiere espacio en techo o terreno",
            "Inversión inicial considerable"
        ]
    elif velocidad_viento > 4.0 and radiacion_solar < 3.5:
        sistema = "Sistema eólico"
        ventajas = [
            "Buenas condiciones de viento en su ubicación", 
            "Puede generar energía día y noche",
            "Complementa bien otras fuentes en días nublados"
        ]
        desventajas = [
            "Mayor mantenimiento que los paneles solares",
            "Puede generar algo de ruido",
            "Requiere buen despeje y altura"
        ]
    elif radiacion_solar > 3.5 and datos_clima.get('temperatura_promedio', 15) > 18:
        sistema = "Sistema combinado (paneles solares + termotanque solar)"
        ventajas = [
            "Aprovecha el sol para electricidad y agua caliente", 
            "Mayor ahorro combinado",
            "Buena relación costo-beneficio"
        ]
        desventajas = [
            "Mayor complejidad de instalación",
            "Requiere más espacio",
            "Mayor inversión inicial"
        ]
    else:
        sistema = "Sistema solar fotovoltaico básico"
        ventajas = [
            "Solución más universal y adaptable", 
            "Tecnología probada y confiable",
            "Buen punto de inicio en energías renovables"
        ]
        desventajas = [
            "Puede no ser óptimo para su ubicación específica",
            "Considere ampliar el sistema en el futuro",
            "Evalúe complementar con otras tecnologías"
        ]
    
    # Preparar consejos según el objetivo
    if objetivo == 'ahorro':
        consejos = [
            "Priorice la eficiencia energética antes de instalar renovables",
            "Considere financiamiento o incentivos disponibles en su región",
            "Dimensione el sistema para su consumo real para maximizar el retorno"
        ]
    elif objetivo == 'ambiental':
        consejos = [
            "Combine su sistema con medidas de reducción de consumo",
            "Considere baterías para aumentar su autonomía energética",
            "Comparta su experiencia para inspirar a otros en su comunidad"
        ]
    else:
        consejos = [
            "Comience con un sistema básico y expanda según resultados",
            "Monitoree su generación y consumo para optimizar el uso",
            "Consulte sobre incentivos fiscales o programas de apoyo disponibles"
        ]
    
    return {
        "recomendacion_principal": sistema,
        "justificacion": f"Basado en las condiciones climáticas de su ubicación (radiación solar: {radiacion_solar} kWh/m²/día, velocidad del viento: {velocidad_viento} m/s) y su objetivo principal ({objetivo}), recomendamos un {sistema.lower()} como la mejor opción para satisfacer sus necesidades energéticas de manera sostenible.",
        "ventajas": ventajas,
        "desventajas": desventajas,
        "consejos_adicionales": consejos,
        "consideraciones_especiales": "Esta es una recomendación general. Para un análisis más detallado, considere consultar con un instalador local que pueda evaluar factores específicos de su propiedad."
    }

def analizar_combinacion_optima(opciones_viables, consumo_mensual, presupuesto=None):
    """
    Analiza la combinación óptima de sistemas de energía renovable
    
    Args:
        opciones_viables (list): Lista de opciones viables
        consumo_mensual (float): Consumo mensual en kWh
        presupuesto (float, optional): Presupuesto disponible
        
    Returns:
        dict: Combinación óptima recomendada
    """
    # Si no hay opciones viables, no hay combinación posible
    if not opciones_viables:
        return None
    
    # Si solo hay una opción, es la única posible
    if len(opciones_viables) == 1:
        return {
            'sistemas': [opciones_viables[0]['tipo']],
            'cobertura_total': opciones_viables[0]['cobertura'],
            'detalles': [opciones_viables[0]]
        }
    
    # Para cada opción, calcular la relación costo-beneficio
    for opcion in opciones_viables:
        if 'ahorro_anual' in opcion and opcion.get('costo_estimado', 0) > 0:
            opcion['retorno_inversion'] = opcion['costo_estimado'] / opcion['ahorro_anual']
            opcion['costo_beneficio'] = opcion['cobertura'] / opcion['costo_estimado'] * 100
        else:
            opcion['retorno_inversion'] = 99  # Valor alto para indicar que no se puede calcular
            opcion['costo_beneficio'] = 0
    
    # Buscar combinaciones posibles
    mejores_combinaciones = []
    
    # Probar combinación de solar + termotanque si ambos existen
    solar = next((op for op in opciones_viables if op['tipo'] == 'solar'), None)
    termotanque = next((op for op in opciones_viables if op['tipo'] == 'termotanque_solar'), None)
    
    if solar and termotanque:
        costo_combinado = solar.get('costo_estimado', 0) + termotanque.get('costo_estimado', 0)
        
        # Solo considerar si está dentro del presupuesto o no hay presupuesto especificado
        if presupuesto is None or costo_combinado <= presupuesto:
            cobertura_combinada = min(100, solar['cobertura'] + termotanque['cobertura'])
            
            mejores_combinaciones.append({
                'sistemas': ['solar', 'termotanque_solar'],
                'cobertura_total': cobertura_combinada,
                'costo_total': costo_combinado,
                'costo_beneficio': cobertura_combinada / costo_combinado * 100 if costo_combinado > 0 else 0,
                'detalles': [solar, termotanque]
            })
    
    # Probar combinación de eólica + termotanque si ambos existen
    eolica = next((op for op in opciones_viables if op['tipo'] == 'eolica'), None)
    
    if eolica and termotanque:
        costo_combinado = eolica.get('costo_estimado', 0) + termotanque.get('costo_estimado', 0)
        
        # Solo considerar si está dentro del presupuesto
        if presupuesto is None or costo_combinado <= presupuesto:
            cobertura_combinada = min(100, eolica['cobertura'] + termotanque['cobertura'])
            
            mejores_combinaciones.append({
                'sistemas': ['eolica', 'termotanque_solar'],
                'cobertura_total': cobertura_combinada,
                'costo_total': costo_combinado,
                'costo_beneficio': cobertura_combinada / costo_combinado * 100 if costo_combinado > 0 else 0,
                'detalles': [eolica, termotanque]
            })
    
    # También considerar sistemas individuales como opciones
    for opcion in opciones_viables:
        costo = opcion.get('costo_estimado', 0)
        
        # Solo considerar si está dentro del presupuesto
        if presupuesto is None or costo <= presupuesto:
            mejores_combinaciones.append({
                'sistemas': [opcion['tipo']],
                'cobertura_total': opcion['cobertura'],
                'costo_total': costo,
                'costo_beneficio': opcion.get('costo_beneficio', 0),
                'detalles': [opcion]
            })
    
    # Si no hay combinaciones dentro del presupuesto
    if not mejores_combinaciones:
        return None
    
    # Ordenar por cobertura total o por costo-beneficio si hay presupuesto
    if presupuesto:
        mejores_combinaciones.sort(key=lambda x: x['costo_beneficio'], reverse=True)
    else:
        mejores_combinaciones.sort(key=lambda x: x['cobertura_total'], reverse=True)
    
    return mejores_combinaciones[0]