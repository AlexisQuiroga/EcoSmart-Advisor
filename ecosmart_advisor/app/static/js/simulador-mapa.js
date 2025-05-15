/**
 * Script específico para manejar el mapa en la página del simulador
 * Versión optimizada para dispositivos móviles con múltiples CDNs
 */

// Variable global para almacenar la instancia del mapa
let simuladorMap = null;
let simuladorMarker = null;
let mapHasBeenInitialized = false;
let mapInitAttempts = 0;

// Función para verificar si la biblioteca Leaflet está disponible
function verificarLeaflet() {
    console.log("Verificando disponibilidad de Leaflet");
    
    if (typeof L === 'undefined') {
        console.error("Leaflet no está disponible");
        return false;
    }
    
    console.log("Leaflet está disponible");
    return true;
}

// Función para cargar leaflet desde CDN alternativo
function cargarLeafletAlternativo() {
    console.log("Intentando cargar Leaflet desde CDN alternativo");
    
    return new Promise((resolve, reject) => {
        // Si ya está cargado, resolvemos inmediatamente
        if (typeof L !== 'undefined') {
            console.log("Leaflet ya está disponible");
            resolve(true);
            return;
        }
        
        const cdns = [
            "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js",
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
            "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"
        ];
        
        let loaded = false;
        
        // Intentar cargar desde cada CDN en secuencia
        function tryNextCDN(index) {
            if (index >= cdns.length) {
                reject(new Error("No se pudo cargar Leaflet desde ningún CDN"));
                return;
            }
            
            const script = document.createElement('script');
            script.src = cdns[index];
            script.onload = () => {
                console.log("Leaflet cargado exitosamente desde: " + cdns[index]);
                loaded = true;
                resolve(true);
            };
            script.onerror = () => {
                console.warn("Error al cargar Leaflet desde: " + cdns[index]);
                tryNextCDN(index + 1);
            };
            
            document.head.appendChild(script);
        }
        
        tryNextCDN(0);
        
        // Timeout como medida de seguridad
        setTimeout(() => {
            if (!loaded) {
                reject(new Error("Tiempo de espera agotado al cargar Leaflet"));
            }
        }, 10000);
    });
}

