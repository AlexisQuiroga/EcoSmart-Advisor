/**
 * Script auxiliar para operaciones de mapa
 * Proporciona funciones de debug y compatibilidad
 */

// Cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log("Inicializando helper de mapa...");
    
    // Verificar que las funciones del mapa estén disponibles
    const funciones = [
        "toggleMap", 
        "initMap", 
        "setupMapClickEvent", 
        "addOrUpdateMarker"
    ];
    
    const funcionesFaltantes = funciones.filter(f => typeof window[f] !== 'function');
    
    if (funcionesFaltantes.length > 0) {
        console.error("Funciones de mapa faltantes:", funcionesFaltantes);
        
        // Definir funciones de emergencia si faltan
        if (typeof window.toggleMap !== 'function') {
            console.log("Definiendo toggleMap de emergencia");
            window.toggleMap = function(containerId) {
                const container = document.getElementById(containerId);
                if (!container) return false;
                const isHidden = container.style.display === 'none';
                container.style.display = isHidden ? 'block' : 'none';
                return isHidden;
            };
        }
        
        if (typeof window.initMap !== 'function') {
            console.log("Definiendo initMap de emergencia");
            window.initMap = function(containerId) {
                const container = document.getElementById(containerId);
                if (!container) return null;
                
                try {
                    if (typeof L === 'undefined') {
                        console.error("Leaflet no está disponible");
                        return null;
                    }
                    
                    // Centrar en Argentina por defecto
                    const map = L.map(containerId).setView([-38.416097, -63.616672], 4);
                    
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                        maxZoom: 19
                    }).addTo(map);
                    
                    return map;
                } catch (e) {
                    console.error("Error inicializando mapa:", e);
                    return null;
                }
            };
        }
        
        if (typeof window.setupMapClickEvent !== 'function') {
            console.log("Definiendo setupMapClickEvent de emergencia");
            window.setupMapClickEvent = function(map, callback) {
                if (!map) return;
                
                map.on('click', function(e) {
                    if (typeof callback === 'function') {
                        callback(e.latlng.lat, e.latlng.lng, null);
                    }
                });
            };
        }
        
        if (typeof window.addOrUpdateMarker !== 'function') {
            console.log("Definiendo addOrUpdateMarker de emergencia");
            window.addOrUpdateMarker = function(map, lat, lng, zoom = 15) {
                if (!map) return null;
                
                try {
                    // Parsear coordenadas
                    lat = parseFloat(lat);
                    lng = parseFloat(lng);
                    
                    if (isNaN(lat) || isNaN(lng)) return null;
                    
                    // Si ya existe un marcador global, eliminarlo
                    if (window._ecosmartMarker) {
                        window._ecosmartMarker.remove();
                    }
                    
                    // Crear nuevo marcador
                    window._ecosmartMarker = L.marker([lat, lng]).addTo(map);
                    map.setView([lat, lng], zoom);
                    
                    return window._ecosmartMarker;
                } catch (e) {
                    console.error("Error al crear marcador:", e);
                    return null;
                }
            };
        }
    } else {
        console.log("Todas las funciones de mapa están disponibles");
    }
    
    // Verificar el botón del mapa
    const toggleMapBtn = document.getElementById('toggleMapBtn');
    if (toggleMapBtn) {
        console.log("Botón de mapa encontrado");
        
        // Añadir un listener de emergencia por si falla el original
        toggleMapBtn.addEventListener('dblclick', function(e) {
            console.log("Click de emergencia en botón de mapa");
            const mapaUbicacion = document.getElementById('mapaUbicacion');
            
            if (mapaUbicacion) {
                const isHidden = mapaUbicacion.style.display === 'none';
                mapaUbicacion.style.display = isHidden ? 'block' : 'none';
                
                if (isHidden && typeof L !== 'undefined') {
                    try {
                        const map = L.map('mapaUbicacion').setView([-38.416097, -63.616672], 4);
                        
                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        }).addTo(map);
                        
                        console.log("Mapa inicializado en modo emergencia");
                    } catch (e) {
                        console.error("Error en inicialización de emergencia:", e);
                    }
                }
            }
        });
    } else {
        console.warn("Botón de mapa no encontrado");
    }
});