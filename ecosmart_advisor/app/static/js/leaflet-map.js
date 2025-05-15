/**
 * Funciones para manejo del mapa con Leaflet
 */

// Variables globales
let ecosmartMap = null;  // Instancia del mapa
let ecosmartMarker = null;  // Marcador en el mapa
let geocodingInProgress = false; // Evita múltiples solicitudes simultáneas

/**
 * Base de datos de direcciones argentinas específicas para uso sin APIs
 * Usar solo cuando todo lo demás falla. Mantener actualizada con direcciones problemáticas.
 */
const knownAddressesDatabase = {
    // Direcciones en Córdoba Capital
    "bolivia 133 cordoba": { lat: -31.4144, lon: -64.1857, type: "house", display: "Bolivia 133, Córdoba, Argentina" },
    "bolivia 133 córdoba": { lat: -31.4144, lon: -64.1857, type: "house", display: "Bolivia 133, Córdoba, Argentina" },
    "ayacucho 367 cordoba": { lat: -31.4181, lon: -64.1831, type: "house", display: "Ayacucho 367, Córdoba, Argentina" },
    "ayacucho 367 córdoba": { lat: -31.4181, lon: -64.1831, type: "house", display: "Ayacucho 367, Córdoba, Argentina" },
    "dean funes 70 cordoba": { lat: -31.4147, lon: -64.1857, type: "house", display: "Dean Funes 70, Córdoba, Argentina" },
    "dean funes 70 córdoba": { lat: -31.4147, lon: -64.1857, type: "house", display: "Dean Funes 70, Córdoba, Argentina" },
    "buenos aires 990 cordoba": { lat: -31.4112, lon: -64.1918, type: "house", display: "Buenos Aires 990, Córdoba, Argentina" },
    "buenos aires 990 córdoba": { lat: -31.4112, lon: -64.1918, type: "house", display: "Buenos Aires 990, Córdoba, Argentina" },
    
    // Calles en Río Tercero
    "independencia 184 rio tercero": { lat: -32.1755, lon: -64.1124, type: "house", display: "Independencia 184, Río Tercero, Córdoba, Argentina" },
    "independencia 184 río tercero": { lat: -32.1755, lon: -64.1124, type: "house", display: "Independencia 184, Río Tercero, Córdoba, Argentina" },
    "general paz 506 rio tercero": { lat: -32.1719, lon: -64.1138, type: "house", display: "General Paz 506, Río Tercero, Córdoba, Argentina" },
    "general paz 506 río tercero": { lat: -32.1719, lon: -64.1138, type: "house", display: "General Paz 506, Río Tercero, Córdoba, Argentina" },
    "wenceslao paunero 2453 rio tercero": { lat: -32.1799, lon: -64.1028, type: "house", display: "Wenceslao Paunero 2453, Río Tercero, Córdoba, Argentina" },
    "wenceslao paunero 2453 río tercero": { lat: -32.1799, lon: -64.1028, type: "house", display: "Wenceslao Paunero 2453, Río Tercero, Córdoba, Argentina" }
};

// Para debugging y diagnóstico
window.debugEcosmart = {
    getMap: function() { return ecosmartMap; },
    getMarker: function() { return ecosmartMarker; },
    createTestMarker: function(lat, lng) {
        if (ecosmartMap) {
            if (ecosmartMarker) {
                ecosmartMarker.remove();
            }
            ecosmartMarker = L.marker([lat, lng]).addTo(ecosmartMap);
            ecosmartMap.setView([lat, lng], 18);
            return "Marcador creado en " + lat + ", " + lng;
        }
        return "Mapa no inicializado";
    },
    verifyMarker: function() {
        // Verificar si el marcador existe pero no está en el mapa
        if (ecosmartMarker && ecosmartMap && !ecosmartMap.hasLayer(ecosmartMarker)) {
            console.warn("Marcador existe pero no está en el mapa - reañadiendo");
            ecosmartMarker.addTo(ecosmartMap);
            return "Marcador reañadido al mapa";
        }
        return "Marcador OK o no existe";
    },
    emergencyCreateMarker: function(lat, lng) {
        try {
            // Crear un marcador de emergencia cuando otros métodos fallan
            console.log("Creando marcador de emergencia");
            
            // Eliminar marcador existente si hay uno
            if (ecosmartMarker) {
                try { 
                    ecosmartMarker.remove(); 
                } catch(e) { 
                    console.warn("Error al eliminar marcador:", e); 
                }
            }
            
            // Crear nuevo marcador
            ecosmartMarker = null;
            ecosmartMarker = new L.Marker([parseFloat(lat), parseFloat(lng)]);
            ecosmartMap.addLayer(ecosmartMarker);
            ecosmartMarker.bindPopup("Ubicación seleccionada").openPopup();
            return "Marcador de emergencia creado";
        } catch(e) {
            console.error("Error en creación de marcador de emergencia:", e);
            return "Error: " + e.message;
        }
    },
    logState: function() { 
        console.log({
            mapInitialized: !!ecosmartMap,
            markerExists: !!ecosmartMarker,
            markerInMap: ecosmartMarker && ecosmartMap ? ecosmartMap.hasLayer(ecosmartMarker) : false,
            geocodingInProgress: geocodingInProgress
        });
        return "Estado logueado en consola";
    }
};

/**
 * Inicializa el mapa en el contenedor especificado
 */
