"""
Script para probar la visualización de mapas con el módulo centralizado
Proporciona URLs específicas para probar cada pantalla con mapas
"""
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>Prueba de Mapas EcoSmart</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #2e7d32;
                border-bottom: 2px solid #2e7d32;
                padding-bottom: 10px;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin-bottom: 20px;
            }
            a {
                display: inline-block;
                background-color: #2e7d32;
                color: white;
                padding: 10px 15px;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
            }
            a:hover {
                background-color: #1b5e20;
            }
            .description {
                margin-top: 5px;
                color: #555;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Prueba de Mapas EcoSmart</h1>
            <p>Este script permite acceder directamente a las páginas con mapas para verificar su funcionamiento:</p>
            
            <ul>
                <li>
                    <a href="http://localhost:5000/diagnostico">Página de Diagnóstico</a>
                    <div class="description">
                        Prueba el mapa en la página de diagnóstico para seleccionar ubicación.
                    </div>
                </li>
                <li>
                    <a href="http://localhost:5000/simulador">Página de Simulador</a>
                    <div class="description">
                        Prueba el mapa en la página del simulador para seleccionar ubicación.
                    </div>
                </li>
            </ul>
            
            <h2>Pasos para probar:</h2>
            <ol>
                <li>Haz clic en cualquiera de los enlaces anteriores</li>
                <li>Verifica que el mapa se cargue correctamente</li>
                <li>Intenta hacer clic en el mapa para colocar un marcador</li>
                <li>Verifica que se actualicen los campos de ubicación</li>
            </ol>
            
            <p>
                <strong>Nota:</strong> Para que esta prueba funcione, la aplicación EcoSmart Advisor debe estar 
                ejecutándose en el puerto 5000. La aplicación se puede iniciar con el comando <code>python start_app.py</code>.
            </p>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("Iniciando servidor de prueba para mapas...")
    print("Abra http://localhost:8080 en su navegador para ver las opciones.")
    print("Asegúrese de que la aplicación principal esté ejecutándose en el puerto 5000.")
    app.run(host='0.0.0.0', port=8080, debug=True)