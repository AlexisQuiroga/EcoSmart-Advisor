"""
Script para probar el módulo central de mapas directamente
"""
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prueba de Módulo Centralizado de Mapas</title>
    
    <!-- Bootstrap y estilos generales -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    
    <!-- Leaflet CSS -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" rel="stylesheet">
    
    <!-- Leaflet JavaScript -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    
    <style>
        body {
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
            font-family: Arial, sans-serif;
        }
        .map-container {
            height: 500px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .info-card {
            margin-bottom: 20px;
            border-radius: 4px;
            padding: 15px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
        }
        .badge-section {
            margin-top: 10px;
        }
        .btn-section {
            margin-top: 15px;
        }
        .heading {
            color: #2e7d32;
            border-bottom: 2px solid #2e7d32;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .coordinate {
            font-family: monospace;
            margin-right: 10px;
        }
        #infoCoordinates {
            font-weight: bold;
        }
        #infoAddress {
            min-height: 60px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="heading">Prueba de Módulo Centralizado de Mapas</h1>
        
        <div class="row">
            <div class="col-md-8">
                <!-- Contenedor del mapa -->
                <div id="mapContainer" class="map-container"></div>
                
                <div class="btn-section">
                    <button id="centerArgentina" class="btn btn-success">
                        <i class="fas fa-map-marker-alt"></i> Centrar en Argentina
                    </button>
                    <button id="toggleCustomMarker" class="btn btn-primary">
                        <i class="fas fa-map-pin"></i> Añadir marcador personalizado
                    </button>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="info-card">
                    <h4><i class="fas fa-info-circle"></i> Información</h4>
                    <p>Esta página prueba el funcionamiento del módulo centralizado de mapas.</p>
                    
                    <h5 class="mt-3"><i class="fas fa-map-marker-alt"></i> Coordenadas</h5>
                    <div id="infoCoordinates">Sin selección</div>
                    
                    <h5 class="mt-3"><i class="fas fa-map"></i> Dirección</h5>
                    <div id="infoAddress" class="alert alert-light">
                        Haga clic en el mapa para ver la dirección
                    </div>
                    
                    <div class="badge-section">
                        <span id="statusBadge" class="badge bg-secondary">
                            <i class="fas fa-circle-notch fa-spin"></i> Inicializando...
                        </span>
                    </div>
                </div>
                
                <div class="info-card">
                    <h4><i class="fas fa-code"></i> Código</h4>
                    <pre class="bg-light p-2" style="font-size: 12px;">