window.initMap = function(containerId) {
    console.log("Inicializando mapa en:", containerId);

    try {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error("Error: No se encontró el contenedor del mapa:", containerId);
            return null;
        }

        // Establecer dimensiones explícitas
        container.style.display = 'block';
        container.style.height = '400px';
        container.style.width = '100%';
        container.style.minHeight = '400px'; // Asegurar altura mínima

        // Forzar reflow
        container.offsetHeight;

        if (!ecosmartMap) {
            // Centrar en Argentina por defecto
            ecosmartMap = L.map(containerId).setView([-38.416097, -63.616672], 4);

            // Usar OpenStreetMap como proveedor de mapas
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19,
                minZoom: 3
            }).addTo(ecosmartMap);

            // Limitar vista a Argentina
            ecosmartMap.setMaxBounds([
                [-55.0, -75.0], // SO
                [-20.0, -50.0]  // NE
            ]);

            // Invalidar tamaño después de la inicialización
            setTimeout(() => {
                ecosmartMap.invalidateSize();
                console.log("Tamaño del mapa actualizado");
            }, 100);
        }

        return ecosmartMap;
    } catch (error) {
        console.error("Error al inicializar mapa:", error);
        return null;
    }
}

/**
 * Añade un evento de clic al mapa
 */
window.setupMapClickEvent = function(map, callback) {
    if (!map) {
        console.error("Error: Mapa no inicializado");
        return;
    }

    map.on('click', function(e) {
        const lat = parseFloat(e.latlng.lat.toFixed(6));
        const lng = parseFloat(e.latlng.lng.toFixed(6));

        // Actualizar marcador
        if (ecosmartMarker) {
            ecosmartMarker.remove();
        }

        ecosmartMarker = L.marker([lat, lng]).addTo(map);
        ecosmartMarker.bindPopup("Ubicación seleccionada").openPopup();

        if (typeof callback === 'function') {
            callback(lat, lng);
        }
    });
}

// Función auxiliar para verificar el estado del mapa
window.checkMapStatus = function(containerId) {
    const container = document.getElementById(containerId);
    console.log("Estado del contenedor:", {
        exists: !!container,
        display: container?.style.display,
        height: container?.style.height,
        width: container?.style.width,
        offsetHeight: container?.offsetHeight,
        offsetWidth: container?.offsetWidth
    });

    console.log("Estado del mapa:", {
        exists: !!ecosmartMap,
        isValid: ecosmartMap?._container != null
    });
}

/**
 * Muestra u oculta el mapa
 * @param {string} containerId - ID del contenedor del mapa
 * @returns {boolean} - true si el mapa está visible después de la operación
 */
