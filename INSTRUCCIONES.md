# EcoSmart Advisor - Instrucciones de Uso

## Resumen de la aplicación
EcoSmart Advisor es una aplicación inteligente que recomienda sistemas de energía renovable (solar, eólico o termotanque solar) basados en la ubicación, consumo y condiciones climáticas del usuario.

## Características implementadas
- Diagnóstico personalizado basado en datos del usuario
- Análisis de condiciones climáticas mediante APIs externas (Open-Meteo)
- Recomendaciones inteligentes usando modelos de IA (OpenAI)
- Simulador interactivo para evaluar diferentes escenarios
- Chatbot educativo para resolver dudas sobre energías renovables

## Estructura del proyecto
```
/ecosmart_advisor/
├── app/
│   ├── __init__.py         # Inicialización de la app Flask
│   ├── routes.py           # Rutas y endpoints
│   ├── services/
│   │   ├── ai_engine.py    # Motor de IA para recomendaciones
│   │   ├── clima_api.py    # Conexión con APIs climáticas
│   │   ├── energia_calculo.py  # Cálculos de energía
│   │   └── simulador.py    # Simulación de sistemas
│   ├── templates/          # Plantillas HTML
│   └── static/             # Archivos estáticos (CSS, JS)
├── chatbot/
│   └── chatbot.py          # Implementación del chatbot
├── main.py                 # Punto de entrada principal
├── start_app.py            # Script alternativo para iniciar la app
└── .env                    # Variables de entorno
```

## Cómo ejecutar la aplicación
1. Asegúrate de tener todas las dependencias instaladas:
   ```
   pip install flask requests python-dotenv openai
   ```

2. Configura las variables de entorno (opcional):
   - Edita el archivo `.env` para añadir tu API key de OpenAI si deseas usar las funcionalidades de IA avanzadas
   - Puedes agregar otras API keys si deseas usar servicios adicionales

3. Ejecuta la aplicación:
   ```
   python main.py
   ```
   o alternativamente:
   ```
   python start_app.py
   ```

4. Accede a la aplicación en tu navegador:
   - URL local: `http://localhost:5000`
   - En Replit: Usa el botón "Run" para iniciar la aplicación y accede mediante la pestaña de vista web

## Páginas principales
- **Inicio** (`/`): Página principal con información general
- **Diagnóstico** (`/diagnostico/`): Formulario para obtener recomendaciones personalizadas
- **Simulador** (`/simulador/`): Herramienta para simular diferentes configuraciones
- **Chatbot** (`/chatbot/`): Asistente virtual para resolver dudas

## Notas importantes
- La aplicación utiliza datos climáticos reales de APIs externas
- Para recomendaciones avanzadas y chatbot inteligente, se requiere una API key de OpenAI
- Todos los cálculos y estimaciones son aproximados y no sustituyen a un estudio profesional

## Personalización
- Puedes modificar los parámetros de cálculo en los archivos de servicios
- Las plantillas HTML, CSS y JS pueden ser personalizados según necesidades específicas
- La base de conocimiento del chatbot puede ampliarse en `chatbot.py`