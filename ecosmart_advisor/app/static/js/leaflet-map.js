/**
 * Funciones para manejo del mapa con Leaflet
 */

// Variables globales
let ecosmartMap = null;  // Instancia del mapa
let ecosmartMarker = null;  // Marcador en el mapa
let geocodingInProgress = false; // Evita múltiples solicitudes simultáneas

/**
 * Inicializa el mapa en el contenedor especificado
 * @param {string} containerId - ID del contenedor del mapa
 * @returns {Object} - Instancia del mapa o null si falla
 */
function initMap(containerId) {
    console.log("Inicializando mapa en:", containerId);
    
    try {
        // Verificar que Leaflet esté disponible
        if (typeof L === 'undefined') {
            console.error("Error: La biblioteca Leaflet no está disponible");
            return null;
        }
        
        // Verificar que el contenedor exista
        const container = document.getElementById(containerId);
        if (!container) {
            console.error("Error: No se encontró el contenedor del mapa:", containerId);
            return null;
        }
        
        // Asegurarse de que el contenedor sea visible
        container.style.display = 'block';
        
        // Crear el mapa o usar la instancia existente
        if (!ecosmartMap) {
            console.log("Creando nueva instancia del mapa");
            ecosmartMap = L.map(containerId).setView([-34.603722, -58.381592], 5);
            
            // Añadir capa base de OpenStreetMap
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(ecosmartMap);
        }
        
        // Actualizar tamaño después de que esté visible
        setTimeout(function() {
            ecosmartMap.invalidateSize();
            console.log("Tamaño del mapa actualizado");
        }, 500);
        
        return ecosmartMap;
    } catch (error) {
        console.error("Error al inicializar el mapa:", error);
        return null;
    }
}

/**
 * Añade un evento de clic al mapa para seleccionar ubicación
 * @param {Object} map - Instancia del mapa
 * @param {Function} callback - Función a llamar cuando se hace clic (recibe lat, lng)
 */
function setupMapClickEvent(map, callback) {
    if (!map) {
        console.error("Error: No se puede configurar evento de clic, el mapa no está inicializado");
        return;
    }
    
    map.on('click', function(e) {
        const lat = e.latlng.lat.toFixed(6);
        const lng = e.latlng.lng.toFixed(6);
        
        console.log("Click en el mapa en:", lat, lng);
        
        // Añadir o mover el marcador
        if (ecosmartMarker) {
            ecosmartMarker.setLatLng(e.latlng);
        } else {
            ecosmartMarker = L.marker(e.latlng).addTo(map);
        }
        
        // Llamar al callback con las coordenadas
        if (typeof callback === 'function') {
            callback(lat, lng);
        }
    });
}

/**
 * Muestra u oculta el mapa
 * @param {string} containerId - ID del contenedor del mapa
 * @returns {boolean} - true si el mapa está visible después de la operación
 */
function toggleMap(containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error("Error: No se encontró el contenedor del mapa:", containerId);
        return false;
    }
    
    // Obtener estado actual (computado)
    const computedStyle = window.getComputedStyle(container);
    const isHidden = computedStyle.display === 'none';
    
    console.log("Toggle mapa, estado actual:", isHidden ? "oculto" : "visible");
    
    if (isHidden) {
        container.style.display = 'block';
        console.log("Mostrando mapa");
        
        // Si el mapa ya está inicializado, actualizar su tamaño
        if (ecosmartMap) {
            setTimeout(function() {
                ecosmartMap.invalidateSize();
                console.log("Tamaño del mapa actualizado después de mostrar");
            }, 500);
        }
        
        return true;
    } else {
        container.style.display = 'none';
        console.log("Ocultando mapa");
        return false;
    }
}

/**
 * Realiza geocodificación inversa para obtener dirección a partir de coordenadas
 * @param {string} lat - Latitud
 * @param {string} lng - Longitud
 * @param {Function} callback - Función a llamar con los datos obtenidos
 */
function reverseGeocode(lat, lng, callback) {
    console.log("Realizando geocodificación inversa para:", lat, lng);
    
    if (geocodingInProgress) {
        console.log("Ya hay una solicitud de geocodificación en progreso");
        return;
    }
    
    geocodingInProgress = true;
    
    // Usar Nominatim para la geocodificación inversa
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
        .then(response => response.json())
        .then(data => {
            console.log("Datos de geocodificación recibidos:", data);
            geocodingInProgress = false;
            if (typeof callback === 'function') {
                callback(data);
            }
        })
        .catch(error => {
            console.error("Error en geocodificación inversa:", error);
            geocodingInProgress = false;
            if (typeof callback === 'function') {
                callback(null, error);
            }
        });
}

