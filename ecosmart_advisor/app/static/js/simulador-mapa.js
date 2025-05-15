/**
 * Script específico para manejar el mapa en la página del simulador
 */

// Función para cargar el mapa Leaflet en el simulador
function cargarLeaflet() {
    console.log("Iniciando carga de mapa Leaflet para simulador");
    
    try {
        // Verificar si Leaflet está disponible
        if (typeof L === 'undefined') {
            console.error("Error: Leaflet no está disponible");
            mostrarErrorMapa("No se pudo cargar la biblioteca de mapas. Por favor, recargue la página.");
            return null;
        }
        
        // Obtener referencias a elementos del DOM
        const mapaDiv = document.getElementById('mapaUbicacion');
        const indicadorCarga = document.getElementById('map-loading-indicator');
        
        if (!mapaDiv) {
            console.error("No se encontró el contenedor del mapa");
            return null;
        }
        
        // Mostrar indicador de carga
        if (indicadorCarga) {
            indicadorCarga.style.display = 'block';
        }
        
        // Inicializar mapa centrado en Argentina
        console.log("Creando instancia del mapa Leaflet");
        const map = L.map('mapaUbicacion').setView([-38.416097, -63.616672], 4);
        
        // Agregar capa de mapa base
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 19
        }).addTo(map);
        
        // Configurar evento de clic en el mapa
        map.on('click', function(e) {
            const lat = parseFloat(e.latlng.lat.toFixed(6));
            const lng = parseFloat(e.latlng.lng.toFixed(6));
            
            console.log("Clic en el mapa en:", lat, lng);
            
            // Actualizar los campos de formulario
            document.getElementById('latitud').value = lat;
            document.getElementById('longitud').value = lng;
            
            // Actualizar la información mostrada
            if (document.getElementById('latitudSeleccionada')) {
                document.getElementById('latitudSeleccionada').textContent = lat;
            }
            if (document.getElementById('longitudSeleccionada')) {
                document.getElementById('longitudSeleccionada').textContent = lng;
            }
            
            // Actualizar visibilidad del panel de coordenadas
            const coordenadasDiv = document.getElementById('coordenadasSeleccionadas');
            if (coordenadasDiv) {
                coordenadasDiv.style.display = 'block';
            }
            
            // Actualizar o crear marcador
            if (window.marker) {
                window.marker.setLatLng([lat, lng]);
            } else {
                window.marker = L.marker([lat, lng]).addTo(map);
            }
            
            // Mostrar botón para usar coordenadas
            const usarBtn = document.getElementById('usarCoordenadas');
            if (usarBtn) {
                usarBtn.style.display = 'inline-block';
                usarBtn.classList.remove('d-none');
            }
        });
        
        // Ocultar indicador de carga
        if (indicadorCarga) {
            indicadorCarga.style.display = 'none';
        }
        
        console.log("Mapa inicializado correctamente");
        return map;
    } catch (error) {
        console.error("Error al cargar el mapa:", error);
        mostrarErrorMapa("Error al inicializar el mapa: " + error.message);
        return null;
    }
}

// Función para mostrar mensaje de error del mapa
function mostrarErrorMapa(mensaje) {
    const errorMsg = document.getElementById('location-error-message');
    const mapaDiv = document.getElementById('mapaUbicacion');
    const indicadorCarga = document.getElementById('map-loading-indicator');
    
    // Ocultar indicador de carga
    if (indicadorCarga) {
        indicadorCarga.style.display = 'none';
    }
    
    // Mostrar mensaje en el contenedor de error
    if (errorMsg) {
        errorMsg.style.display = 'block';
        const errorText = errorMsg.querySelector('#error-text');
        if (errorText) {
            errorText.textContent = mensaje;
        }
    }
    
    // Mostrar mensaje en el contenedor del mapa
    if (mapaDiv) {
        mapaDiv.innerHTML = `
            <div class="alert alert-danger p-3 m-0">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${mensaje}
                <br>
                <button type="button" class="btn btn-sm btn-outline-danger mt-2" onclick="window.location.reload()">
                    Recargar página
                </button>
            </div>
        `;
    }
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
            
            if (latInput.value && lngInput.value) {
                // Ocultar cualquier mensaje de error
                const errorMsg = document.getElementById('location-error-message');
                if (errorMsg) {
                    errorMsg.style.display = 'none';
                }
                
                // Mostrar mensaje de éxito
                alert('Ubicación seleccionada correctamente. Continúe con el formulario.');
            } else {
                alert('Por favor, seleccione una ubicación en el mapa primero.');
            }
        });
    }
});