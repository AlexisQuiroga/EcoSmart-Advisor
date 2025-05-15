"""
Script para probar la generación de datos del carrusel
"""
import traceback
import json
import os

print("Probando la generación de datos del carrusel...")

# Probar el módulo carousel_content
try:
    from ecosmart_advisor.app.services.carousel_content import generar_datos_carrusel as generar_datos_content
    print("Importado carousel_content correctamente")
    
    print("Intentando generar datos con carousel_content...")
    datos_content = generar_datos_content()
    print(f"Categorías generadas con content: {list(datos_content.keys())}")
    
    # Mostrar algunas claves de ejemplo
    categoria = list(datos_content.keys())[0]
    print(f"Datos para '{categoria}': {list(datos_content[categoria].keys())}")
    print(f"Título: {datos_content[categoria].get('titulo', 'No disponible')}")
    print(f"URL de imagen: {datos_content[categoria].get('imagen_url', 'No disponible')}")
    
except Exception as e:
    print(f"Error en carousel_content: {str(e)}")
    traceback.print_exc()

print("\n" + "-"*50 + "\n")

# Probar el módulo carousel_simple
try:
    from ecosmart_advisor.app.services.carousel_simple import generar_datos_carrusel as generar_datos_simple
    print("Importado carousel_simple correctamente")
    
    print("Intentando generar datos con carousel_simple...")
    datos_simple = generar_datos_simple()
    print(f"Categorías generadas con simple: {list(datos_simple.keys())}")
    
    # Mostrar algunas claves de ejemplo
    categoria = list(datos_simple.keys())[0]
    print(f"Datos para '{categoria}': {list(datos_simple[categoria].keys())}")
    print(f"Título: {datos_simple[categoria].get('titulo', 'No disponible')}")
    print(f"URL de imagen: {datos_simple[categoria].get('imagen_url', 'No disponible')}")
    
except Exception as e:
    print(f"Error en carousel_simple: {str(e)}")
    traceback.print_exc()

print("\nPrueba completada.")