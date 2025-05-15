"""
Módulo para interactuar con APIs climáticas y obtener datos relevantes
para las recomendaciones de energía renovable.
"""
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def obtener_datos_clima(ubicacion):
    """
    Obtiene datos climáticos relevantes para la ubicación especificada
    
    Args:
        ubicacion (str): Ciudad o coordenadas del usuario
        
    Returns:
        dict: Datos climáticos relevantes para la evaluación de energía renovable
    """
    # Determinar si se trata de coordenadas (lat,lon) o un nombre de ciudad
    if ',' in ubicacion and len(ubicacion.split(',')) == 2:
        try:
            lat_str, lon_str = ubicacion.strip().split(',')
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            print(f"Procesando ubicación por coordenadas: {lat}, {lon}")
            return obtener_datos_por_coordenadas(lat, lon)
        except ValueError as e:
            print(f"Error al procesar coordenadas '{ubicacion}': {str(e)}")
            # Si no se pueden convertir a float, tratar como ciudad
            return obtener_datos_por_ciudad(ubicacion)
    else:
        print(f"Procesando ubicación por nombre: {ubicacion}")
        return obtener_datos_por_ciudad(ubicacion)

def obtener_datos_por_ciudad(ciudad, provincia=None, pais="Argentina"):
    """
    Obtiene coordenadas de una ciudad usando Nominatim
    y luego obtiene los datos climáticos.
    
    Args:
        ciudad (str): Nombre de la ciudad
        provincia (str, optional): Nombre de la provincia
        pais (str, optional): Nombre del país, default "Argentina"
        
    Returns:
        dict: Datos climáticos para la ubicación
    """
    try:
        # Construir query optimizada para Argentina
        query = f"{ciudad}"
        if provincia:
            query += f", {provincia}"
        if pais:
            query += f", {pais}"
            
        # Usando Nominatim con parámetros optimizados para Argentina
        headers = {
            'User-Agent': 'EcoSmartAdvisor/1.0',
            'Accept-Language': 'es'
        }
        geocoding_url = (
            "https://nominatim.openstreetmap.org/search"
            f"?format=json&q={query}&limit=1&countrycodes=ar"
            "&addressdetails=1&accept-language=es"
        )
        resp = requests.get(geocoding_url, headers=headers, timeout=5)
        data = resp.json()
        
        # Nominatim devuelve una lista de resultados, no un objeto con 'results'
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            lugar = data[0].get('display_name', 'Ubicación')
            return obtener_datos_por_coordenadas(lat, lon, nombre_lugar=lugar)
        else:
            # Si no se encuentra, devolver datos genéricos
            return {
                'radiacion_solar': 4.2,  # kWh/m²/día (valor medio global)
                'velocidad_viento': 3.5,  # m/s (valor medio global)
                'temperatura_promedio': 15,  # °C (valor medio global)
                'ubicacion': ciudad,
                'latitud': None,
                'longitud': None,
                'fuente': 'datos_estimados'
            }
    except Exception as e:
        print(f"Error al obtener coordenadas de {ciudad}: {str(e)}")
        # Devolver valores genéricos en caso de error
        return {
            'radiacion_solar': 4.2,
            'velocidad_viento': 3.5,
            'temperatura_promedio': 15,
            'ubicacion': ciudad,
            'latitud': None,
            'longitud': None,
            'fuente': 'datos_estimados'
        }

def obtener_datos_por_coordenadas(lat, lon, nombre_lugar=None):
    """
    Obtiene datos climáticos para las coordenadas especificadas
    usando la API de Open-Meteo
    
    Args:
        lat (float): Latitud
        lon (float): Longitud
        nombre_lugar (str, optional): Nombre del lugar si se conoce
        
    Returns:
        dict: Datos climáticos para la ubicación
    """
    try:
        print(f"Obteniendo datos para lat={lat}, lon={lon}")
        
        # Obtener datos de clima usando Open-Meteo con clima histórico
        clima_url = (f"https://archive-api.open-meteo.com/v1/archive?"
                     f"latitude={lat}&longitude={lon}"
                     f"&start_date=2022-01-01&end_date=2022-12-31"
                     f"&daily=temperature_2m_mean,windspeed_10m_mean&timezone=auto")
        
        # Obtener datos de radiación solar con forecast API de Open-Meteo
        solar_url = (f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&daily=shortwave_radiation_sum&forecast_days=10&timezone=auto")
        
        print(f"Obteniendo clima de: {clima_url}")
        print(f"Obteniendo radiación de: {solar_url}")
                     
        clima_resp = requests.get(clima_url, timeout=10)
        solar_resp = requests.get(solar_url, timeout=10)
        
        # Verificar respuestas HTTP
        if clima_resp.status_code != 200:
            print(f"Error al obtener datos de clima: {clima_resp.status_code}")
            print(f"Respuesta: {clima_resp.text}")
            raise Exception(f"API de clima devolvió: {clima_resp.status_code}")
            
        if solar_resp.status_code != 200:
            print(f"Error al obtener datos de radiación: {solar_resp.status_code}")
            print(f"Respuesta: {solar_resp.text}")
            raise Exception(f"API de radiación devolvió: {solar_resp.status_code}")
        
        clima_data = clima_resp.json()
        solar_data = solar_resp.json()
        
        # Verificar si los datos contienen la estructura esperada
        print(f"Datos clima: {clima_data.keys() if clima_data else 'Vacío'}")
        print(f"Datos solar: {solar_data.keys() if solar_data else 'Vacío'}")
        
        # Calcular promedios anuales
        if 'daily' in clima_data and 'temperature_2m_mean' in clima_data['daily']:
            temp_promedio = sum(clima_data['daily']['temperature_2m_mean']) / len(clima_data['daily']['temperature_2m_mean'])
            viento_promedio = sum(clima_data['daily']['windspeed_10m_mean']) / len(clima_data['daily']['windspeed_10m_mean'])
            print(f"Datos climáticos calculados - Temp: {temp_promedio}°C, Viento: {viento_promedio}m/s")
        else:
            temp_promedio = 15  # valor por defecto
            viento_promedio = 3.5  # valor por defecto
            print("Usando valores por defecto para temperatura y viento")
            
        # Calcular radiación solar promedio (kWh/m²/día)
        if 'daily' in solar_data and 'shortwave_radiation_sum' in solar_data['daily']:
            # Los datos vienen en MJ/m², los convertimos a kWh/m²/día
            radiacion_valores = solar_data['daily']['shortwave_radiation_sum']
            radiacion_promedio = sum(radiacion_valores) / len(radiacion_valores) / 3.6  # Convertir MJ a kWh
            print(f"Radiación solar calculada: {radiacion_promedio} kWh/m²/día")
        else:
            radiacion_promedio = 4.2  # valor por defecto
            print("Usando valor por defecto para radiación solar")
            
        return {
            'radiacion_solar': round(radiacion_promedio, 2),  # kWh/m²/día
            'velocidad_viento': round(viento_promedio, 1),  # m/s
            'temperatura_promedio': round(temp_promedio, 1),  # °C
            'ubicacion': nombre_lugar or f"{lat}, {lon}",
            'latitud': lat,
            'longitud': lon,
            'fuente': 'open_meteo'
        }
        
    except Exception as e:
        print(f"Error al obtener datos climáticos: {str(e)}")
        # Devolver valores genéricos en caso de error
        return {
            'radiacion_solar': 4.2,
            'velocidad_viento': 3.5,
            'temperatura_promedio': 15,
            'ubicacion': nombre_lugar or f"{lat}, {lon}",
            'latitud': lat,
            'longitud': lon,
            'fuente': 'datos_estimados'
        }