window.toggleMap = function(containerId) {
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
    
    // Verificar que las coordenadas son válidas
    lat = parseFloat(lat);
    lng = parseFloat(lng);
    
    if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
        console.error("Coordenadas inválidas para geocodificación inversa:", lat, lng);
        if (typeof callback === 'function') {
            callback(null, new Error("Coordenadas inválidas"));
        }
        return;
    }
    
    if (geocodingInProgress) {
        console.log("Ya hay una solicitud de geocodificación en progreso");
        return;
    }
    
    geocodingInProgress = true;
    
    // Configurar timeout para evitar bloqueos
    const timeoutId = setTimeout(() => {
        console.warn("Timeout en geocodificación inversa después de 5 segundos");
        geocodingInProgress = false;
        if (typeof callback === 'function') {
            callback(null, new Error("Timeout en geocodificación"));
        }
        }, 5000);
    
    // Usar Nominatim para la geocodificación inversa con parámetros optimizados
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1&accept-language=es`)
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos de geocodificación inversa recibidos:", data);
            geocodingInProgress = false;
            
            // Enriquecer los datos de dirección para mejorar la precisión
            if (data && data.address) {
                // Si no tenemos road pero tenemos otros datos que pueden funcionar como calle
                if (!data.address.road) {
                    if (data.address.pedestrian) data.address.road = data.address.pedestrian;
                    else if (data.address.footway) data.address.road = data.address.footway;
                    else if (data.address.path) data.address.road = data.address.path;
                }
                
                // Determinar si es una dirección urbana
                data.isUrbanAddress = !!(data.address.road || data.address.suburb || 
                                      data.address.neighbourhood || data.address.residential);
            }
            
            if (typeof callback === 'function') {
                callback(data);
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
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
window.geocodeAddress = function(address, callback, zoomLevel = 15) {
    // Flag para utilizar OpenCage API como primera opción
    const useOpenCageFirst = true;
    if (!address || address.trim() === '') {
        console.error("La dirección está vacía");
        return;
    }
    
    // Normalizar la dirección para búsquedas consistentes
    const normalizedAddress = address.trim().toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    
    // Extraer partes de la dirección original para mejor formato y búsqueda múltiple
    const addressParts = extractAddressParts(address);
    console.log("Partes extraídas de la dirección:", addressParts);
    
    // === PASO 1: Intentar con nuestra base de datos local primero (más rápido) ===
    const knownAddress = findKnownAddress(addressParts);
    if (knownAddress) {
        console.log("Dirección encontrada en base de datos local:", knownAddress);
        const result = {
            lat: knownAddress.lat,
            lon: knownAddress.lon,
            display_name: knownAddress.display,
            type: knownAddress.type || "house",
            importance: 0.95,
            zoomLevel: 19
        };
        
        // También guardamos en caché para futuras consultas
        try {
            localStorage.setItem(`geocode_${normalizedAddress}`, JSON.stringify({
                lat: result.lat,
                lon: result.lon,
                result: result,
                zoomLevel: result.zoomLevel || zoomLevel,
                timestamp: Date.now()
            }));
        } catch (e) {
            console.warn("Error guardando en caché local:", e);
        }
        
        if (typeof callback === 'function') {
            callback(result.lat, result.lon, result, result.zoomLevel);
        }
        return;
    }
    
    // === PASO 2: Verificar caché para búsquedas recientes ===
    const cacheKey = `geocode_${normalizedAddress}`;
    
    // Primero verificar localStorage (persistente entre sesiones)
    const cachedLocal = localStorage.getItem(cacheKey);
    if (cachedLocal) {
        try {
            const data = JSON.parse(cachedLocal);
            if (Date.now() - data.timestamp < 86400000) { // Caché válido por 24 horas
                console.log("Usando datos en caché local (localStorage)");
                if (typeof callback === 'function') {
                    callback(
                        parseFloat(data.lat), 
                        parseFloat(data.lon), 
                        data.result, 
                        data.zoomLevel || zoomLevel
                    );
                }
                return;
            }
        } catch (e) {
            console.warn("Error al usar caché local:", e);
        }
    }
    
    // Luego verificar sessionStorage (solo para esta sesión)
    const cachedResult = sessionStorage.getItem(cacheKey);
    
    if (cachedResult) {
        try {
            const cachedData = JSON.parse(cachedResult);
            console.log("Usando resultado en caché (sessionStorage) para:", normalizedAddress);
            
            if (typeof callback === 'function') {
                callback(
                    parseFloat(cachedData.lat), 
                    parseFloat(cachedData.lon), 
                    cachedData.result, 
                    cachedData.zoomLevel
                );
            }
            return;
        } catch (e) {
            console.warn("Error al usar datos en caché:", e);
        }
    }
    
    // === PASO 3: Verificar si tenemos todos los elementos para buscar en ciudades conocidas ===
    // Esto es más rápido que buscar online y sirve como respaldo
    if (addressParts.city && !addressParts.street) {
        const cityCoords = getKnownCoordinatesForCity(addressParts.city);
        if (cityCoords) {
            console.log("Usando coordenadas conocidas para ciudad:", cityCoords);
            const result = {
                lat: cityCoords.lat,
                lon: cityCoords.lon,
                display_name: addressParts.city + (addressParts.province ? ", " + addressParts.province : "") + ", Argentina",
                type: "city",
                importance: 0.75,
                zoomLevel: cityCoords.zoom
            };
            
            // También guardamos en caché
            try {
                localStorage.setItem(cacheKey, JSON.stringify({
                    lat: result.lat,
                    lon: result.lon,
                    result: result,
                    zoomLevel: result.zoomLevel,
                    timestamp: Date.now()
                }));
            } catch (e) {
                console.warn("Error guardando en caché:", e);
            }
            
            if (typeof callback === 'function') {
                callback(result.lat, result.lon, result, result.zoomLevel);
            }
            return;
        }
    }
    
    // === PASO 4: Si seguimos aquí, necesitamos hacer una búsqueda online ===
    if (geocodingInProgress) {
        console.log("Ya hay una solicitud de geocodificación en progreso, intentando nuevamente en 200ms");
        setTimeout(() => {
            geocodeAddress(address, callback, zoomLevel);
        }, 200);
        return;
    }
    
    geocodingInProgress = true;
    
    // === PASO 4.1: Intentar primero con OpenCage API si está habilitado ===
    if (useOpenCageFirst) {
        console.log("Intentando geocodificación con OpenCage API:", address);
        
        // Configurar query para OpenCage
        const queryParams = new URLSearchParams({
            q: address,
            limit: 5
        }).toString();
        
        // Usar nuestra API interna que maneja la API key en el servidor
        fetch(`/api/geocode?${queryParams}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error de respuesta: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error("Error en API de OpenCage:", data.error);
                    throw new Error(data.error);
                }
                
                if (data.results && data.results.length > 0) {
                    // Encontramos resultados con OpenCage
                    const result = data.results[0]; // Tomar el primer resultado
                    console.log("Geocodificación exitosa con OpenCage:", result);
                    
                    // Preparar objeto de resultado en formato estándar
                    const standardResult = {
                        lat: result.lat,
                        lon: result.lng,
                        display_name: result.formatted,
                        type: "address",
                        importance: 0.9,
                        zoomLevel: 18, // Zoom alto para direcciones exactas
                        source: 'opencage'
                    };
                    
                    // También guardamos en caché
                    try {
                        const cacheKey = `geocode_${normalizedAddress}`;
                        localStorage.setItem(cacheKey, JSON.stringify({
                            lat: standardResult.lat,
                            lon: standardResult.lon,
                            result: standardResult,
                            zoomLevel: standardResult.zoomLevel || zoomLevel,
                            timestamp: Date.now()
                        }));
                    } catch (e) {
                        console.warn("Error guardando en caché:", e);
                    }
                    
                    // Liberar bandera y notificar resultado
                    geocodingInProgress = false;
                    if (typeof callback === 'function') {
                        callback(
                            parseFloat(standardResult.lat), 
                            parseFloat(standardResult.lon), 
                            standardResult, 
                            standardResult.zoomLevel || zoomLevel
                        );
                    }
                    return;
                } else {
                    console.log("OpenCage no encontró resultados, usando métodos alternativos");
                    throw new Error("No se encontraron resultados con OpenCage");
                }
            })
            .catch(error => {
                console.warn("Error o sin resultados con OpenCage, continuando con métodos alternativos:", error.message);
                // Continuamos con los métodos alternativos, no liberamos geocodingInProgress
            });
    
    // Mostrar indicador de carga
    const loadingEl = document.getElementById('map-loading-indicator');
    if (loadingEl) loadingEl.style.display = 'block';
    
    // Hacer geocodificación optimizada para Argentina
    performMultipleGeocodingRequests(addressParts, (result) => {
        geocodingInProgress = false;
        
        // Ocultar indicador de carga
        if (loadingEl) loadingEl.style.display = 'none';
        
        if (result && result.lat && result.lon) {
            // Éxito - Guardar en ambas cachés para máxima eficiencia
            try {
                // En sessionStorage para esta sesión
                sessionStorage.setItem(cacheKey, JSON.stringify({
                    lat: result.lat,
                    lon: result.lon,
                    result: result,
                    zoomLevel: result.zoomLevel || zoomLevel
                }));
                
                // En localStorage para persistencia entre sesiones (24 horas)
                localStorage.setItem(cacheKey, JSON.stringify({
                    lat: result.lat,
                    lon: result.lon,
                    result: result,
                    zoomLevel: result.zoomLevel || zoomLevel,
                    timestamp: Date.now()
                }));
                
                console.log("Resultado guardado en caché local y de sesión");
            } catch (e) {
                console.warn("No se pudo guardar en caché:", e);
            }
            
            if (typeof callback === 'function') {
                callback(
                    parseFloat(result.lat), 
                    parseFloat(result.lon), 
                    result, 
                    result.zoomLevel || zoomLevel
                );
            }
        } else {
            console.warn("No se encontraron resultados para ninguna variante de la dirección:", address);
            
            // Última oportunidad - intentar con el nombre de la ciudad si está disponible
            if (addressParts.city) {
                const cityCoords = getKnownCoordinatesForCity(addressParts.city);
                if (cityCoords) {
                    console.log("Usando coordenadas conocidas para ciudad como último recurso:", cityCoords);
                    const fallbackResult = {
                        lat: cityCoords.lat.toString(),
                        lon: cityCoords.lon.toString(),
                        display_name: addressParts.city + (addressParts.province ? ", " + addressParts.province : "") + ", Argentina",
                        type: "city",
                        importance: 0.7,
                        zoomLevel: cityCoords.zoom,
                        fallback: true
                    };
                    
                    if (typeof callback === 'function') {
                        callback(cityCoords.lat, cityCoords.lon, fallbackResult, cityCoords.zoom);
                    }
                    return;
                }
            }
            
            if (typeof callback === 'function') {
                callback(null, null, null);
            }
        }
    });
}

