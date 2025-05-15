#!/usr/bin/env python
"""
Script para probar la API de OpenCage
"""
import os
import requests
from dotenv import load_dotenv

def main():
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener la API key
    api_key = os.environ.get('OPENCAGE_API_KEY')
    if not api_key:
        print("ERROR: No se encontró OPENCAGE_API_KEY en el entorno")
        return
    
    print(f"API Key encontrada: {api_key[:4]}...{api_key[-4:]}")
    
    # Consulta de prueba
    query = "Córdoba, Argentina"
    
    # Construir URL de la API
    url = 'https://api.opencagedata.com/geocode/v1/json'
    params = {
        'q': query,
        'key': api_key,
        'limit': 5,
        'countrycode': 'ar',
        'language': 'es',
        'no_annotations': 1
    }
    
    print(f"Consultando OpenCage para: {query}")
    
    try:
        # Realizar la solicitud a OpenCage
        response = requests.get(url, params=params)
        data = response.json()
        
        # Verificar si hay resultados
        if 'results' in data and len(data['results']) > 0:
            print(f"Resultados encontrados: {len(data['results'])}")
            
            # Mostrar información relevante de cada resultado
            for i, result in enumerate(data['results']):
                print(f"\nResultado {i+1}:")
                print(f"  Dirección: {result['formatted']}")
                print(f"  Coordenadas: {result['geometry']['lat']}, {result['geometry']['lng']}")
                print(f"  Confianza: {result.get('confidence', 'N/A')}")
                
                # Mostrar componentes de dirección si están disponibles
                if 'components' in result:
                    print("  Componentes:")
                    comp = result['components']
                    components = {
                        'Calle': comp.get('road', 'N/A'),
                        'Número': comp.get('house_number', 'N/A'),
                        'Ciudad': comp.get('city', comp.get('town', comp.get('village', 'N/A'))),
                        'Provincia': comp.get('state', 'N/A'),
                        'País': comp.get('country', 'N/A')
                    }
                    for k, v in components.items():
                        print(f"    {k}: {v}")
        else:
            print("No se encontraron resultados")
            print(f"Respuesta completa: {data}")
    
    except Exception as e:
        print(f"Error al procesar solicitud: {str(e)}")

if __name__ == "__main__":
    main()