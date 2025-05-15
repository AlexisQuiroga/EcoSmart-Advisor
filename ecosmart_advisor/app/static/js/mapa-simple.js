/**
 * Script simplificado para la inicialización y manejo del mapa en EcoSmart Advisor
 * Utiliza una implementación más sencilla y confiable para garantizar la compatibilidad
 * con diferentes dispositivos y navegadores.
 */

// Variable global para mantener referencia al marcador actual
let currentMarker = null;

/**
 * Inicializa el mapa de Leaflet en el elemento especificado
 * @param {string} containerId - ID del elemento contenedor para el mapa
 * @returns {Object} Instancia del mapa o null si falla
 */
function initMap(containerId) {
    try {
        console.log(`Inicializando mapa en ${containerId}...`);
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error(`No se encontró el contenedor ${containerId}`);
            return null;
        }
        
        // Crear el mapa centrado en Argentina inicialmente
        const map = L.map(containerId, {
            center: [-34.603722, -58.381592], // Buenos Aires
            zoom: 5,
            zoomControl: true,
            scrollWheelZoom: true
        });
        
        // Añadir capa de mapa base
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
        
        console.log('Mapa inicializado correctamente');
        return map;
    } catch (error) {
        console.error('Error al inicializar el mapa:', error);
        return null;
    }
}

/**
 * Actualiza o crea un marcador en las coordenadas especificadas
 * @param {Object} map - Instancia del mapa
 * @param {number} lat - Latitud
 * @param {number} lng - Longitud
 * @returns {Object} Marcador creado o actualizado
 */
function updateMarker(map, lat, lng) {
    try {
        // Si ya existe un marcador, eliminarlo
        if (currentMarker) {
            map.removeLayer(currentMarker);
        }
        
        // Crear un nuevo marcador
        currentMarker = L.marker([lat, lng]).addTo(map);
        
        // Centrar el mapa en la nueva ubicación
        map.setView([lat, lng], 14);
        
        return currentMarker;
    } catch (error) {
        console.error('Error al actualizar el marcador:', error);
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
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;
        
        fetch(url, {
            headers: {
                'Accept-Language': 'es',
                'User-Agent': 'EcoSmartAdvisor/1.0'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Geocodificación inversa exitosa:', data);
            callback(data);
        })
        .catch(error => {
            console.error('Error en geocodificación inversa:', error);
            callback(null);
        });
    } catch (error) {
        console.error('Error al realizar geocodificación inversa:', error);
        callback(null);
    }
}