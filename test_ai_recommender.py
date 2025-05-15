"""
Script para probar la integración con Deepseek AI para recomendaciones
"""
import json
from ecosmart_advisor.app.services.ai_recommender import evaluar_factores_energia_renovable

def test_recomendacion_ia():
    """Prueba la función de recomendación con IA"""
    # Datos de prueba
    datos_usuario = {
        "tipo_vivienda": "casa",
        "superficie_disponible": 80,
        "consumo_mensual": 300,
        "objetivo": "ahorro",
        "equipos": ["refrigerador", "computadoras", "iluminacion_led"]
    }
    
    datos_clima = {
        "ubicacion": "Buenos Aires, Argentina",
        "latitud": -34.6037,
        "longitud": -58.3816,
        "radiacion_solar": 5.2,
        "velocidad_viento": 3.8,
        "temperatura_promedio": 18
    }
    
    # Ejecutar recomendación
    print("Consultando a Deepseek AI para recomendaciones...")
    resultado = evaluar_factores_energia_renovable(datos_usuario, datos_clima)
    
    # Mostrar resultado
    print("\nResultado de la recomendación IA:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    return resultado

if __name__ == "__main__":
    test_recomendacion_ia()