const map = EcoSmart.Map.init('mapContainer');
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;
    
    // Actualizar marcador
    EcoSmart.Map.setMarker(map, lat, lng);
    
    // Geocodificar
    EcoSmart.Map.reverseGeocode(lat, lng, 
        function(data) {
            // Mostrar resultados
        });
});</pre>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Script centralizado para mapas -->
    <script>
        // Namespace para EcoSmart
        window.EcoSmart = window.EcoSmart || {};
        
        // Módulo de mapas
        EcoSmart.Map = (function() {
            // Variables privadas del módulo
            let _currentMarker = null;
            let _mapInstance = null;
        
            /**
             * Inicializa un mapa de Leaflet en el elemento especificado
             * @param {string} containerId - ID del elemento contenedor para el mapa
             * @param {Object} options - Opciones adicionales para la inicialización
             * @returns {Object} Instancia del mapa o null si falla
             */
            function init(containerId, options = {}) {
                try {
                    console.log(`[EcoSmart.Map] Inicializando mapa en ${containerId}...`);
                    const container = document.getElementById(containerId);
                    
                    if (!container) {
                        console.error(`[EcoSmart.Map] No se encontró el contenedor ${containerId}`);
                        return null;
                    }
                    
                    // Si el mapa ya está visible, asegurarse de que sea visible
                    if (container.style.display === 'none') {
                        container.style.display = 'block';
                    }
                    
                    // Asegurarse de que el contenedor tenga una altura mínima
                    if (getComputedStyle(container).height === '0px') {
                        container.style.height = '300px';
                    }
                    
                    // Configuración predeterminada centrada en Argentina
                    const defaultOptions = {
                        center: [-34.603722, -58.381592], // Buenos Aires
                        zoom: 5,
                        zoomControl: true,
                        scrollWheelZoom: true,
                        minZoom: 3
                    };
                    
                    // Combinar opciones predeterminadas con las opciones proporcionadas
                    const mapOptions = { ...defaultOptions, ...options };
                    
                    // Crear el mapa con las opciones combinadas
                    _mapInstance = L.map(containerId, mapOptions);
                    
                    // Añadir capa de mapa base
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        maxZoom: 19
                    }).addTo(_mapInstance);
                    
                    console.log('[EcoSmart.Map] Mapa inicializado correctamente');
                    
                    // Hacer que el mapa sea accesible globalmente para depuración
                    window.ecosmartMap = _mapInstance;
                    
                    return _mapInstance;
                } catch (error) {
                    console.error('[EcoSmart.Map] Error al inicializar el mapa:', error);
                    return null;
                }
            }
            
            /**
             * Coloca o actualiza un marcador en las coordenadas especificadas
             * @param {Object} map - Instancia del mapa de Leaflet
             * @param {number} lat - Latitud
             * @param {number} lng - Longitud
             * @param {number} zoom - Nivel de zoom opcional (predeterminado: 14)
             * @returns {Object} Marcador creado o actualizado
             */
            function setMarker(map, lat, lng, zoom = 14) {
                try {
                    // Validar entradas
                    if (!map || typeof lat !== 'number' || typeof lng !== 'number') {
                        console.error('[EcoSmart.Map] Parámetros inválidos para setMarker:', { map, lat, lng });
                        return null;
                    }
                    
                    // Si ya existe un marcador, eliminarlo
                    if (_currentMarker) {
                        map.removeLayer(_currentMarker);
                    }
                    
                    // Crear un nuevo marcador
                    _currentMarker = L.marker([lat, lng]).addTo(map);
                    
                    // Centrar el mapa en la nueva ubicación
                    map.setView([lat, lng], zoom);
                    
                    console.log('[EcoSmart.Map] Marcador actualizado en:', lat, lng);
                    return _currentMarker;
                } catch (error) {
                    console.error('[EcoSmart.Map] Error al actualizar el marcador:', error);
                    return null;
                }
            }
            
            /**
             * Realiza una geocodificación inversa para obtener información de ubicación
             * @param {number} lat - Latitud
             * @param {number} lng - Longitud
             * @param {function} callback - Función de callback para procesar los resultados
             */
            function reverseGeocode(lat, lng, callback) {
                try {
                    // Validar parámetros
                    if (typeof lat !== 'number' || typeof lng !== 'number' || typeof callback !== 'function') {
                        console.error('[EcoSmart.Map] Parámetros inválidos para reverseGeocode:', { lat, lng });
                        if (typeof callback === 'function') {
                            callback(null);
                        }
                        return;
                    }
                    
                    console.log('[EcoSmart.Map] Iniciando geocodificación inversa para:', lat, lng);
                    
                    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;
                    
                    fetch(url, {
                        headers: {
                            'Accept-Language': 'es',
                            'User-Agent': 'EcoSmartAdvisor/1.0'
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Error HTTP: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('[EcoSmart.Map] Geocodificación inversa exitosa:', data);
                        callback(data);
                    })
                    .catch(error => {
                        console.error('[EcoSmart.Map] Error en geocodificación inversa:', error);
                        callback(null);
                    });
                } catch (error) {
                    console.error('[EcoSmart.Map] Error al realizar geocodificación inversa:', error);
                    callback(null);
                }
            }
            
            /**
             * Función auxiliar para centrar el mapa en Argentina
             * @param {Object} map - Instancia del mapa de Leaflet
             */
            function centerOnArgentina(map) {
                try {
                    if (!map) {
                        map = _mapInstance;
                        if (!map) {
                            console.error('[EcoSmart.Map] No hay mapa inicializado para centrar en Argentina');
                            return;
                        }
                    }
                    
                    map.setView([-34.603722, -58.381592], 5);
                    console.log('[EcoSmart.Map] Mapa centrado en Argentina');
                } catch (error) {
                    console.error('[EcoSmart.Map] Error al centrar mapa en Argentina:', error);
                }
            }
            
            /**
             * Realiza geocodificación progresiva basada en componentes de dirección
             * @param {Object} addressData - Datos de la dirección (pais, provincia, ciudad, dirección)
             * @param {Function} callback - Función a llamar cuando se obtienen las coordenadas
             */
            function geocodeProgressive(addressData, callback) {
                try {
                    const { pais, provincia, ciudad, direccion } = addressData;
                    
                    // Construir la cadena de búsqueda de más específica a menos específica
                    let searchString = '';
                    
                    if (direccion && ciudad && provincia && pais) {
                        // Dirección completa
                        searchString = `${direccion}, ${ciudad}, ${provincia}, ${pais}`;
                    } else if (ciudad && provincia && pais) {
                        // Ciudad
                        searchString = `${ciudad}, ${provincia}, ${pais}`;
                    } else if (provincia && pais) {
                        // Provincia
                        searchString = `${provincia}, ${pais}`;
                    } else if (pais) {
                        // Solo país
                        searchString = pais;
                    }
                    
                    if (!searchString) {
                        console.warn('[EcoSmart.Map] Geocodificación progresiva: datos insuficientes');
                        if (typeof callback === 'function') {
                            callback(null, null, null, 5);
                        }
                        return;
                    }
                    
                    console.log('[EcoSmart.Map] Geocodificación progresiva para:', searchString);
                    
                    // Usar Nominatim para geocodificar
                    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchString)}&addressdetails=1&limit=1`;
                    
                    fetch(url, {
                        headers: {
                            'Accept-Language': 'es',
                            'User-Agent': 'EcoSmartAdvisor/1.0'
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data && data.length > 0) {
                            const result = data[0];
                            const lat = parseFloat(result.lat);
                            const lon = parseFloat(result.lon);
                            
                            // Determinar el nivel de zoom basado en la especificidad de la búsqueda
                            let zoom = 5; // Zoom predeterminado para país
                            
                            if (direccion && ciudad && provincia && pais) {
                                zoom = 17; // Dirección completa
                            } else if (ciudad && provincia && pais) {
                                zoom = 12; // Ciudad
                            } else if (provincia && pais) {
                                zoom = 8; // Provincia
                            }
                            
                            console.log('[EcoSmart.Map] Geocodificación exitosa:', { lat, lon, zoom });
                            if (typeof callback === 'function') {
                                callback(lat, lon, result, zoom);
                            }
                        } else {
                            console.warn('[EcoSmart.Map] No se encontraron resultados para:', searchString);
                            if (typeof callback === 'function') {
                                callback(null, null, null, 5);
                            }
                        }
                    })
                    .catch(error => {
                        console.error('[EcoSmart.Map] Error en geocodificación progresiva:', error);
                        if (typeof callback === 'function') {
                            callback(null, null, null, 5);
                        }
                    });
                } catch (error) {
                    console.error('[EcoSmart.Map] Error en geocodificación progresiva:', error);
                    if (typeof callback === 'function') {
                        callback(null, null, null, 5);
                    }
                }
            }
            
            /**
             * Interfaz pública del módulo
             */
            return {
                init: init,
                setMarker: setMarker,
                reverseGeocode: reverseGeocode,
                centerOnArgentina: centerOnArgentina,
                geocodeProgressive: geocodeProgressive,
                
                // Getters para las variables privadas
                getCurrentMarker: function() { return _currentMarker; },
                getMapInstance: function() { return _mapInstance; }
            };
        })();
    </script>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Elementos de la interfaz
            const infoCoordinates = document.getElementById('infoCoordinates');
            const infoAddress = document.getElementById('infoAddress');
            const statusBadge = document.getElementById('statusBadge');
            const centerArgentinaBtn = document.getElementById('centerArgentina');
            const toggleCustomMarkerBtn = document.getElementById('toggleCustomMarker');
            
            // Inicializar el mapa
            const map = EcoSmart.Map.init('mapContainer');
            
            if (map) {
                // Actualizar estado
                statusBadge.className = 'badge bg-success';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Mapa cargado correctamente';
                
                // Configurar evento de clic en el mapa
                map.on('click', function(e) {
                    const lat = e.latlng.lat;
                    const lng = e.latlng.lng;
                    
                    // Actualizar información de coordenadas
                    infoCoordinates.innerHTML = `
                        <span class="coordinate">Lat: ${lat.toFixed(6)}</span>
                        <span class="coordinate">Lng: ${lng.toFixed(6)}</span>
                    `;
                    
                    // Actualizar marcador
                    const marker = EcoSmart.Map.setMarker(map, lat, lng);
                    
                    // Mostrar mensaje de carga para la dirección
                    infoAddress.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Obteniendo dirección...';
                    infoAddress.className = 'alert alert-info';
                    
                    // Realizar geocodificación inversa
                    EcoSmart.Map.reverseGeocode(lat, lng, function(data) {
                        if (data && data.display_name) {
                            infoAddress.innerHTML = data.display_name;
                            infoAddress.className = 'alert alert-success';
                        } else {
                            infoAddress.innerHTML = 'No se pudo obtener la dirección';
                            infoAddress.className = 'alert alert-warning';
                        }
                    });
                });
                
                // Configurar botón para centrar en Argentina
                if (centerArgentinaBtn) {
                    centerArgentinaBtn.addEventListener('click', function() {
                        EcoSmart.Map.centerOnArgentina(map);
                        infoCoordinates.innerHTML = 'Sin selección';
                        infoAddress.innerHTML = 'Haga clic en el mapa para ver la dirección';
                        infoAddress.className = 'alert alert-light';
                    });
                }
                
                // Configurar botón para añadir marcador personalizado
                if (toggleCustomMarkerBtn) {
                    toggleCustomMarkerBtn.addEventListener('click', function() {
                        // Coordenadas para un punto al azar en Argentina
                        const latRandom = -34.603722 + (Math.random() * 10 - 5);
                        const lngRandom = -58.381592 + (Math.random() * 10 - 5);
                        
                        // Actualizar marcador
                        EcoSmart.Map.setMarker(map, latRandom, lngRandom);
                        
                        // Actualizar información de coordenadas
                        infoCoordinates.innerHTML = `
                            <span class="coordinate">Lat: ${latRandom.toFixed(6)}</span>
                            <span class="coordinate">Lng: ${lngRandom.toFixed(6)}</span>
                        `;
                        
                        // Mostrar mensaje de carga para la dirección
                        infoAddress.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Obteniendo dirección...';
                        infoAddress.className = 'alert alert-info';
                        
                        // Realizar geocodificación inversa
                        EcoSmart.Map.reverseGeocode(latRandom, lngRandom, function(data) {
                            if (data && data.display_name) {
                                infoAddress.innerHTML = data.display_name;
                                infoAddress.className = 'alert alert-success';
                            } else {
                                infoAddress.innerHTML = 'No se pudo obtener la dirección';
                                infoAddress.className = 'alert alert-warning';
                            }
                        });
                    });
                }
            } else {
                // Actualizar estado a error
                statusBadge.className = 'badge bg-danger';
                statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Error al cargar el mapa';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("Iniciando servidor de prueba para el módulo central de mapas...")
    print("Abra http://localhost:5050 en su navegador para ver la prueba.")
    app.run(host='0.0.0.0', port=5050, debug=True)