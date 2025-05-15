"""
Módulo para interactuar con APIs climáticas y obtener datos relevantes
para las recomendaciones de energía renovable.
"""
import requests
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    logger.info(f"Iniciando obtención de datos climáticos para: '{ubicacion}'")
    
    # Validar que la ubicación sea un string válido
    if not ubicacion or not isinstance(ubicacion, str):
        logger.error(f"Ubicación no válida: {ubicacion}, usando datos por defecto")
        return {
            'radiacion_solar': 4.5,  # kWh/m²/día (valor medio global)
            'velocidad_viento': 4.0,  # m/s (valor medio global)
            'temperatura_promedio': 18,  # °C (valor medio global)
            'ubicacion': 'Ubicación no válida',
            'latitud': None,
            'longitud': None,
            'fuente': 'datos_por_defecto'
        }
    
    try:
        # Determinar si se trata de coordenadas (lat,lon) o un nombre de ciudad
        if ',' in ubicacion and len(ubicacion.split(',')) == 2:
            try:
                lat_str, lon_str = ubicacion.strip().split(',')
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
                
                # Validar rangos de coordenadas
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    logger.error(f"Coordenadas fuera de rango: {lat}, {lon}")
                    lat = max(-90, min(90, lat))  # Limitar a rango válido
                    lon = max(-180, min(180, lon))  # Limitar a rango válido
                
                logger.info(f"Procesando ubicación por coordenadas: {lat}, {lon}")
                return obtener_datos_por_coordenadas(lat, lon)
            except ValueError as e:
                logger.error(f"Error al procesar coordenadas '{ubicacion}': {str(e)}")
                # Si no se pueden convertir a float, tratar como ciudad
                return obtener_datos_por_ciudad(ubicacion)
        else:
            logger.info(f"Procesando ubicación por nombre: {ubicacion}")
            return obtener_datos_por_ciudad(ubicacion)
    except Exception as e:
        import traceback
        logger.error(f"Error general en obtener_datos_clima: {str(e)}")
        logger.error(traceback.format_exc())
        # Retornar datos por defecto en caso de error
        return {
            'radiacion_solar': 4.5,
            'velocidad_viento': 4.0,
            'temperatura_promedio': 18,
            'ubicacion': str(ubicacion) if ubicacion else 'Desconocida',
            'latitud': None,
            'longitud': None,
            'fuente': 'error_datos_por_defecto'
        }

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
                'radiacion_solar': 4.5,  # kWh/m²/día (valor medio global)
                'velocidad_viento': 4.0,  # m/s (valor medio global)
                'temperatura_promedio': 18,  # °C (valor medio global)
                'ubicacion': ciudad,
                'latitud': None,
                'longitud': None,
                'fuente': 'datos_estimados'
            }
    except Exception as e:
        logger.error(f"Error al obtener coordenadas de {ciudad}: {str(e)}")
        # Devolver valores genéricos en caso de error
        return {
            'radiacion_solar': 4.5,
            'velocidad_viento': 4.0,
            'temperatura_promedio': 18,
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
        logger.info(f"Obteniendo datos para lat={lat}, lon={lon}")
        
        # Open-Meteo Forecast API para obtener datos básicos de clima actual
        forecast_url = (f"https://api.open-meteo.com/v1/forecast?"
                       f"latitude={lat}&longitude={lon}"
                       f"&current=temperature_2m,windspeed_10m"
                       f"&daily=shortwave_radiation_sum&timezone=auto")
        
        logger.info(f"Obteniendo datos climáticos de: {forecast_url}")
        
        try:
            forecast_resp = requests.get(forecast_url, timeout=10)
            if forecast_resp.status_code != 200:
                logger.error(f"Error al obtener datos de clima: {forecast_resp.status_code}")
                raise Exception(f"API de clima devolvió código: {forecast_resp.status_code}")
                
            forecast_data = forecast_resp.json()
            logger.info(f"Datos obtenidos: {list(forecast_data.keys()) if forecast_data else 'Vacío'}")
            
            # Obtener temperatura y velocidad del viento actuales
            if 'current' in forecast_data:
                temp_promedio = forecast_data['current'].get('temperature_2m', 18)
                viento_promedio = forecast_data['current'].get('windspeed_10m', 4.0)
                logger.info(f"Temperatura actual: {temp_promedio}°C, Viento: {viento_promedio} m/s")
            else:
                temp_promedio = 18  # valor por defecto
                viento_promedio = 4.0  # valor por defecto
                logger.warning("No se encontraron datos actuales, usando valores por defecto")
                
            # Calcular radiación solar promedio
            radiacion_promedio = 4.5  # valor por defecto
            
            if 'daily' in forecast_data and 'shortwave_radiation_sum' in forecast_data['daily']:
                radiacion_valores = forecast_data['daily']['shortwave_radiation_sum']
                if radiacion_valores and len(radiacion_valores) > 0:
                    # Convertir de MJ/m² a kWh/m²/día
                    radiacion_promedio = sum(radiacion_valores) / len(radiacion_valores) / 3.6
                    logger.info(f"Radiación solar calculada: {radiacion_promedio} kWh/m²/día")
            
            # Ajustar valores basados en latitud
            abs_lat = abs(lat)
            if abs_lat > 60:  # Zonas polares tienen menos radiación
                factor_latitud = max(0.5, 1 - (abs_lat - 60) / 30)
                radiacion_promedio = radiacion_promedio * factor_latitud
                
            if 40 < abs_lat < 60:  # Zonas de vientos más fuertes
                factor_viento = min(1.5, 1 + (abs_lat - 40) / 40)
                viento_promedio = viento_promedio * factor_viento
                
        except Exception as e:
            logger.error(f"Error al procesar datos climáticos: {str(e)}")
            # En caso de error, usamos valores por defecto según la latitud
            abs_lat = abs(lat)
            
            # Ajustar valores por defecto según la latitud
            if abs_lat < 23.5:  # Zonas ecuatoriales
                radiacion_promedio = 5.5
                viento_promedio = 3.0
                temp_promedio = 25
            elif abs_lat < 45:  # Zonas templadas
                radiacion_promedio = 4.5
                viento_promedio = 4.0
                temp_promedio = 18
            elif abs_lat < 66.5:  # Zonas subpolares
                radiacion_promedio = 3.5
                viento_promedio = 5.0
                temp_promedio = 10
            else:  # Zonas polares
                radiacion_promedio = 2.5
                viento_promedio = 6.0
                temp_promedio = 0
                
        # Retornar los datos climáticos obtenidos
        return {
            'radiacion_solar': round(radiacion_promedio, 2),  # kWh/m²/día
            'velocidad_viento': round(viento_promedio, 1),  # m/s
            'temperatura_promedio': round(temp_promedio, 1),  # °C
            'ubicacion': nombre_lugar or f"{lat}, {lon}",
            'latitud': float(lat),
            'longitud': float(lon),
            'fuente': 'open_meteo' if 'forecast_data' in locals() else 'valores_estimados_por_latitud'
        }
            
    except Exception as e:
        logger.error(f"Error general obtener_datos_por_coordenadas: {str(e)}")
        # Valores predeterminados en caso de fallo total
        return {
            'radiacion_solar': 4.2,
            'velocidad_viento': 3.5,
            'temperatura_promedio': 15,
            'ubicacion': nombre_lugar or f"{lat}, {lon}",
            'latitud': float(lat) if lat else None,
            'longitud': float(lon) if lon else None,
            'fuente': 'valores_por_defecto_emergencia'
        }