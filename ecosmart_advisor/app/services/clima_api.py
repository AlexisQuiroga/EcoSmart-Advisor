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
            lat, lon = map(float, ubicacion.strip().split(','))
            return obtener_datos_por_coordenadas(lat, lon)
        except ValueError:
            # Si no se pueden convertir a float, tratar como ciudad
            return obtener_datos_por_ciudad(ubicacion)
    else:
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
        # Construir query para Nominatim
        query = f"{ciudad}"
        if provincia:
            query += f", {provincia}"
        if pais:
            query += f", {pais}"
            
        # Usando Nominatim
        headers = {'User-Agent': 'EcoSmartAdvisor/1.0'}
        geocoding_url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}&limit=1"
        resp = requests.get(geocoding_url, headers=headers)
        data = resp.json()
        
        if 'results' in data and len(data['results']) > 0:
            lat = data['results'][0]['latitude']
            lon = data['results'][0]['longitude']
            lugar = data['results'][0]['name']
            pais = data['results'][0]['country']
            return obtener_datos_por_coordenadas(lat, lon, nombre_lugar=f"{lugar}, {pais}")
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
        # Obtener datos de clima usando Open-Meteo
        clima_url = (f"https://archive-api.open-meteo.com/v1/archive?"
                     f"latitude={lat}&longitude={lon}"
                     f"&start_date=2021-01-01&end_date=2021-12-31"
                     f"&daily=temperature_2m_mean,windspeed_10m_mean&timezone=auto")
        
        # Obtener datos de radiación solar con otro endpoint de Open-Meteo
        solar_url = (f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&daily=shortwave_radiation_sum&timezone=auto")
                     
        clima_resp = requests.get(clima_url)
        solar_resp = requests.get(solar_url)
        
        clima_data = clima_resp.json()
        solar_data = solar_resp.json()
        
        # Calcular promedios anuales
        if 'daily' in clima_data:
            temp_promedio = sum(clima_data['daily']['temperature_2m_mean']) / len(clima_data['daily']['temperature_2m_mean'])
            viento_promedio = sum(clima_data['daily']['windspeed_10m_mean']) / len(clima_data['daily']['windspeed_10m_mean'])
        else:
            temp_promedio = 15  # valor por defecto
            viento_promedio = 3.5  # valor por defecto
            
        # Calcular radiación solar promedio (kWh/m²/día)
        if 'daily' in solar_data and 'shortwave_radiation_sum' in solar_data['daily']:
            # Los datos vienen en W/m², los convertimos a kWh/m²/día
            radiacion_valores = solar_data['daily']['shortwave_radiation_sum']
            radiacion_promedio = sum(radiacion_valores) / len(radiacion_valores) / 1000
        else:
            radiacion_promedio = 4.2  # valor por defecto
            
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