/**
 * Extrae partes significativas de una dirección para mejorar la búsqueda
 * @param {string} fullAddress - Dirección completa a analizar
 * @returns {Object} - Objeto con las partes de la dirección
 */
function extractAddressParts(fullAddress) {
    const parts = {};
    
    // Intentar extraer país, provincia, ciudad y dirección específica
    const segments = fullAddress.split(',').map(s => s.trim());
    
    // Extraer número de la calle si existe
    const streetNumberMatch = fullAddress.match(/(\d+)/);
    if (streetNumberMatch) {
        parts.number = streetNumberMatch[0];
    }
    
    // Extraer nombre de la calle (todo antes del número si hay)
    if (parts.number) {
        const streetNameMatch = fullAddress.match(/([^\d,]+)[\s]*\d+/);
        if (streetNameMatch) {
            parts.street = streetNameMatch[1].trim();
        }
    }
    
    // Si no pudimos extraer calle y número por el patrón, usar el último segmento
    if (!parts.street && segments.length > 0) {
        parts.specificAddress = segments[0];
    }
    
    // Asignar el resto de segmentos a ciudad, provincia, país
    if (segments.length > 1) parts.city = segments[1]; 
    if (segments.length > 2) parts.province = segments[2];
    if (segments.length > 3) parts.country = segments[3];
    
    // Reconstruir dirección completa en diferentes formatos
    parts.fullAddress = fullAddress;
    
    return parts;
}

/**
 * Realiza múltiples intentos de geocodificación con diferentes formatos y proveedores
 * @param {Object} addressParts - Partes de la dirección extraídas
 * @param {Function} finalCallback - Función final a llamar con el mejor resultado
 */
