/**
 * Script simplificado para manejar el mapa de selección de ubicación
 * Este script reemplaza la compleja implementación anterior
 */

document.addEventListener('DOMContentLoaded', function() {
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
    const diagnosticoForm = document.getElementById('diagnosticoForm');
    
    // Variables globales
    let map = null;
    let marker = null;
    let selectedLat = null;
    let selectedLng = null;
    
    // Coordenadas por defecto (centro de Argentina)
    const ARGENTINA_LAT = -38.416097;
    const ARGENTINA_LNG = -63.616672;
    const ARGENTINA_ZOOM = 4;
    
    // Mostrar indicador de carga
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    
    // Inicializar mapa si tenemos el contenedor
    if (mapaUbicacionDiv) {
        try {
            // Inicializar el mapa con Leaflet
            map = L.map('mapaUbicacion').setView([ARGENTINA_LAT, ARGENTINA_LNG], ARGENTINA_ZOOM);
            
            // Agregar capa de mosaicos (tiles)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                maxZoom: 19
            }).addTo(map);
            
            // Ocultar indicador de carga
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
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
            });
            
            console.log("Mapa inicializado correctamente");
        } catch (error) {
            console.error("Error al inicializar el mapa:", error);
            
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
            }
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
    
    // Botón para centrar mapa en Argentina
    if (centrarEnArgentinaBtn) {
        centrarEnArgentinaBtn.addEventListener('click', function() {
            if (map) {
                map.setView([ARGENTINA_LAT, ARGENTINA_LNG], ARGENTINA_ZOOM);
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
                    ubicacionInput.value = `${selectedLat},${selectedLng}`;
                }
                
                // Indicación visual de que se han confirmado las coordenadas
                usarCoordenadasBtn.innerHTML = '<i class="fas fa-check me-1"></i>Ubicación confirmada';
                usarCoordenadasBtn.classList.remove('btn-success');
                usarCoordenadasBtn.classList.add('btn-outline-success');
                
                // Opcional: Mostrar mensaje de confirmación
                alert('Ubicación confirmada correctamente. Puede continuar con el resto del formulario.');
            }
        });
    }
    
    // Validar que se hayan seleccionado coordenadas antes de enviar el formulario
    if (diagnosticoForm) {
        diagnosticoForm.addEventListener('submit', function(e) {
            if (!selectedLat || !selectedLng || !ubicacionInput.value) {
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
                mapaUbicacionDiv.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
});