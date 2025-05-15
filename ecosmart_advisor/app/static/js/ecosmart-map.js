/**
 * EcoSmart Map Module
 * 
 * Módulo centralizado para el manejo de mapas en EcoSmart Advisor.
 * Este módulo proporciona funcionalidades para inicializar y manipular
 * mapas de forma consistente en todas las páginas de la aplicación.
 */

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

// Funciones compatibles con el código existente para mantener compatibilidad
function initMap(containerId, options) {
    return EcoSmart.Map.init(containerId, options);
}

function updateMarker(map, lat, lng, zoom) {
    return EcoSmart.Map.setMarker(map, lat, lng, zoom);
}

function reverseGeocode(lat, lng, callback) {
    return EcoSmart.Map.reverseGeocode(lat, lng, callback);
}

function geocodeProgressive(addressData, callback) {
    return EcoSmart.Map.geocodeProgressive(addressData, callback);
}