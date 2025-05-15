/**
 * Script simplificado para manejar el mapa de selección de ubicación
 * Este script reemplaza la compleja implementación anterior
 */

// Función global para inicializar el mapa que puede ser llamada desde otros scripts
function initMap(mapContainerId) {
    console.log("Función initMap llamada para inicializar el mapa en:", mapContainerId);
    
    // Si se proporciona un ID de contenedor, usarlo, de lo contrario usar el predeterminado
    const mapContainerElement = mapContainerId ? 
        document.getElementById(mapContainerId) : 
        document.getElementById('mapaUbicacion');
    
    if (mapContainerElement) {
        console.log("Contenedor de mapa encontrado, configurando Leaflet");
        
        // Asegurarse de que el contenedor sea visible y tenga tamaño apropiado
        // Ajustamos altura según el dispositivo para mejorar la experiencia móvil
        mapContainerElement.style.display = 'block';
        
        // Altura adaptativa según el ancho de pantalla (dispositivo móvil vs escritorio)
        const isMobile = window.innerWidth < 768;
        mapContainerElement.style.height = isMobile ? '300px' : '400px';
        
        // Inicializar con coordenadas predeterminadas (Argentina)
        const defaultLat = -38.416097;
        const defaultLng = -63.616672;
        const defaultZoom = isMobile ? 3 : 4; // Zoom más lejano en móviles para mejor contexto
        
        try {
            // Verificación adicional de que Leaflet está disponible
            if (typeof L === 'undefined') {
                throw new Error("Leaflet no está disponible en este momento");
            }
            
            // Crear el mapa con opciones optimizadas para móviles
            const mapOptions = {
                zoomControl: true,
                attributionControl: true,
                scrollWheelZoom: true,
                dragging: !L.Browser.mobile, // Desactivar arrastre en móviles inicialmente
                tap: !L.Browser.mobile       // Desactivar tap en móviles inicialmente
            };
            
            const newMap = L.map(mapContainerElement.id, mapOptions).setView([defaultLat, defaultLng], defaultZoom);
            
            // Reactivar arrastre y tap después de un momento para evitar problemas al inicio
            setTimeout(function() {
                if (L.Browser.mobile) {
                    newMap.dragging.enable();
                    newMap.tap.enable();
                }
            }, 1000);
            
            // Agregar capa de mosaicos con URLs de respaldo
            const tileUrls = [
                'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
                'https://tile.openstreetmap.de/{z}/{x}/{y}.png'
            ];
            
            // Intentar el primer URL, si falla, probar con el siguiente
            let tileLayerAdded = false;
            for (let i = 0; i < tileUrls.length; i++) {
                try {
                    L.tileLayer(tileUrls[i], {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        maxZoom: 19,
                        minZoom: 3
                    }).addTo(newMap);
                    tileLayerAdded = true;
                    console.log("Mapa inicializado con URL de tiles:", tileUrls[i]);
                    break;
                } catch (tileError) {
                    console.warn("Error al cargar tiles desde", tileUrls[i], tileError);
                    continue;
                }
            }
            
            if (!tileLayerAdded) {
                throw new Error("No se pudieron cargar las capas del mapa");
            }
            
            console.log("Mapa inicializado correctamente desde initMap");
            
            // Forzar actualización del mapa varias veces para asegurar visualización
            setTimeout(function() {
                newMap.invalidateSize();
                console.log("Primera actualización de tamaño del mapa");
                
                // Segunda actualización después de un tiempo más largo
                setTimeout(function() {
                    newMap.invalidateSize();
                    console.log("Segunda actualización de tamaño del mapa");
                }, 1000);
            }, 200);
            
            return newMap;
        } catch (error) {
            console.error("Error al inicializar el mapa desde initMap:", error);
            
            // Determinar si estamos en dispositivo móvil para personalizar mensaje
            const esMovil = detectarDispositivoMovil();
            let mensajeError = esMovil ? 
                "Error al cargar el mapa en dispositivo móvil. Intente con WiFi o recargar la página." :
                "Error al cargar el mapa. Por favor, recargue la página.";
                
            // Añadir detalles del error si están disponibles
            if (error && error.message) {
                console.error("Detalles del error:", error.message);
                
                // Personalizar para ciertos tipos de errores comunes en móviles
                if (esMovil) {
                    if (error.message.includes("timeout") || error.message.includes("timed out")) {
                        mensajeError = "Tiempo de espera agotado al cargar el mapa. Verifique su conexión e intente nuevamente.";
                    } else if (error.message.includes("network") || error.message.includes("Network")) {
                        mensajeError = "Error de red. Verifique su conexión a internet y recargue la página.";
                    }
                }
            }
            
            // Mostrar mensaje en el elemento de error específico
            const errorMsgEl = document.getElementById('location-error-message');
            if (errorMsgEl) {
                errorMsgEl.style.display = 'block';
                const errorTextEl = errorMsgEl.querySelector('#error-text');
                if (errorTextEl) {
                    errorTextEl.textContent = mensajeError;
                }
            }
            
            // También mostrar directamente en el contenedor
            if (mapContainerElement) {
                mapContainerElement.innerHTML = 
                    '<div class="alert alert-danger p-3 m-0">' +
                    '<i class="fas fa-exclamation-triangle me-2"></i>' + 
                    mensajeError +
                    '<br><button type="button" class="btn btn-sm btn-outline-danger mt-2" onclick="window.location.reload()">Recargar página</button>' +
                    (esMovil ? '<br><small class="d-block mt-2">Consejo: Las conexiones WiFi suelen funcionar mejor para cargar mapas en dispositivos móviles.</small>' : '') +
                    '</div>';
            }
            
            return null;
        }
    } else {
        console.error("No se encontró el contenedor del mapa:", mapContainerId);
        return null;
    }
}