// Función para cargar el mapa Leaflet en el simulador
function cargarLeaflet() {
    console.log("Iniciando carga de mapa Leaflet para simulador (intento " + (mapInitAttempts + 1) + ")");
    mapInitAttempts++;
    
    // Obtener referencias a elementos del DOM
    const mapaDiv = document.getElementById('mapaUbicacion');
    const indicadorCarga = document.getElementById('map-loading-indicator');
    const errorMsg = document.getElementById('location-error-message');
    
    // Si hay un error visible, ocultarlo para nuevo intento
    if (errorMsg) {
        errorMsg.style.display = 'none';
    }
    
    if (!mapaDiv) {
        console.error("No se encontró el contenedor del mapa");
        mostrarErrorMapa("Error: No se encontró el contenedor del mapa");
        return null;
    }
    
    // Mostrar indicador de carga
    if (indicadorCarga) {
        indicadorCarga.style.display = 'block';
    }
    
    // Si el mapa ya está inicializado, mostrar mensaje y salir
    if (simuladorMap) {
        console.log("El mapa ya está inicializado, actualizando tamaño");
        // Refrescar el tamaño para evitar problemas de visualización
        simuladorMap.invalidateSize();
        // Ocultar indicador de carga
        if (indicadorCarga) {
            indicadorCarga.style.display = 'none';
        }
        return simuladorMap;
    }
    
    // Crear contenedor limpio para el mapa
    while (mapaDiv.firstChild) {
        mapaDiv.removeChild(mapaDiv.firstChild);
    }
    
    // Inicializar el proceso de carga del mapa
    const iniciarMapa = () => {
        try {
            // Verificar si Leaflet está disponible
            if (!verificarLeaflet()) {
                console.warn("Leaflet no disponible, intentando cargar desde CDN alternativo");
                // Intentar cargar desde CDN alternativo
                cargarLeafletAlternativo()
                    .then(() => {
                        console.log("Leaflet cargado desde CDN alternativo, reiniciando");
                        setTimeout(cargarLeaflet, 500);
                    })
                    .catch(error => {
                        console.error("Error al cargar Leaflet:", error);
                        mostrarErrorMapa("No se pudo cargar la biblioteca de mapas. Intente con WiFi o recargue la página.");
                    });
                return null;
            }
            
            // Inicializar mapa centrado en Argentina
            console.log("Creando instancia del mapa Leaflet");
            
            // Clean up pre-existing instance if there was one
            if (simuladorMap) {
                try {
                    simuladorMap.remove();
                    simuladorMap = null;
                } catch (e) {
                    console.warn("Error al limpiar mapa existente:", e);
                }
            }
            
            // Create new map instance
            simuladorMap = L.map('mapaUbicacion', {
                zoomControl: true,
                attributionControl: false,
                preferCanvas: true
            }).setView([-38.416097, -63.616672], 4);
            
            // Agregar capa de mapa base con múltiples opciones de CDN
            const addTileLayer = () => {
                try {
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    }).addTo(simuladorMap);
                    return true;
                } catch (e) {
                    console.warn("Error con primer tile provider, intentando alternativa:", e);
                    try {
                        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
                            maxZoom: 19,
                            attribution: '&copy; CartoDB'
                        }).addTo(simuladorMap);
                        return true;
                    } catch (e2) {
                        console.error("Error con todos los tile providers:", e2);
                        return false;
                    }
                }
            };
            
            // Agregar tiles
            if (!addTileLayer()) {
                mostrarErrorMapa("Error al cargar las imágenes del mapa");
                return null;
            }
            
            // Configurar evento de clic en el mapa
            simuladorMap.on('click', function(e) {
                const lat = parseFloat(e.latlng.lat.toFixed(6));
                const lng = parseFloat(e.latlng.lng.toFixed(6));
                
                console.log("Clic en el mapa en:", lat, lng);
                
                // Actualizar los campos de formulario
                const latInput = document.getElementById('latitud');
                const lngInput = document.getElementById('longitud');
                
                if (latInput) latInput.value = lat;
                if (lngInput) lngInput.value = lng;
                
                // Actualizar la información mostrada
                const latSpan = document.getElementById('latitudSeleccionada');
                const lngSpan = document.getElementById('longitudSeleccionada');
                
                if (latSpan) latSpan.textContent = lat;
                if (lngSpan) lngSpan.textContent = lng;
                
                // Actualizar visibilidad del panel de coordenadas
                const coordenadasDiv = document.getElementById('coordenadasSeleccionadas');
                if (coordenadasDiv) {
                    coordenadasDiv.style.display = 'block';
                }
                
                // Actualizar o crear marcador
                if (simuladorMarker) {
                    simuladorMarker.setLatLng([lat, lng]);
                } else {
                    simuladorMarker = L.marker([lat, lng]).addTo(simuladorMap);
                }
                
                // Mostrar botón para usar coordenadas
                const usarBtn = document.getElementById('usarCoordenadas');
                if (usarBtn) {
                    usarBtn.style.display = 'inline-block';
                    usarBtn.classList.remove('d-none');
                }
            });
            
            // Marcar que el mapa se ha inicializado
            mapHasBeenInitialized = true;
            mapInitAttempts = 0;
            
            // Ocultar indicador de carga
            if (indicadorCarga) {
                indicadorCarga.style.display = 'none';
            }
            
            // Agregar botón para centrar en Argentina
            const centrarBtn = document.getElementById('centrarEnArgentina');
            if (centrarBtn) {
                centrarBtn.addEventListener('click', function() {
                    if (simuladorMap) {
                        simuladorMap.setView([-38.416097, -63.616672], 4);
                    }
                });
            }
            
            console.log("Mapa inicializado correctamente");
            return simuladorMap;
        } catch (error) {
            console.error("Error al inicializar el mapa:", error);
            
            // Si han habido demasiados intentos, mostrar error
            if (mapInitAttempts >= 3) {
                mostrarErrorMapa("Error al cargar el mapa después de múltiples intentos. Por favor, recargue la página o intente más tarde.");
                return null;
            }
            
            // Intentar una vez más con un retraso
            console.log("Reintentando inicialización del mapa en 1 segundo");
            setTimeout(cargarLeaflet, 1000);
            return null;
        }
    };
    
    // Ejecutar inicialización con un pequeño retraso para permitir que el DOM esté listo
    setTimeout(iniciarMapa, 200);
}