/**
 * Realiza geocodificación directa para obtener coordenadas a partir de una dirección
 * @param {string} address - Dirección a geocodificar
 * @param {Function} callback - Función a llamar con los datos obtenidos (lat, lng)
 * @param {number} zoomLevel - Nivel de zoom a aplicar (opcional, por defecto 15)
 */
function geocodeAddress(address, callback, zoomLevel = 15) {
    if (!address || address.trim() === '') {
        console.error("La dirección está vacía");
        return;
    }
    
    console.log("Realizando geocodificación para dirección:", address);
    
    if (geocodingInProgress) {
        console.log("Ya hay una solicitud de geocodificación en progreso");
        return;
    }
    
    geocodingInProgress = true;
    
    // Usar Nominatim para geocodificación directa
    const encodedAddress = encodeURIComponent(address);
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodedAddress}&limit=1`)
        .then(response => response.json())
        .then(data => {
            console.log("Datos de geocodificación directa recibidos:", data);
            geocodingInProgress = false;
            
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lng = parseFloat(result.lon);
                
                if (typeof callback === 'function') {
                    callback(lat, lng, result, zoomLevel);
                }
            } else {
                console.warn("No se encontraron resultados para la dirección:", address);
                if (typeof callback === 'function') {
                    callback(null, null, null);
                }
            }
        })
        .catch(error => {
            console.error("Error en geocodificación directa:", error);
            geocodingInProgress = false;
            if (typeof callback === 'function') {
                callback(null, null, error);
            }
        });
}

/**
 * Geocodificación progresiva que se ajusta según la precisión de la información
 * @param {Object} params - Objeto con los parámetros de geocodificación
 * @param {string} params.provincia - Nombre de la provincia/estado
 * @param {string} params.ciudad - Nombre de la ciudad/localidad (opcional)
 * @param {string} params.direccion - Dirección específica (opcional)
 * @param {Function} callback - Función a llamar con los datos obtenidos
 */
function geocodeProgressive(params, callback) {
    const { provincia, ciudad, direccion } = params;
    
    // Verificar si tenemos al menos la provincia
    if (!provincia || provincia.trim() === '') {
        console.error("Se requiere al menos la provincia para la geocodificación progresiva");
        return;
    }
    
    console.log("Iniciando geocodificación progresiva con:", params);
    
    // Determinar qué nivel de precisión tenemos y qué geocodificar
    let query = '';
    let zoomLevel = 7; // Nivel de zoom para provincia
    
    if (direccion && ciudad) {
        // Tenemos dirección específica y ciudad, la consulta más precisa
        query = `${direccion}, ${ciudad}, ${provincia}`;
        zoomLevel = 18; // Zoom cercano para dirección específica
    } else if (ciudad) {
        // Tenemos ciudad pero no dirección específica
        query = `${ciudad}, ${provincia}`;
        zoomLevel = 13; // Zoom medio para la ciudad
    } else {
        // Solo tenemos provincia
        query = provincia;
        zoomLevel = 7; // Zoom lejano para la provincia
    }
    
    // Realizar la geocodificación con el nivel de zoom apropiado
    geocodeAddress(query, function(lat, lng, result, zoom) {
        // Pasar el resultado al callback, con el nivel de zoom apropiado
        if (typeof callback === 'function') {
            callback(lat, lng, result, zoom);
        }
    }, zoomLevel);
}

/**
 * Agrega o actualiza un marcador en el mapa
 * @param {Object} map - Instancia del mapa
 * @param {number} lat - Latitud
 * @param {number} lng - Longitud
 * @param {number} zoom - Nivel de zoom (opcional)
 * @returns {Object} - El marcador creado o actualizado
 */
function addOrUpdateMarker(map, lat, lng, zoom = 15) {
    if (!map) {
        console.error("El mapa no está inicializado");
        return null;
    }
    
    console.log("Agregando/actualizando marcador en:", lat, lng, "con zoom:", zoom);
    
    // Crear o actualizar el marcador
    if (ecosmartMarker) {
        ecosmartMarker.setLatLng([lat, lng]);
    } else {
        ecosmartMarker = L.marker([lat, lng]).addTo(map);
    }
    
    // Centrar el mapa en la ubicación del marcador con el zoom especificado
    map.setView([lat, lng], zoom);
    
    return ecosmartMarker;
}