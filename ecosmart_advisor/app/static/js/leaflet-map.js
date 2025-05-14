/**
 * Funciones para manejo del mapa con Leaflet
 */

// Variables globales
let ecosmartMap = null;  // Instancia del mapa
let ecosmartMarker = null;  // Marcador en el mapa
let geocodingInProgress = false; // Evita múltiples solicitudes simultáneas

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
        try {
            // Capturar las coordenadas y convertirlas a número antes de formatear
            const rawLat = e.latlng.lat;
            const rawLng = e.latlng.lng;
            
            // Validar coordenadas
            if (isNaN(rawLat) || isNaN(rawLng)) {
                console.error("Coordenadas inválidas del clic:", rawLat, rawLng);
                return;
            }
            
            // Formatear para precisión fija
            const lat = parseFloat(rawLat.toFixed(6));
            const lng = parseFloat(rawLng.toFixed(6));
            
            console.log("Click en el mapa en:", lat, lng);
            
            // Limpiar marcador existente si hay uno
            if (ecosmartMarker) {
                try {
                    ecosmartMarker.remove();
                    ecosmartMarker = null;
                } catch (err) {
                    console.warn("Error al eliminar marcador existente:", err);
                }
            }
            
            try {
                // Crear un nuevo marcador
                ecosmartMarker = L.marker([lat, lng]).addTo(map);
                ecosmartMarker.bindPopup("Ubicación seleccionada").openPopup();
                console.log("Marcador creado exitosamente en:", lat, lng);
            } catch (err) {
                console.error("Error al crear marcador:", err);
            }
            
            // Realizar geocodificación inversa para obtener la dirección
            reverseGeocode(lat, lng, function(addressData) {
                console.log("Datos de geocodificación inversa:", addressData);
                
                // Llamar al callback con las coordenadas y datos de dirección
                if (typeof callback === 'function') {
                    callback(lat, lng, addressData);
                }
            });
        } catch (error) {
            console.error("Error general en el evento de clic:", error);
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
function geocodeAddress(address, callback, zoomLevel = 15) {
    if (!address || address.trim() === '') {
        console.error("La dirección está vacía");
        return;
    }
    
    // Normalizar la dirección para evitar problemas de mayúsculas/minúsculas
    // y caracteres especiales
    const normalizedAddress = address.trim().toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // Eliminar acentos
    
    console.log("Realizando geocodificación para dirección normalizada:", normalizedAddress);
    
    // Extraer partes de la dirección original para mejor formato y búsqueda múltiple
    const addressParts = extractAddressParts(address);
    console.log("Partes extraídas de la dirección:", addressParts);
    
    // Verificar si tenemos la dirección en caché
    const cacheKey = `geocode_${normalizedAddress}`;
    const cachedResult = sessionStorage.getItem(cacheKey);
    
    if (cachedResult) {
        try {
            const cachedData = JSON.parse(cachedResult);
            console.log("Usando resultado en caché para:", normalizedAddress);
            
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
    
    if (geocodingInProgress) {
        console.log("Ya hay una solicitud de geocodificación en progreso, intentando nuevamente en 300ms");
        setTimeout(() => {
            geocodeAddress(address, callback, zoomLevel);
        }, 300);
        return;
    }
    
    geocodingInProgress = true;
    
    // Mostrar indicador de carga si existe
    const loadingEl = document.getElementById('map-loading-indicator');
    if (loadingEl) loadingEl.style.display = 'block';
    
    // Primero intentaremos con formatos optimizados para Argentina
    performMultipleGeocodingRequests(addressParts, (result) => {
        geocodingInProgress = false;
        
        // Ocultar indicador de carga
        if (loadingEl) loadingEl.style.display = 'none';
        
        if (result && result.lat && result.lon) {
            // Éxito - Guardar en caché
            try {
                sessionStorage.setItem(cacheKey, JSON.stringify({
                    lat: result.lat,
                    lon: result.lon,
                    result: result,
                    zoomLevel: result.zoomLevel || zoomLevel
                }));
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
function performMultipleGeocodingRequests(addressParts, finalCallback) {
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
        
        // Log para verificar que el marcador se creó correctamente
        console.log("Marcador creado exitosamente:", ecosmartMarker);
        
        return ecosmartMarker;
    } catch (e) {
        console.error("Error al crear marcador:", e);
        return null;
    }
}