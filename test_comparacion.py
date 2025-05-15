"""
Script para comparar algoritmos originales vs modificados
"""
import json
from ecosmart_advisor.app.services.energia_calculo import (
    calcular_potencial_solar, 
    calcular_potencial_eolico,
    calcular_potencial_termotanque
)

def calcular_eolico_original(velocidad_viento, superficie):
    """Cálculo eólico con fórmula original (sobrestimada)"""
    # Factores determinantes para eólica doméstica:
    if velocidad_viento < 3.0:
        factor_viabilidad = 0.3  # Muy baja viabilidad
    elif velocidad_viento < 4.0:
        factor_viabilidad = 0.6  # Baja viabilidad
    elif velocidad_viento < 5.0:
        factor_viabilidad = 0.8  # Viabilidad media
    else:
        factor_viabilidad = 1.0  # Alta viabilidad
    
    # Tamaño del aerogenerador (para aplicaciones domésticas)
    potencia_maxima = min(3.0, superficie / 30)  # 1kW por cada 10m² como límite aproximado
    
    # Generación aproximada para un aerogenerador con la fórmula ORIGINAL
    if velocidad_viento < 2.5:
        generacion_nominal = 0  # Por debajo de la velocidad de arranque
    else:
        # Versión ORIGINAL sobreestimada
        generacion_nominal = potencia_maxima * (0.2 * (velocidad_viento ** 3) / (11 ** 3))
        generacion_nominal = min(generacion_nominal, potencia_maxima)  # No exceder la potencia máxima
    
    # Factor de capacidad ORIGINAL (25%)
    factor_capacidad = 0.25 * factor_viabilidad
    
    # Generación diaria y mensual
    generacion_diaria = generacion_nominal * 24 * factor_capacidad
    generacion_mensual = generacion_diaria * 30
    
    return {
        'potencia_recomendada': round(potencia_maxima, 2),  # kW
        'generacion_diaria': round(generacion_diaria, 1),  # kWh/día
        'generacion_mensual': round(generacion_mensual, 1),  # kWh/mes
        'factor_viabilidad': round(factor_viabilidad, 2),  # 0-1
        'viable': True,
    }

def calcular_termotanque_limitado(radiacion_solar, temperatura):
    """Cálculo de termotanque con límite de 30% como era originalmente"""
    # Calculamos normal
    termotanque = calcular_potencial_termotanque(radiacion_solar, temperatura)
    return termotanque

def test_comparacion():
    """Comparación de algoritmos de cálculo"""
    print("COMPARACIÓN DE CÁLCULOS ORIGINALES VS CORREGIDOS")
    print("================================================")
    
    # Datos típicos para un usuario en Buenos Aires
    ubicacion = "Buenos Aires, Argentina"
    latitud = -34.6037
    longitud = -58.3816
    radiacion_solar = 5.2  # kWh/m²/día
    velocidad_viento = 3.8  # m/s
    temperatura = 18  # °C
    superficie = 80  # m²
    consumo_mensual = 300  # kWh/mes
    
    print(f"Ubicación: {ubicacion}")
    print(f"Coordenadas: {latitud}, {longitud}")
    print(f"Radiación solar: {radiacion_solar} kWh/m²/día")
    print(f"Velocidad viento: {velocidad_viento} m/s")
    print(f"Temperatura: {temperatura} °C")
    print(f"Superficie: {superficie} m²")
    print(f"Consumo mensual: {consumo_mensual} kWh/mes")
    print("")
    
    # CALCULOS ORIGINALES (que favorecían a la energía eólica)
    print("CÁLCULO ORIGINAL (ANTES):")
    solar_original = calcular_potencial_solar(radiacion_solar, superficie, temperatura)  # No cambió
    eolico_original = calcular_eolico_original(velocidad_viento, superficie)  # Versión sobrestimada
    termotanque_original = calcular_termotanque_limitado(radiacion_solar, temperatura)
    
    # Calcular cobertura con límite del 30% para termotanque
    cobertura_solar_original = min(100, (solar_original['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_eolica_original = min(100, (eolico_original['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_termo_original = min(30, (termotanque_original['ahorro_mensual'] / consumo_mensual) * 100)  # LIMITADO A 30%
    
    print(f"Solar:")
    print(f"  - Generación mensual: {solar_original['generacion_mensual']:.1f} kWh/mes")
    print(f"  - Cobertura: {cobertura_solar_original:.1f}%")
    
    print(f"Eólico (SOBRESTIMADO):")
    print(f"  - Generación mensual: {eolico_original['generacion_mensual']:.1f} kWh/mes")
    print(f"  - Cobertura: {cobertura_eolica_original:.1f}%")
    
    print(f"Termotanque solar (LIMITADO A 30%):")
    print(f"  - Ahorro mensual: {termotanque_original['ahorro_mensual']:.1f} kWh/mes")
    print(f"  - Cobertura: {cobertura_termo_original:.1f}%")
    
    # Determinar mejor recomendación original
    opciones_original = [
        {"tipo": "solar", "cobertura": cobertura_solar_original},
        {"tipo": "eolica", "cobertura": cobertura_eolica_original},
        {"tipo": "termotanque", "cobertura": cobertura_termo_original}
    ]
    opciones_original.sort(key=lambda x: x["cobertura"], reverse=True)
    
    print("\nRecomendación principal ORIGINAL: " + opciones_original[0]["tipo"])
    
    # CALCULOS NUEVOS CORREGIDOS
    print("\n\nCÁLCULO CORREGIDO (AHORA):")
    solar = calcular_potencial_solar(radiacion_solar, superficie, temperatura)
    eolico = calcular_potencial_eolico(velocidad_viento, superficie)
    termotanque = calcular_potencial_termotanque(radiacion_solar, temperatura)
    
    # Calcular cobertura
    cobertura_solar = min(100, (solar['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_eolica = min(100, (eolico['generacion_mensual'] / consumo_mensual) * 100)
    cobertura_termotanque = min(100, (termotanque['ahorro_mensual'] / consumo_mensual) * 100)
    
    print(f"Solar:")
    print(f"  - Generación mensual: {solar['generacion_mensual']:.1f} kWh/mes")
    print(f"  - Cobertura: {cobertura_solar:.1f}%")
    print(f"  - Viable: {solar.get('viable', True)}")
    
    print(f"Eólico (CORREGIDO):")
    print(f"  - Generación mensual: {eolico['generacion_mensual']:.1f} kWh/mes")
    print(f"  - Cobertura: {cobertura_eolica:.1f}%")
    print(f"  - Viable: {eolico.get('viable', False)}")
    
    print(f"Termotanque solar (SIN LÍMITE ARTIFICIAL):")
    print(f"  - Ahorro mensual: {termotanque['ahorro_mensual']:.1f} kWh/mes")
    print(f"  - Cobertura: {cobertura_termotanque:.1f}%")
    print(f"  - Viable: {termotanque.get('viable', True)}")
    
    # Determinar mejor recomendación
    opciones = [
        {"tipo": "solar", "cobertura": cobertura_solar},
        {"tipo": "eolica", "cobertura": cobertura_eolica},
        {"tipo": "termotanque", "cobertura": cobertura_termotanque}
    ]
    opciones.sort(key=lambda x: x["cobertura"], reverse=True)
    
    print("\nRecomendación principal CORREGIDA: " + opciones[0]["tipo"])
    return opciones

if __name__ == "__main__":
    test_comparacion()