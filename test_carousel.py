"""
Script para probar la generación de contenido del carrusel
"""
import json
from ecosmart_advisor.app.services.carousel_content import generar_datos_carrusel, buscar_imagen_unsplash

def test_generar_datos_carrusel():
    """Prueba la generación de datos del carrusel"""
    print("Generando datos del carrusel...")
    datos = generar_datos_carrusel()
    
    # Imprimir los datos generados con formato bonito
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    
    # Verificar si hay URLs de imágenes
    for categoria, info in datos.items():
        print(f"\nCategoría: {categoria}")
        print(f"  Título: {info.get('titulo', 'No disponible')}")
        print(f"  Imagen URL: {info.get('imagen_url', 'No disponible')}")

def test_buscar_imagen():
    """Prueba la búsqueda de imágenes con Unsplash"""
    temas = [
        "solar panels energy",
        "wind turbine energy", 
        "solar water heater",
        "energy efficiency home",
        "renewable energy future"
    ]
    
    print("Buscando imágenes en Unsplash...")
    for tema in temas:
        print(f"\nTema: {tema}")
        imagen_url = buscar_imagen_unsplash(tema)
        print(f"  URL: {imagen_url}")

if __name__ == "__main__":
    print("\n=== TEST DE GENERACIÓN DE DATOS DEL CARRUSEL ===\n")
    test_generar_datos_carrusel()
    
    print("\n\n=== TEST DE BÚSQUEDA DE IMÁGENES ===\n")
    test_buscar_imagen()