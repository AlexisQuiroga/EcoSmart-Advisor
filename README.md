# EcoSmart Advisor

Una aplicación inteligente que asesora a los usuarios sobre qué sistema de energía renovable (solar, eólico o termotanque solar) les conviene instalar, según su ubicación, consumo y condiciones climáticas.

## Características principales

- **Diagnóstico personalizado**: Analiza tu ubicación, consumo eléctrico y preferencias para recomendarte el sistema de energía renovable más adecuado.
- **Análisis climático**: Utiliza datos de radiación solar, velocidad del viento y temperatura de tu ubicación para realizar recomendaciones precisas.
- **Simulador interactivo**: Permite modificar parámetros y visualizar cómo afectan a la generación de energía, ahorro económico e impacto ambiental.
- **Chatbot educativo**: Resuelve tus dudas sobre energías renovables con explicaciones claras y técnicamente precisas.
- **Sistema de recomendación avanzado**: Utiliza algoritmos basados en reglas para personalizar las recomendaciones según tu caso específico.

## Tecnologías utilizadas

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **APIs externas**: Open-Meteo (datos climáticos)
- **Motor de recomendaciones**: Sistema experto basado en reglas (no requiere servicios externos de IA)

## Instalación y configuración

1. Clona el repositorio:
```
git clone https://github.com/tu-usuario/ecosmart-advisor.git
cd ecosmart-advisor
```

2. Crea un entorno virtual e instala las dependencias:
```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configura las variables de entorno (opcional):
   - El archivo `.env` ya está configurado con valores por defecto
   - Puedes modificar las variables según tus necesidades, pero no se requiere configuración adicional para el funcionamiento básico

4. Ejecuta la aplicación:
```
python main.py
```

5. Accede a la aplicación en tu navegador: `http://localhost:5000`

## Estructura del proyecto

```
/ecosmart_advisor/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── services/
│   │   ├── ai_engine.py
│   │   ├── clima_api.py
│   │   ├── energia_calculo.py
│   │   └── simulador.py
│   ├── templates/
│   └── static/
├── chatbot/
│   └── chatbot.py
├── main.py
├── requirements.txt
└── README.md
```

## Uso de la aplicación

1. **Diagnóstico**: Completa el formulario con tu ubicación, tipo de vivienda, consumo y preferencias para recibir una recomendación personalizada.

2. **Simulador**: Selecciona el tipo de sistema renovable, ajusta la capacidad y visualiza los resultados en términos de generación energética, ahorro económico e impacto ambiental.

3. **Chatbot**: Realiza preguntas sobre energías renovables y recibe respuestas educativas adaptadas a tu nivel de conocimiento.

## APIs y servicios externos

- **Open-Meteo**: Proporciona datos climáticos históricos y actuales para cualquier ubicación.

## Autor

- **EcoSmart Team** - Desarrollado para ayudar a promover la adopción de energías renovables

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo `LICENSE` para más detalles.

## Agradecimientos

- [Open-Meteo](https://open-meteo.com/) por proporcionar APIs climáticas gratuitas
- Toda la comunidad de energías renovables por la información y conocimientos compartidos