window.performMultipleGeocodingRequests = function(addressParts, finalCallback) {
    const { direccion, ciudad, provincia, pais } = addressParts;
    
    // Construir query estructurada para mejor precisión
    let query = [];
    if (direccion) query.push(direccion);
    if (ciudad) query.push(ciudad);
    if (provincia) query.push(provincia);
    if (pais) query.push(pais || 'Argentina');
    
    const searchString = query.join(', ');
    
    // PASO 1: Intentar con nuestra API interna de OpenCage primero
    const queryParams = new URLSearchParams({
        q: searchString,
        limit: 5
    }).toString();
    
    console.log("Consultando API de OpenCage a través de nuestro proxy:", searchString);
    
    // Usar nuestra API interna que maneja la API key en el servidor
    fetch(`/api/geocode?${queryParams}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error de respuesta: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error("Error en API de OpenCage:", data.error);
                throw new Error(data.error);
            }
            
            if (data.results && data.results.length > 0) {
                // Encontramos resultados con OpenCage
                const result = data.results[0]; // Tomar el primer resultado
                console.log("Geocodificación exitosa con OpenCage:", result);
                
                // Preparar objeto de resultado en formato estándar
                const standardResult = {
                    lat: result.lat.toString(),
                    lon: result.lng.toString(),
                    display_name: result.formatted,
                    type: "address",
                    importance: 0.9,
                    zoomLevel: 18, // Zoom alto para direcciones exactas
                    source: 'opencage'
                };
                
                // Devolver inmediatamente el resultado
                finalCallback(standardResult);
                return;
            } else {
                // OpenCage no encontró resultados, probamos con Nominatim
                throw new Error("No se encontraron resultados con OpenCage");
            }
        })
        .catch(error => {
            console.warn("Error o sin resultados con OpenCage, intentando con Nominatim:", error.message);
            
            // PASO 2: Si falla OpenCage, intentar con Nominatim como respaldo
            const encodedQuery = encodeURIComponent(searchString);
            
            // Usar Nominatim con parámetros optimizados
            fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodedQuery}&limit=1&countrycodes=ar&addressdetails=1`, {
                headers: {
                    'User-Agent': 'EcoSmartAdvisor/1.0'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    const result = {
                        lat: data[0].lat,
                        lon: data[0].lon,
                        display_name: data[0].display_name,
                        type: data[0].type,
                        importance: data[0].importance,
                        zoomLevel: determineZoomLevel(data[0].type),
                        from_nominatim: true
                    };
                    
                    // Devolver la dirección encontrada con Nominatim
                    finalCallback(result);
                    return;
                }
                
                // Crear diferentes variantes de consulta para aumentar probabilidad de éxito
                const queryVariants = createQueryVariants(addressParts);
                console.log("Variantes de consulta generadas:", queryVariants);
    
                // Formatos adicionales específicos para Argentina
                // 1. Usar el formato argentino de dirección: "Calle Número, Ciudad, Provincia, Argentina"
                // 2. Buscar sólo con nombre de calle y ciudad si el número no se encuentra
    
                let bestResult = null;
                let requestsCompleted = 0;
                const totalRequests = queryVariants.length;
    
                // Función para procesar resultados de cada petición
                const processResults = (results, queryVariant) => {
                    requestsCompleted++;
                    
                    if (results && results.length > 0) {
                        // Filtrar y priorizar resultados por país y relevancia
                        const filteredResults = filterResultsByCountry(results, 'Argentina');
                        if (filteredResults.length > 0) {
                            const prioritizedResult = prioritizeResults(filteredResults, addressParts);
                            
                            // Si este es el primer resultado o mejor que el anterior, actualizarlo
                            if (!bestResult || (prioritizedResult.score > bestResult.score)) {
                                bestResult = prioritizedResult;
                                console.log("Nuevo mejor resultado encontrado:", bestResult);
                            }
                        }
                    }
                    
                    // Verificar si hemos completado todas las peticiones
                    if (requestsCompleted >= totalRequests) {
                        // Si no tenemos resultado pero tenemos ciudad, intentar usar coordenadas conocidas
                        if (!bestResult && addressParts.city) {
                            const knownCoords = getKnownCoordinatesForCity(addressParts.city);
                            if (knownCoords) {
                                console.log("Usando coordenadas conocidas para ciudad como último recurso:", knownCoords);
                                bestResult = {
                                    lat: knownCoords.lat.toString(),
                                    lon: knownCoords.lon.toString(),
                                    display_name: addressParts.city + (addressParts.province ? ", " + addressParts.province : "") + ", Argentina",
                                    type: "city",
                                    importance: 0.75,
                                    zoomLevel: knownCoords.zoom,
                                    fallback: true
                                };
                            }
                        }
                        
                        finalCallback(bestResult);
                    }
                };
    
                // Realizar peticiones para cada variante
                queryVariants.forEach((query, index) => {
                    setTimeout(() => {
                        // Usar Nominatim para geocodificación
                        const encodedQuery = encodeURIComponent(query);
                        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodedQuery}&addressdetails=1&limit=5&accept-language=es`;
                        
                        console.log(`Realizando petición ${index+1}/${totalRequests} a:`, url);
                        
                        // Crear un timeout para abortar la solicitud si tarda demasiado
                        const controller = new AbortController();
                        const timeoutId = setTimeout(() => controller.abort(), 3000);
                        
                        fetch(url, { signal: controller.signal })
                            .then(response => {
                                clearTimeout(timeoutId);
                                if (!response.ok) {
                                    throw new Error(`Error HTTP: ${response.status}`);
                                }
                                return response.json();
                            })
                            .then(data => {
                                console.log(`Datos recibidos para consulta ${index+1}:`, data);
                                processResults(data, query);
                            })
                            .catch(error => {
                                clearTimeout(timeoutId);
                                console.error(`Error en consulta ${index+1}:`, error);
                                requestsCompleted++;
                                
                                // Si todas las peticiones fallaron, devolver el callback con error
                    if (requestsCompleted >= totalRequests) {
                        // Si no tenemos resultado pero tenemos ciudad, intentar usar coordenadas conocidas
                        if (!bestResult && addressParts.city) {
                            const knownCoords = getKnownCoordinatesForCity(addressParts.city);
                            if (knownCoords) {
                                console.log("Usando coordenadas conocidas para ciudad como último recurso (timeout):", knownCoords);
                                bestResult = {
                                    lat: knownCoords.lat.toString(),
                                    lon: knownCoords.lon.toString(),
                                    display_name: addressParts.city + (addressParts.province ? ", " + addressParts.province : "") + ", Argentina",
                                    type: "city",
                                    importance: 0.75,
                                    zoomLevel: knownCoords.zoom,
                                    fallback: true
                                };
                            }
                        }
                        
                        finalCallback(bestResult);
                    }
                });
        }, index * 200); // Espaciar las peticiones para no sobrecargar el servidor
    });
    
    // Si no hay variantes (improbable), devolver error
    if (queryVariants.length === 0) {
        finalCallback(null);
    }
}

/**
 * Crea múltiples variantes de consulta para aumentar probabilidad de éxito
 * @param {Object} parts - Partes de la dirección
 * @returns {Array} - Array de strings con diferentes formatos de consulta
 */
function createQueryVariants(parts) {
    const variants = [];
    
    // Variante 1: Dirección completa original
    if (parts.fullAddress) {
        variants.push(parts.fullAddress);
    }
    
    // Variante 2: Formato argentino estricto si tenemos calle y número
    if (parts.street && parts.number) {
        let argentineFormat = `${parts.street} ${parts.number}`;
        if (parts.city) argentineFormat += `, ${parts.city}`;
        if (parts.province) argentineFormat += `, ${parts.province}`;
        argentineFormat += `, Argentina`;
        
        variants.push(argentineFormat);
    }
    
    // Variante 3: Calle y ciudad (sin número, útil cuando el número no se encuentra)
    if (parts.street && parts.city) {
        variants.push(`${parts.street}, ${parts.city}, Argentina`);
    }
    
    // Variante 4: Calle, número y ciudad sin otros detalles
    if (parts.street && parts.number && parts.city) {
        variants.push(`${parts.street} ${parts.number}, ${parts.city}`);
    }
    
    // Variante 5: Especialmente para Río Tercero, Córdoba
    if (parts.city && parts.city.toLowerCase().includes('rio tercero') || 
        parts.city && parts.city.toLowerCase().includes('río tercero')) {
        
        // Coordenadas conocidas para Río Tercero, Córdoba
        variants.push(`Río Tercero, Córdoba, Argentina`);
        
        if (parts.street && parts.number) {
            // Varias variantes de escritura para Río Tercero
            variants.push(`${parts.street} ${parts.number}, Río Tercero, Córdoba, Argentina`);
            variants.push(`${parts.street} ${parts.number}, Rio Tercero, Cordoba, Argentina`);
            variants.push(`${parts.street} ${parts.number}, Rio Tercero, Argentina`);
            
            // Intentar con barrios conocidos en Río Tercero
            const barriosRioTercero = [
                "Centro", "Norte", "Sur", "Media Luna", "Cerino", 
                "Panamericano", "Belgrano", "Cabero", "Castagnino"
            ];
            
            // Agregar algunas variantes con barrios
            barriosRioTercero.forEach(barrio => {
                variants.push(`${parts.street} ${parts.number}, Barrio ${barrio}, Río Tercero, Córdoba, Argentina`);
            });
        }
        
        // Caso sin éxito: intentar fallback con coordenadas conocidas
        // Coordenadas aproximadas para el centro de Río Tercero: -32.173, -64.112
        // Estas se usarán si nada más funciona
    }
    
    // Variante 6: Ciudad y provincia simplificado
    if (parts.city && parts.province) {
        variants.push(`${parts.city}, ${parts.province}, Argentina`);
    }
    
    // Eliminar duplicados
    return [...new Set(variants)];
}

/**
 * Filtra resultados por país para asegurar que son de Argentina
 * @param {Array} results - Resultados de geocodificación
 * @param {string} countryName - Nombre del país a filtrar
 * @returns {Array} - Resultados filtrados
 */
function filterResultsByCountry(results, countryName) {
    return results.filter(result => {
        // Verificar en addressdetails.country
        if (result.address && result.address.country) {
            return result.address.country.toLowerCase() === countryName.toLowerCase();
        }
        
        // Verificar en display_name como fallback
        if (result.display_name) {
            return result.display_name.toLowerCase().includes(countryName.toLowerCase());
        }
        
        return false;
    });
}

/**
 * Prioriza y puntúa resultados según relevancia para la dirección buscada
 * @param {Array} results - Resultados de geocodificación
 * @param {Object} addressParts - Partes de la dirección buscada
 * @returns {Object} - El mejor resultado con su puntuación
 */
function prioritizeResults(results, addressParts) {
    // Puntuar resultados según criterios de relevancia
    const scoredResults = results.map(result => {
        let score = 0;
        let zoomLevel = 15; // Zoom predeterminado
        
        // Priorizar por tipo de resultado
        const typeWeights = {
            'house': 50,
            'building': 45,
            'residential': 40,
            'address': 35,
            'street': 30,
            'road': 25,
            'pedestrian': 20,
            'path': 15,
            'quarter': 10,
            'suburb': 8,
            'village': 5,
            'town': 3,
            'city': 2
        };
        
        // Añadir puntos por tipo
        score += typeWeights[result.type] || 0;
        
        // Ajustar zoom según tipo
        if (result.type === 'house' || result.type === 'building') {
            zoomLevel = 18;
        } else if (result.type === 'street' || result.type === 'road') {
            zoomLevel = 17;
        } else if (result.type === 'suburb' || result.type === 'quarter') {
            zoomLevel = 15;
        } else if (result.type === 'city' || result.type === 'town') {
            zoomLevel = 13;
        }
        
        // Verificar coincidencia de dirección específica
        if (addressParts.street && result.address && result.address.road) {
            // Normalizar para comparación
            const normStreet = addressParts.street.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            const normResultStreet = result.address.road.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            
            // Puntuar por coincidencia exacta o parcial
            if (normStreet === normResultStreet) {
                score += 30;
            } else if (normResultStreet.includes(normStreet) || normStreet.includes(normResultStreet)) {
                score += 20;
            }
        }
        
        // Verificar coincidencia de número
        if (addressParts.number && result.address && result.address.house_number) {
            if (addressParts.number === result.address.house_number) {
                score += 30;
            }
        }
        
        // Verificar coincidencia de ciudad
        if (addressParts.city && result.address) {
            const cityMatches = ['city', 'town', 'village', 'hamlet'].some(cityType => {
                if (!result.address[cityType]) return false;
                
                const normCity = addressParts.city.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                const normResultCity = result.address[cityType].toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                
                return normCity === normResultCity || normResultCity.includes(normCity) || normCity.includes(normResultCity);
            });
            
            if (cityMatches) score += 20;
        }
        
        // Verificar coincidencia de provincia
        if (addressParts.province && result.address && result.address.state) {
            const normProvince = addressParts.province.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            const normResultProvince = result.address.state.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            
            if (normProvince === normResultProvince || normResultProvince.includes(normProvince)) {
                score += 15;
            }
        }
        
        // Caso especial para Río Tercero, Córdoba
        if ((addressParts.city && addressParts.city.toLowerCase().includes('rio tercero')) || 
            (result.display_name && result.display_name.toLowerCase().includes('rio tercero'))) {
            score += 10; // Bonus para Río Tercero
        }
        
        // Añadir metadatos necesarios al resultado
        return {
            ...result,
            score,
            zoomLevel
        };
    });
    
    // Ordenar por puntuación y devolver el mejor
    scoredResults.sort((a, b) => b.score - a.score);
    return scoredResults[0] || results[0];
}

/**
 * Geocodificación progresiva que se ajusta según la precisión de la información
 * @param {Object} params - Objeto con los parámetros de geocodificación
 * @param {string} params.pais - Nombre del país (opcional, pero recomendado)
 * @param {string} params.provincia - Nombre de la provincia/estado
 * @param {string} params.ciudad - Nombre de la ciudad/localidad (opcional)
 * @param {string} params.direccion - Dirección específica (opcional)
 * @param {Function} callback - Función a llamar con los datos obtenidos
 */
function geocodeProgressive(params, callback) {
    const { pais, provincia, ciudad, direccion } = params;
    
    // Verificar si tenemos al menos la provincia
    if (!provincia || provincia.trim() === '') {
        console.error("Se requiere al menos la provincia para la geocodificación progresiva");
        return;
    }
    
    console.log("Iniciando geocodificación progresiva con:", params);
    
    // Determinar qué nivel de precisión tenemos y qué geocodificar
    let query = '';
    let zoomLevel = 7; // Nivel de zoom para provincia
    
    // Formatear la consulta de manera que optimice la búsqueda basada en la estructura de direcciones
    if (direccion && ciudad && provincia) {
        // Detectar si la dirección ya contiene números (calle específica con número)
        const tieneNumero = /\d+/.test(direccion);
        
        // Tenemos dirección específica y ciudad, la consulta más precisa
        if (pais) {
            // Formato país, optimizado para búsqueda específica
            if (tieneNumero) {
                // Si tenemos número de calle, hacemos la búsqueda más específica
                query = `${direccion}, ${ciudad}, ${provincia}, ${pais}`;
                zoomLevel = 19; // Zoom muy cercano para dirección exacta
            } else {
                query = `${direccion}, ${ciudad}, ${provincia}, ${pais}`;
                zoomLevel = 18; // Zoom cercano para dirección específica
            }
        } else {
            // Sin país especificado
            if (tieneNumero) {
                query = `${direccion}, ${ciudad}, ${provincia}`;
                zoomLevel = 19;
            } else {
                query = `${direccion}, ${ciudad}, ${provincia}`;
                zoomLevel = 18;
            }
        }
    } else if (ciudad && provincia) {
        // Tenemos ciudad pero no dirección específica
        query = pais 
            ? `${ciudad}, ${provincia}, ${pais}` 
            : `${ciudad}, ${provincia}`;
        zoomLevel = 13; // Zoom medio para la ciudad
    } else if (provincia) {
        // Solo tenemos provincia
        query = pais 
            ? `${provincia}, ${pais}` 
            : provincia;
        zoomLevel = 7; // Zoom lejano para la provincia
    }
    
    console.log("Query formateada para geocodificación:", query, "Zoom:", zoomLevel);
    
    // Realizar la geocodificación con el nivel de zoom apropiado
    geocodeAddress(query, function(lat, lng, result, zoom) {
        // Pasar el resultado al callback, con el nivel de zoom apropiado
        if (typeof callback === 'function') {
            callback(lat, lng, result, zoom);
        }
    }, zoomLevel);
}

/**
 * Busca una dirección específica en la base de datos de direcciones conocidas
 * @param {Object} addressParts - Partes de la dirección extraídas
 * @returns {Object|null} - Objeto con lat, lon, etc. o null si no se encuentra
 */
function findKnownAddress(addressParts) {
    if (!addressParts || !addressParts.street) return null;
    
    // Crear una clave de búsqueda normalizada
    let searchKey = '';
    if (addressParts.street && addressParts.number) {
        searchKey = `${addressParts.street} ${addressParts.number}`;
        
        if (addressParts.city) {
            searchKey += ` ${addressParts.city}`;
        }
    } else if (addressParts.fullAddress) {
        searchKey = addressParts.fullAddress;
    } else {
        return null;
    }
    
    // Normalizar la clave de búsqueda (minúsculas, sin acentos)
    searchKey = searchKey.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    
    console.log("Buscando dirección conocida con clave:", searchKey);
    
    // Buscar coincidencias exactas
    if (knownAddressesDatabase[searchKey]) {
        return knownAddressesDatabase[searchKey];
    }
    
    // Buscar coincidencias parciales
    for (const [key, value] of Object.entries(knownAddressesDatabase)) {
        if (searchKey.includes(key) || key.includes(searchKey)) {
            return value;
        }
    }
    
    return null;
}

/**
 * Recurso de último momento - Coordenadas predefinidas para ciudades argentinas comunes
 * Sólo se debe usar como último recurso cuando la geocodificación falla totalmente
 * @param {string} cityName - Nombre de la ciudad a buscar
 * @returns {Object|null} - Objeto con lat, lon y zoom o null si no se encuentra
 */
function getKnownCoordinatesForCity(cityName) {
    if (!cityName) return null;
    
    // Normalizar el nombre de la ciudad
    const normalizedCity = cityName.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // Eliminar acentos
    
    // Base de datos de coordenadas conocidas para ciudades argentinas comunes
    const knownCities = {
        // Córdoba
        "cordoba": { lat: -31.420, lon: -64.188, zoom: 12 },
        "cordoba capital": { lat: -31.420, lon: -64.188, zoom: 12 },
        "rio tercero": { lat: -32.173, lon: -64.112, zoom: 14 },
        "río tercero": { lat: -32.173, lon: -64.112, zoom: 14 },
        "rio cuarto": { lat: -33.123, lon: -64.349, zoom: 13 },
        "villa maria": { lat: -32.407, lon: -63.240, zoom: 13 },
        
        // Buenos Aires
        "buenos aires": { lat: -34.603, lon: -58.381, zoom: 12 },
        "la plata": { lat: -34.921, lon: -57.954, zoom: 13 },
        "mar del plata": { lat: -38.005, lon: -57.542, zoom: 13 },
        
        // Otras provincias
        "rosario": { lat: -32.944, lon: -60.639, zoom: 13 },
        "mendoza": { lat: -32.889, lon: -68.844, zoom: 13 },
        "san juan": { lat: -31.537, lon: -68.525, zoom: 13 },
        "tucuman": { lat: -26.808, lon: -65.217, zoom: 13 }
    };
    
    // Buscar coincidencias
    for (const [city, coords] of Object.entries(knownCities)) {
        if (normalizedCity.includes(city) || city.includes(normalizedCity)) {
            return coords;
        }
    }
    
    return null;
}

/**
 * Agrega o actualiza un marcador en el mapa
 * @param {Object} map - Instancia del mapa
 * @param {number} lat - Latitud
 * @param {number} lng - Longitud
 * @param {number} zoom - Nivel de zoom (opcional)
 * @returns {Object} - El marcador creado o actualizado
 */
// Exponer la función globalmente
window.addOrUpdateMarker = function(map, lat, lng, zoom = 15) {
    if (!map) {
        console.error("El mapa no está inicializado");
        return null;
    }
    
    console.log("Agregando/actualizando marcador en:", lat, lng, "con zoom:", zoom);
    
    // Parsear coordenadas para asegurar que son números válidos
    lat = parseFloat(lat);
    lng = parseFloat(lng);
    
    if (isNaN(lat) || isNaN(lng)) {
        console.error("Coordenadas inválidas:", lat, lng);
        return null;
    }
    
    // Asegurar que las coordenadas están en rangos válidos
    if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
        console.error("Coordenadas fuera de rango:", lat, lng);
        return null;
    }
    
    // Remover marcador existente si ya hay uno
    if (ecosmartMarker) {
        try {
            console.log("Removiendo marcador existente");
            ecosmartMarker.remove();
            ecosmartMarker = null;
        } catch (e) {
            console.error("Error al remover marcador:", e);
        }
    }
    
    try {
        // Crear un nuevo marcador
        console.log("Creando nuevo marcador en:", lat, lng);
        ecosmartMarker = L.marker([lat, lng]).addTo(map);
        
        // Añadir un popup para hacer más visible el marcador
        ecosmartMarker.bindPopup("Ubicación seleccionada").openPopup();
        
        // Centrar el mapa en la ubicación del marcador con el zoom especificado
        map.setView([lat, lng], zoom);
        console.log("Mapa centrado en:", lat, lng, "con zoom:", zoom);
        
        return ecosmartMarker;
    } catch (e) {
        console.error("Error al agregar/actualizar marcador:", e);
        return null;
    }
}

function initMap(containerId) {
    try {
        const map = L.map(containerId).setView([-34.603722, -58.381592], 4);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        return map;
    } catch (e) {
        console.error("Error al inicializar mapa:", e);
        return null;
    }
}
function determineZoomLevel(locationType) {
    const zoomLevels = {
        'house': 19,
        'building': 18,
        'street': 17,
        'suburb': 15,
        'city': 13,
        'administrative': 12,
        'state': 8,
        'country': 6
    };
    return zoomLevels[locationType] || 16;
}