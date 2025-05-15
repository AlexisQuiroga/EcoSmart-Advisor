"""
Módulo simplificado para el carrusel de la página principal
que muestra imágenes estáticas y mensajes predefinidos sobre
beneficios económicos de energías renovables.
"""
import os
import json

# Categorías para el carrusel
CAROUSEL_CATEGORIES = [
    "energia_eolica",
    "eficiencia_energetica", 
    "termotanque_solar",
    "energia_solar",
    "energia_termica",
    "futuro_renovables"
]

# Datos predeterminados para cada slide del carrusel con énfasis en los beneficios económicos y ambientales
DEFAULT_CAROUSEL_DATA = {
    "energia_solar": {
        "titulo": "Ahorro con Energía Solar",
        "texto_principal": "La inversión en paneles solares se recupera en un promedio de 4-6 años según la zona geográfica.",
        "dato_destacado": "Reduce hasta un 95% de tu factura eléctrica mensual generando tu propia energía limpia.",
        "color": "primary",
        "imagen_url": "/static/images/carousel/energia_solar.jpg"
    },
    "energia_eolica": {
        "titulo": "Rentabilidad Eólica",
        "texto_principal": "La energía eólica tiene el menor costo de generación entre todas las renovables y continúa bajando.",
        "dato_destacado": "Un hogar con turbina pequeña puede ahorrar entre $200-600 USD mensuales en áreas con buen recurso.",
        "color": "success",
        "imagen_url": "/static/images/carousel/energia_eolica.jpg"
    },
    "termotanque_solar": {
        "titulo": "Beneficio Económico Inmediato",
        "texto_principal": "Los termotanques solares ofrecen el retorno de inversión más rápido entre todas las tecnologías renovables.",
        "dato_destacado": "Reduce hasta 85% el gasto en calentamiento de agua, con amortización en solo 2-3 años.",
        "color": "info",
        "imagen_url": "/static/images/carousel/termotanque_solar.jpg"
    },
    "eficiencia_energetica": {
        "titulo": "Maximiza tu Inversión Verde",
        "texto_principal": "Cada peso invertido en eficiencia energética genera un retorno de hasta 3 veces la inversión inicial.",
        "dato_destacado": "Combinando renovables y eficiencia se puede lograr hasta 50% más ahorro que con renovables solas.",
        "color": "warning",
        "imagen_url": "/static/images/carousel/eficiencia_energetica.jpg"
    },
    "futuro_renovables": {
        "titulo": "Independencia Energética",
        "texto_principal": "Las renovables ofrecen soberanía energética a hogares y empresas, protegiéndolos de aumentos de tarifas.",
        "dato_destacado": "Se prevé que para 2025 las renovables serán hasta 60% más baratas que los combustibles fósiles.",
        "color": "danger",
        "imagen_url": "/static/images/carousel/futuro_renovable.jpg"
    },
    "energia_termica": {
        "titulo": "Valorización Inmobiliaria",
        "texto_principal": "Las propiedades con sistemas de energía renovable aumentan su valor de mercado entre un 4% y 8%.",
        "dato_destacado": "Los edificios con certificación energética se venden un 35% más rápido que propiedades similares.",
        "color": "primary",
        "imagen_url": "/static/images/carousel/energia_termica.jpg"
    }
}

def generar_datos_carrusel():
    """
    Devuelve datos estáticos para el carrusel con textos predefinidos sobre 
    beneficios económicos e imágenes locales.
    
    Returns:
        dict: Datos para el carrusel
    """
    print("Generando datos estáticos para el carrusel")
    
    # Simplemente devolver los datos predefinidos
    return DEFAULT_CAROUSEL_DATA