// Función para detectar si estamos en un dispositivo móvil
function detectarDispositivoMovil() {
    // Detectar si el dispositivo es móvil basado en el User-Agent o el tamaño de pantalla
    const esMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
                    window.innerWidth <= 768;
    
    console.log("Detección de dispositivo: " + (esMobile ? "Móvil" : "Escritorio"), window.innerWidth + "x" + window.innerHeight);
    
    return esMobile;
}

// Función para manejar errores al cargar el mapa con mensaje específico para móviles
function mostrarErrorMapaMobile(mensaje, containerElement) {
    const esMovil = detectarDispositivoMovil();
    
    // Mensaje predeterminado según el dispositivo
    let mensajeError = mensaje || (esMovil ? 
        "Error al cargar el mapa en dispositivo móvil. Intente recargar la página o utilizar WiFi." :
        "Error al cargar el mapa. Por favor, recargue la página.");
    
    console.error("Error de mapa:", mensajeError);
    
    // Mensaje para el contenedor de error específico
    const errorMsgEl = document.getElementById('location-error-message');
    if (errorMsgEl) {
        errorMsgEl.style.display = 'block';
        const errorTextEl = errorMsgEl.querySelector('#error-text');
        if (errorTextEl) {
            errorTextEl.textContent = mensajeError;
        }
    }
    
    // Mensaje directamente en el contenedor del mapa
    if (containerElement) {
        containerElement.innerHTML = '<div class="alert alert-danger p-3 m-0"><i class="fas fa-exclamation-triangle me-2"></i>' + 
            mensajeError + 
            '<br><button type="button" class="btn btn-sm btn-outline-danger mt-2" onclick="window.location.reload()">Recargar página</button>' +
            (esMovil ? '<br><small class="d-block mt-2">Consejo: En dispositivos móviles, una conexión WiFi estable mejora la carga del mapa.</small>' : '') +
            '</div>';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Detectar tipo de dispositivo
    const esDispositivoMovil = detectarDispositivoMovil();
    console.log("Aplicación cargada en: " + (esDispositivoMovil ? "Dispositivo móvil" : "Escritorio"));
    
    // Adaptar elementos de la interfaz si es móvil
    if (esDispositivoMovil) {
        const mapaContainers = document.querySelectorAll('.mapContainer');
        mapaContainers.forEach(container => {
            container.style.height = "300px"; // Altura reducida para móviles
        });
        
        // Añadir clase para estilos específicos de móvil
        document.body.classList.add('mobile-device');
    }
    
    // Referencias a elementos del DOM
    const mapaUbicacionDiv = document.getElementById('mapaUbicacion');
    const loadingIndicator = document.getElementById('map-loading-indicator');
    const centrarEnArgentinaBtn = document.getElementById('centrarEnArgentina');
    const coordenadasDiv = document.getElementById('coordenadasSeleccionadas');
    const latitudSpan = document.getElementById('latitudSeleccionada');
    const longitudSpan = document.getElementById('longitudSeleccionada');
    const usarCoordenadasBtn = document.getElementById('usarCoordenadas');
    const latitudInput = document.getElementById('latitud');
    const longitudInput = document.getElementById('longitud');
    const ubicacionInput = document.getElementById('ubicacion');
    const locationErrorMsg = document.getElementById('location-error-message');
    
    // Configuraciones para móvil
    if (esDispositivoMovil && mapaUbicacionDiv) {
        console.log("Aplicando configuraciones para móvil al mapa");
        mapaUbicacionDiv.style.height = "300px";
    }
    
    // Variables globales
    let map = null;
    let marker = null;
    let selectedLat = null;
    let selectedLng = null;
    let currentCountry = 'Argentina'; // País por defecto
    
    // Coordenadas por defecto (centro de Argentina)
    const ARGENTINA_LAT = -38.416097;
    const ARGENTINA_LNG = -63.616672;
    const ARGENTINA_ZOOM = 4;
    
    // Diccionario de traducciones de países (inglés a español)
    const countryTranslations = {
        'Argentina': 'Argentina',
        'Brazil': 'Brasil',
        'Bolivia': 'Bolivia',
        'Chile': 'Chile',
        'Colombia': 'Colombia',
        'Ecuador': 'Ecuador',
        'Paraguay': 'Paraguay',
        'Peru': 'Perú',
        'Uruguay': 'Uruguay',
        'Venezuela': 'Venezuela',
        'United States': 'Estados Unidos',
        'Mexico': 'México',
        'Spain': 'España',
        'France': 'Francia',
        'Italy': 'Italia',
        'Germany': 'Alemania',
        'United Kingdom': 'Reino Unido',
        'Portugal': 'Portugal',
        'Canada': 'Canadá'
        // Añadir más países según sea necesario
    };
    
    // Mostrar indicador de carga
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    
    // Inicializar mapa si tenemos el contenedor
    if (mapaUbicacionDiv) {
        try {
            // Verificar que Leaflet esté disponible
            if (typeof L === 'undefined') {
                throw new Error("La biblioteca Leaflet no está disponible");
            }
            
            // Si hay un mensaje de error visible, ocúltalo
            if (locationErrorMsg) {
                locationErrorMsg.style.display = 'none';
            }
            
            console.log("Intentando inicializar mapa con Leaflet. Estado de mapaUbicacionDiv:", mapaUbicacionDiv.clientWidth, "x", mapaUbicacionDiv.clientHeight);
            
            // Mostrar indicador de carga mientras se inicializa
            if (loadingIndicator) {
                loadingIndicator.style.display = 'block';
            }
            
            // Asegurarse de que el contenedor sea visible y tenga tamaño
            mapaUbicacionDiv.style.display = 'block';
            mapaUbicacionDiv.style.height = '400px';
            
            // Pequeña pausa para asegurar que el DOM está listo
            setTimeout(function() {
                try {
                    // Inicializar el mapa con Leaflet
                    map = L.map('mapaUbicacion').setView([ARGENTINA_LAT, ARGENTINA_LNG], ARGENTINA_ZOOM);
                    
                    // Agregar capa de mosaicos (tiles) - usar un servidor más estable
                    L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        maxZoom: 19,
                        minZoom: 3
                    }).addTo(map);
                    
                    // Ocultar indicador de carga
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                    
                    // Detectar país al iniciar y actualizar el botón
                    detectarPaisEnCentroMapa();
                    
                    // Detectar país cuando se mueve el mapa
                    map.on('moveend', function() {
                        detectarPaisEnCentroMapa();
                    });
                    
                    // Configurar evento de clic en el mapa
                    map.on('click', function(e) {
                        const lat = e.latlng.lat;
                        const lng = e.latlng.lng;
                        
                        // Actualizar coordenadas seleccionadas
                        selectedLat = lat;
                        selectedLng = lng;
                        
                        // Actualizar marcador
                        updateMarker(lat, lng);
                        
                        // Mostrar panel de coordenadas
                        updateCoordinatesPanel(lat, lng);
                        
                        // Obtener descripción de la ubicación (país, provincia, ciudad)
                        obtenerDescripcionUbicacion(lat, lng);
                        
                        // Asegurarse de ocultar cualquier mensaje de error
                        if (locationErrorMsg) {
                            locationErrorMsg.style.display = 'none';
                        }
                    });
                    
                    console.log("Mapa inicializado correctamente");
                    
                    // Forzar actualización del mapa para evitar problemas de renderizado
                    setTimeout(function() {
                        if (map) {
                            map.invalidateSize();
                            console.log("Tamaño del mapa actualizado");
                        }
                    }, 500);
                    
                } catch (innerError) {
                    console.error("Error durante la inicialización diferida del mapa:", innerError);
                    manejarErrorMapa(innerError);
                }
            }, 100);
            
        } catch (error) {
            console.error("Error al inicializar el mapa:", error);
            manejarErrorMapa(error);
        }
    }
    
    // Función para manejar errores de mapa de manera consistente
    function manejarErrorMapa(error) {
        // Ocultar indicador de carga
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        // Mostrar mensaje de error
        if (locationErrorMsg) {
            locationErrorMsg.style.display = 'block';
            const errorTextEl = locationErrorMsg.querySelector('#error-text');
            if (errorTextEl) {
                errorTextEl.textContent = "Error al cargar el mapa. Por favor, recargue la página.";
            }
            console.warn("Mostrando mensaje de error al usuario:", errorTextEl ? errorTextEl.textContent : "Mensaje de error no disponible");
        }
    }
    
    // Función para actualizar el marcador en el mapa
    function updateMarker(lat, lng) {
        // Remover marcador existente si hay
        if (marker) {
            map.removeLayer(marker);
        }
        
        // Crear nuevo marcador
        marker = L.marker([lat, lng]).addTo(map);
        
        // Centrar mapa en la ubicación
        map.setView([lat, lng], 15);
    }
    
    // Función para actualizar el panel de coordenadas
    function updateCoordinatesPanel(lat, lng) {
        if (coordenadasDiv && latitudSpan && longitudSpan) {
            // Formatear las coordenadas para mostrar
            latitudSpan.textContent = lat.toFixed(6);
            longitudSpan.textContent = lng.toFixed(6);
            
            // Mostrar el panel
            coordenadasDiv.classList.remove('d-none');
            
            // Ocultar mensaje de error si está visible
            if (locationErrorMsg) {
                locationErrorMsg.style.display = 'none';
            }
        }
    }
    
    // Función para obtener la descripción de la ubicación (país, provincia, ciudad)
    function obtenerDescripcionUbicacion(lat, lng) {
        const descripcionElement = document.getElementById('ubicacionDescripcion');
        
        if (descripcionElement) {
            descripcionElement.textContent = "Obteniendo ubicación...";
            descripcionElement.classList.remove('text-success', 'text-danger');
            descripcionElement.classList.add('text-muted');
            
            // Usar el servicio de geocodificación inversa de Nominatim
            const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1&accept-language=es`;
            
            fetch(url, {
                headers: {
                    'User-Agent': 'EcoSmartAdvisor/1.0'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error en la respuesta: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.address) {
                    // Construir descripción: País, estado/provincia, ciudad
                    const address = data.address;
                    const pais = address.country || '';
                    const provincia = address.state || address.province || '';
                    const ciudad = address.city || address.town || address.village || address.hamlet || '';
                    
                    let descripcion = '';
                    
                    if (ciudad) descripcion += ciudad;
                    if (provincia) {
                        if (descripcion) descripcion += ', ';
                        descripcion += provincia;
                    }
                    if (pais) {
                        if (descripcion) descripcion += ', ';
                        descripcion += pais;
                    }
                    
                    // Si no se pudo obtener una descripción completa
                    if (!descripcion) {
                        descripcion = data.display_name || 'Ubicación seleccionada';
                    }
                    
                    descripcionElement.textContent = descripcion;
                    descripcionElement.classList.remove('text-muted', 'text-danger');
                    descripcionElement.classList.add('text-success');
                    
                    // Guardar la descripción para usarla en el formulario
                    if (ubicacionInput) {
                        ubicacionInput.dataset.descripcion = descripcion;
                        
                        // También guardar en el campo oculto
                        const descripcionInput = document.getElementById('descripcion_ubicacion');
                        if (descripcionInput) {
                            descripcionInput.value = descripcion;
                        }
                    }
                } else {
                    descripcionElement.textContent = "Ubicación seleccionada";
                    descripcionElement.classList.remove('text-muted', 'text-danger');
                    descripcionElement.classList.add('text-success');
                }
            })
            .catch(error => {
                console.error('Error al obtener descripción de ubicación:', error);
                descripcionElement.textContent = "No se pudo obtener la dirección";
                descripcionElement.classList.remove('text-muted', 'text-success');
                descripcionElement.classList.add('text-danger');
            });
        }
    }
    
    // Función para detectar el país en el centro del mapa
    function detectarPaisEnCentroMapa() {
        if (!map || !centrarEnArgentinaBtn) return;
        
        // Obtener centro del mapa
        const center = map.getCenter();
        const lat = center.lat;
        const lng = center.lng;
        
        // Consultar Nominatim para obtener el país
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=3&addressdetails=1&accept-language=es`;
        
        fetch(url, {
            headers: {
                'User-Agent': 'EcoSmartAdvisor/1.0'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error en la respuesta: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.address && data.address.country) {
                // Obtener el país y traducirlo si es necesario
                let detectedCountry = data.address.country;
                let translatedCountry = countryTranslations[detectedCountry] || detectedCountry;
                
                // Actualizar el botón con el nombre del país
                centrarEnArgentinaBtn.innerHTML = `<i class="fas fa-globe-americas me-1"></i>${translatedCountry}`;
                
                // Guardar el país actual
                currentCountry = translatedCountry;
                
                // Actualizar el campo oculto del país (si existe)
                const paisInput = document.getElementById('pais');
                if (paisInput) {
                    paisInput.value = translatedCountry;
                }
            }
        })
        .catch(error => {
            console.error('Error al detectar país:', error);
            // En caso de error, mostrar "Argentina" por defecto
            centrarEnArgentinaBtn.innerHTML = `<i class="fas fa-globe-americas me-1"></i>Argentina`;
        });
    }
    
    // Botón para centrar mapa en Argentina
    if (centrarEnArgentinaBtn) {
        centrarEnArgentinaBtn.addEventListener('click', function() {
            if (map) {
                map.setView([ARGENTINA_LAT, ARGENTINA_LNG], ARGENTINA_ZOOM);
                // Al centrar en Argentina, actualizar el botón
                centrarEnArgentinaBtn.innerHTML = `<i class="fas fa-globe-americas me-1"></i>Argentina`;
                currentCountry = 'Argentina';
            }
        });
    }
    
    // Botón para usar coordenadas seleccionadas
    if (usarCoordenadasBtn) {
        usarCoordenadasBtn.addEventListener('click', function() {
            if (selectedLat && selectedLng) {
                // Actualizar campos ocultos del formulario
                if (latitudInput) {
                    latitudInput.value = selectedLat;
                }
                
                if (longitudInput) {
                    longitudInput.value = selectedLng;
                }
                
                if (ubicacionInput) {
                    // Incluir tanto coordenadas como descripción
                    const descripcion = ubicacionInput.dataset.descripcion || '';
                    ubicacionInput.value = `${selectedLat},${selectedLng}`;
                    
                    // Si tenemos descripción, guardarla en el campo oculto para usar en el backend
                    if (descripcion) {
                        const descripcionInput = document.getElementById('descripcion_ubicacion');
                        if (descripcionInput) {
                            descripcionInput.value = descripcion;
                        }
                    }
                }
                
                // Indicación visual de que se han confirmado las coordenadas
                usarCoordenadasBtn.innerHTML = '<i class="fas fa-check me-1"></i>Ubicación confirmada';
                usarCoordenadasBtn.classList.remove('btn-success');
                usarCoordenadasBtn.classList.add('btn-outline-success');
                
                // Mensaje de confirmación más amigable
                const descripcionElement = document.getElementById('ubicacionDescripcion');
                const lugarDescripcion = descripcionElement ? descripcionElement.textContent : 'seleccionada';
                
                // No interrumpir al usuario con alertas
                const successMsg = document.createElement('div');
                successMsg.className = 'alert alert-success mt-2 alert-dismissible fade show';
                successMsg.innerHTML = `
                    <i class="fas fa-check-circle me-2"></i>
                    Ubicación "${lugarDescripcion}" confirmada correctamente. Puede continuar con el resto del formulario.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                
                // Insertar mensaje de éxito después del panel de coordenadas
                if (coordenadasDiv && coordenadasDiv.parentNode) {
                    const existingMsg = coordenadasDiv.parentNode.querySelector('.alert-success');
                    if (existingMsg) {
                        existingMsg.remove();
                    }
                    coordenadasDiv.parentNode.insertBefore(successMsg, coordenadasDiv.nextSibling);
                    
                    // Auto-desaparición después de 5 segundos
                    setTimeout(() => {
                        successMsg.remove();
                    }, 5000);
                }
            }
        });
    }
    
    // Validar que se hayan seleccionado coordenadas antes de enviar el formulario
    const formularios = [
        document.getElementById('diagnosticoForm'),
        document.getElementById('simuladorForm')
    ];
    
    formularios.forEach(function(form) {
        if (form) {
            console.log("Configurando validación para formulario:", form.id);
            form.addEventListener('submit', function(e) {
                console.log("Verificando formulario antes de enviar:", form.id);
                console.log("Estado de coordenadas:", {
                    selectedLat: selectedLat,
                    selectedLng: selectedLng,
                    ubicacionInput: ubicacionInput ? ubicacionInput.value : 'no disponible'
                });
                
                if (!selectedLat || !selectedLng || (ubicacionInput && !ubicacionInput.value)) {
                    console.warn("Formulario bloqueado: coordenadas no seleccionadas");
                    e.preventDefault();
                
                    // Mostrar mensaje de error
                    if (locationErrorMsg) {
                        locationErrorMsg.style.display = 'block';
                        const errorTextEl = locationErrorMsg.querySelector('#error-text');
                        if (errorTextEl) {
                            errorTextEl.textContent = "Debe seleccionar y confirmar una ubicación en el mapa para continuar.";
                        }
                    }
                    
                    // Scroll hasta el mapa
                    if (mapaUbicacionDiv) {
                        mapaUbicacionDiv.scrollIntoView({ behavior: 'smooth' });
                    }
                } else {
                    console.log("Formulario validado correctamente, enviando datos");
                }
            });
        }
    });
});