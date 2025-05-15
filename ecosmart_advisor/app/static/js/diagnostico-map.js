/**
 * Script para la inicialización y manejo del mapa en la página de diagnóstico
 * Este script se carga específicamente en la página de diagnóstico.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("Inicializando mapa en diagnóstico (archivo externo)...");
    
    // Elementos del DOM
    const coordenadasSeleccionadas = document.getElementById('coordenadasSeleccionadas');
    const ubicacionDescripcion = document.getElementById('ubicacionDescripcion');
    const latitudSeleccionada = document.getElementById('latitudSeleccionada');
    const longitudSeleccionada = document.getElementById('longitudSeleccionada');
    const latitudInput = document.getElementById('latitud');
    const longitudInput = document.getElementById('longitud');
    const descripcionUbicacionInput = document.getElementById('descripcion_ubicacion');
    const centrarEnArgentinaBtn = document.getElementById('centrarEnArgentina');
    const usarCoordenadasBtn = document.getElementById('usarCoordenadas');
    const paisInput = document.getElementById('pais');
    const provinciaInput = document.getElementById('provincia');
    const ciudadInput = document.getElementById('ciudad');
    const direccionInput = document.getElementById('direccion');
    const ubicacionInput = document.getElementById('ubicacion');
    
    // Asegurar que el contenedor del mapa esté visible y con altura
    const mapaDiv = document.getElementById('mapaUbicacion');
    if (mapaDiv) {
        mapaDiv.style.display = 'block';
        mapaDiv.style.height = '400px';
    }
    
    // Inicializar el mapa directamente con mapa-simple.js
    // La función initMap está definida en mapa-simple.js
    const map = initMap('mapaUbicacion');
    
    // Hacer el mapa accesible globalmente para depuración
    window.diagnosticoMap = map;
    
    if (map) {
        console.log("✅ Mapa inicializado correctamente en diagnóstico");
        
        // Configurar evento de clic en el mapa
        map.on('click', function(e) {
            // Obtener coordenadas del clic
            const lat = e.latlng.lat;
            const lng = e.latlng.lng;
            
            console.log("Clic en mapa de diagnóstico:", lat, lng);
            
            // Actualizar el marcador usando mapa-simple.js
            updateMarker(map, lat, lng);
            
            // Actualizar los campos ocultos
            if (latitudInput) latitudInput.value = lat;
            if (longitudInput) longitudInput.value = lng;
            
            // Actualizar la visualización de coordenadas
            if (latitudSeleccionada) latitudSeleccionada.textContent = lat.toFixed(6);
            if (longitudSeleccionada) longitudSeleccionada.textContent = lng.toFixed(6);
            
            // Mostrar el panel de coordenadas
            if (coordenadasSeleccionadas) {
                coordenadasSeleccionadas.classList.remove('d-none');
            }
            
            // Realizar geocodificación inversa
            if (ubicacionDescripcion) {
                ubicacionDescripcion.textContent = 'Obteniendo dirección...';
                
                reverseGeocode(lat, lng, function(data) {
                    if (data && data.display_name) {
                        console.log("Datos de geocodificación:", data);
                        const addressText = data.display_name;
                        
                        // Actualizar la descripción visible
                        if (ubicacionDescripcion) {
                            ubicacionDescripcion.textContent = addressText;
                        }
                        
                        // Guardar la descripción en el campo oculto
                        if (descripcionUbicacionInput) {
                            descripcionUbicacionInput.value = addressText;
                        }
                        
                        // Actualizar campos individuales de dirección
                        if (data.address) {
                            const addr = data.address;
                            
                            // Actualizar país
                            if (paisInput && addr.country) {
                                paisInput.value = addr.country;
                            }
                            
                            // Actualizar provincia
                            if (provinciaInput) {
                                let provincia = addr.state || addr.province || addr.region || '';
                                if (provincia) provinciaInput.value = provincia;
                            }
                            
                            // Actualizar ciudad
                            if (ciudadInput) {
                                let ciudad = addr.city || addr.town || addr.village || addr.hamlet || addr.municipality || '';
                                if (ciudad) ciudadInput.value = ciudad;
                            }
                            
                            // Actualizar dirección
                            if (direccionInput) {
                                let direccionCompleta = '';
                                
                                if (addr.road) {
                                    direccionCompleta += addr.road;
                                    if (addr.house_number) {
                                        direccionCompleta += ' ' + addr.house_number;
                                    }
                                }
                                
                                if (addr.suburb && !direccionCompleta.includes(addr.suburb)) {
                                    direccionCompleta += (direccionCompleta ? ', ' : '') + addr.suburb;
                                }
                                
                                if (direccionCompleta) {
                                    direccionInput.value = direccionCompleta;
                                }
                            }
                            
                            // Actualizar campos ocultos
                            const ubicacionCompleta = data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
                            if (ubicacionInput) {
                                ubicacionInput.value = ubicacionCompleta;
                            }
                        }
                    } else {
                        if (ubicacionDescripcion) {
                            ubicacionDescripcion.textContent = 'No se pudo obtener la dirección';
                        }
                    }
                });
            }
        });
        
        // Configurar botón para centrar en Argentina
        if (centrarEnArgentinaBtn) {
            centrarEnArgentinaBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log("Centrando mapa en Argentina");
                // Centrar en Argentina
                map.setView([-34.603722, -58.381592], 5);
            });
        }
        
        // Configurar botón para usar coordenadas
        if (usarCoordenadasBtn) {
            usarCoordenadasBtn.addEventListener('click', function() {
                console.log("Confirmando uso de coordenadas seleccionadas...");
                
                // Scroll hasta el siguiente paso
                const tipoViviendaField = document.getElementById('tipo_vivienda');
                if (tipoViviendaField) {
                    tipoViviendaField.scrollIntoView({ behavior: 'smooth' });
                    tipoViviendaField.focus();
                }
                
                // Ocultar mensaje de error si estaba visible
                const errorMsgEl = document.getElementById('location-error-message');
                if (errorMsgEl) {
                    errorMsgEl.style.display = 'none';
                }
            });
        }
    } else {
        console.error("❌ No se pudo inicializar el mapa en diagnóstico");
    }
    
    // Validación del formulario
    const formulario = document.getElementById('diagnosticoForm');
    if (formulario) {
        formulario.addEventListener('submit', function(event) {
            // Validar que tengamos coordenadas
            const latitud = latitudInput.value;
            const longitud = longitudInput.value;
            
            if (!latitud || !longitud) {
                event.preventDefault();
                alert('Por favor, seleccione su ubicación en el mapa.');
                
                // Mostrar mensaje de error
                const errorMsgEl = document.getElementById('location-error-message');
                const errorTextEl = document.getElementById('error-text');
                if (errorMsgEl && errorTextEl) {
                    errorTextEl.textContent = 'Debe seleccionar una ubicación en el mapa para continuar.';
                    errorMsgEl.style.display = 'block';
                }
                
                return false;
            }
            
            // Validar otros campos requeridos
            const tipoVivienda = document.getElementById('tipo_vivienda').value;
            const superficie = document.getElementById('superficie_disponible').value;
            const objetivo = document.getElementById('objetivo').value;
            
            if (!tipoVivienda || !superficie || !objetivo) {
                event.preventDefault();
                alert('Por favor, complete todos los campos obligatorios.');
                return false;
            }
            
            // Validar superficie (valor numérico positivo)
            const superficieNum = parseFloat(superficie);
            if (isNaN(superficieNum) || superficieNum <= 0) {
                event.preventDefault();
                alert('Por favor, ingrese un valor válido para la superficie disponible.');
                return false;
            }
            
            return true;
        });
    }
});