// Función para mostrar mensaje de error del mapa
function mostrarErrorMapa(mensaje) {
    console.error("Error de mapa:", mensaje);
    
    const errorMsg = document.getElementById('location-error-message');
    const mapaDiv = document.getElementById('mapaUbicacion');
    const indicadorCarga = document.getElementById('map-loading-indicator');
    
    // Determinar si es dispositivo móvil
    const esMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
                    window.innerWidth <= 768;
    
    // Personalizar mensaje para dispositivos móviles
    let mensajeError = mensaje;
    if (esMobile && !mensaje.includes("móvil")) {
        mensajeError = "Error al cargar el mapa en dispositivo móvil. Intente con WiFi o recargar la página.";
    }
    
    // Ocultar indicador de carga
    if (indicadorCarga) {
        indicadorCarga.style.display = 'none';
    }
    
    // Mostrar mensaje en el contenedor de error
    if (errorMsg) {
        errorMsg.style.display = 'block';
        const errorText = errorMsg.querySelector('#error-text');
        if (errorText) {
            errorText.textContent = mensajeError;
        }
    }
    
    // Mostrar mensaje en el contenedor del mapa
    if (mapaDiv) {
        mapaDiv.innerHTML = `
            <div class="alert alert-danger p-3 m-0">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${mensajeError}
                <br>
                <button type="button" class="btn btn-sm btn-outline-danger mt-2" onclick="window.location.reload()">
                    Recargar página
                </button>
                ${esMobile ? '<br><small class="d-block mt-2">Consejo: Las conexiones WiFi suelen funcionar mejor para cargar mapas.</small>' : ''}
            </div>
        `;
    }
    
    // Asegurar que el botón de reinicio esté visible en dispositivos móviles
    if (esMobile) {
        const helperDiv = document.getElementById('mobile-map-helper');
        if (helperDiv) {
            helperDiv.classList.remove('d-none', 'd-sm-none');
        }
    }
}

// Función global para reiniciar el mapa
function reiniciarMapa() {
    console.log("Reiniciando mapa del simulador");
    
    // Limpiar simuladorMap si existe
    if (simuladorMap) {
        try {
            simuladorMap.remove();
        } catch (e) {
            console.warn("Error al eliminar mapa existente:", e);
        }
        simuladorMap = null;
    }
    
    // Limpiar marcador si existe
    simuladorMarker = null;
    
    // Reiniciar estado
    mapHasBeenInitialized = false;
    mapInitAttempts = 0;
    
    // Limpiar el div del mapa
    const mapaDiv = document.getElementById('mapaUbicacion');
    if (mapaDiv) {
        while (mapaDiv.firstChild) {
            mapaDiv.removeChild(mapaDiv.firstChild);
        }
    }
    
    // Ocultar mensajes de error
    const errorMsg = document.getElementById('location-error-message');
    if (errorMsg) {
        errorMsg.style.display = 'none';
    }
    
    // Inicializar nuevamente
    setTimeout(cargarLeaflet, 500);
}

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM cargado, preparando mapa para simulador");
    
    // Inicializar mapa con un pequeño retraso para asegurar carga completa
    setTimeout(cargarLeaflet, 500);
    
    // Configurar botón para usar coordenadas
    const usarCoordenadasBtn = document.getElementById('usarCoordenadas');
    if (usarCoordenadasBtn) {
        usarCoordenadasBtn.addEventListener('click', function() {
            // Verificar si se han seleccionado coordenadas
            const latInput = document.getElementById('latitud');
            const lngInput = document.getElementById('longitud');
            
            if (latInput && latInput.value && lngInput && lngInput.value) {
                // Ocultar cualquier mensaje de error
                const errorMsg = document.getElementById('location-error-message');
                if (errorMsg) {
                    errorMsg.style.display = 'none';
                }
                
                // Mostrar mensaje de éxito
                alert('Ubicación seleccionada correctamente. Continue con el formulario.');
            } else {
                alert('Por favor, seleccione una ubicación en el mapa primero.');
            }
        });
    }
    
    // Configurar botón de reinicio para dispositivos móviles
    const resetBtn = document.getElementById('reiniciarMapaBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', reiniciarMapa);
    }
    
    // Detectar si es dispositivo móvil para mostrar el botón de reinicio
    const esMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
                     window.innerWidth <= 768;
    
    if (esMobile) {
        const helperDiv = document.getElementById('mobile-map-helper');
        if (helperDiv) {
            helperDiv.classList.remove('d-none', 'd-sm-none');
        }
    }
});