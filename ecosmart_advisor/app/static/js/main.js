
// Configuración del mapa interactivo y autocompletado por sectores
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a campos del formulario de ubicación
    const provinciaInput = document.getElementById('provincia');
    const ciudadInput = document.getElementById('ciudad');
    const direccionInput = document.getElementById('direccion');
    const ubicacionInput = document.getElementById('ubicacion'); // Campo oculto para el valor completo
    
    // Referencias a contenedores de sugerencias
    const sugerenciasProvinciaDiv = document.getElementById('sugerenciasProvincia');
    const sugerenciasCiudadDiv = document.getElementById('sugerenciasCiudad');
    
    // Referencias a elementos del mapa
    const mostrarMapaBtn = document.getElementById('mostrarMapa');
    const mapaUbicacionDiv = document.getElementById('mapaUbicacion');
    const coordenadasDiv = document.getElementById('coordenadasSeleccionadas');
    const latitudSpan = document.getElementById('latitudSeleccionada');
    const longitudSpan = document.getElementById('longitudSeleccionada');
    const usarCoordenadasBtn = document.getElementById('usarCoordenadas');
    
    // Variables para el mapa
    let map, marker;
    let selectedLat, selectedLng;
    
    // Función para actualizar el campo oculto de ubicación completa
    function actualizarUbicacionCompleta() {
        const provincia = provinciaInput.value.trim();
        const ciudad = ciudadInput.value.trim();
        const direccion = direccionInput.value.trim();
        
        let ubicacionCompleta = '';
        
        if (direccion) {
            ubicacionCompleta += direccion + ', ';
        }
        
        if (ciudad) {
            ubicacionCompleta += ciudad + ', ';
        }
        
        if (provincia) {
            ubicacionCompleta += provincia;
        }
        
        // Eliminar la coma final si es necesario
        ubicacionCompleta = ubicacionCompleta.replace(/,\s*$/, '');
        
        // Asignar al campo oculto
        if (ubicacionCompleta) {
            ubicacionInput.value = ubicacionCompleta;
        }
    }
    
    // Función genérica para manejar autocompletado de un campo usando OpenCage
    async function manejarAutocompletado(inputElement, sugerenciasDiv, tipo) {
        const texto = inputElement.value;
        if (texto.length < 2) { // Reducido a 2 caracteres para mejor experiencia
            sugerenciasDiv.style.display = 'none';
            return;
        }

        try {
            // Construir consulta para OpenCage a través de nuestro proxy
            let consulta = texto;
            
            // Agregar contexto adicional según el tipo de campo
            if (tipo === 'provincia') {
                consulta = `${texto}, Argentina`;
            } else if (tipo === 'ciudad') {
                // Si hay provincia seleccionada, agregar contexto
                if (provinciaInput.value) {
                    consulta = `${texto}, ${provinciaInput.value}, Argentina`;
                } else {
                    consulta = `${texto}, Argentina`;
                }
            } else if (tipo === 'direccion') {
                // Para direcciones, combinar con ciudad y provincia si están disponibles
                let contextoDireccion = '';
                if (ciudadInput.value) {
                    contextoDireccion += ciudadInput.value;
                    
                    if (provinciaInput.value) {
                        contextoDireccion += `, ${provinciaInput.value}`;
                    }
                } else if (provinciaInput.value) {
                    contextoDireccion = provinciaInput.value;
                }
                
                if (contextoDireccion) {
                    consulta = `${texto}, ${contextoDireccion}, Argentina`;
                } else {
                    consulta = `${texto}, Argentina`;
                }
            }
            
            console.log(`Buscando '${consulta}' usando OpenCage`);
            
            // Usar nuestro endpoint API proxy para OpenCage
            const response = await fetch(`/api/geocode?q=${encodeURIComponent(consulta)}&limit=5`);
            const data = await response.json();
            
            // Limpiar resultados anteriores
            sugerenciasDiv.innerHTML = '';
            
            if (data.results && data.results.length > 0) {
                // Filtrar y procesar resultados según el tipo de campo
                const resultadosFiltrados = data.results.filter(result => {
                    // Para provincias, solo mostrar estados/provincias
                    if (tipo === 'provincia') {
                        return result.components && 
                              (result.components.state && !result.components.city && !result.components.street);
                    }
                    // Para ciudades, solo mostrar ciudades
                    else if (tipo === 'ciudad') {
                        return result.components && 
                              (result.components.city || result.components.town || result.components.village) &&
                              !result.components.street;
                    }
                    // Para direcciones, privilegiar resultados con calle
                    else if (tipo === 'direccion') {
                        // Mayor prioridad a resultados con calle y número
                        return result.components && result.components.street;
                    }
                    return true;
                });
                
                // Si no hay resultados filtrados, usar todos los resultados
                const resultadosAMostrar = resultadosFiltrados.length > 0 ? resultadosFiltrados : data.results;
                
                // Mostrar resultados en el div de sugerencias
                resultadosAMostrar.slice(0, 5).forEach(result => {
                    const div = document.createElement('div');
                    div.className = 'list-group-item list-group-item-action';
                    
                    // Formatear el texto mostrado según el tipo
                    let nombreMostrado = '';
                    if (tipo === 'provincia') {
                        nombreMostrado = result.components?.state || result.formatted.split(',')[0];
                    } else if (tipo === 'ciudad') {
                        nombreMostrado = result.components?.city || 
                                        result.components?.town || 
                                        result.components?.village || 
                                        result.formatted.split(',')[0];
                    } else if (tipo === 'direccion') {
                        // Para direcciones, mostrar calle y número
                        if (result.components?.street) {
                            nombreMostrado = `${result.components.street}`;
                            if (result.components?.number) {
                                nombreMostrado += ` ${result.components.number}`;
                            }
                        } else {
                            // Si no hay calle, usar primera parte del formatted
                            nombreMostrado = result.formatted.split(',')[0];
                        }
                    }
                    
                    div.textContent = nombreMostrado;
                    div.dataset.lat = result.lat;
                    div.dataset.lng = result.lng;
                    div.dataset.formatted = result.formatted;
                    
                    // Almacenar más datos para uso posterior
                    if (result.components) {
                        if (result.components.street) div.dataset.street = result.components.street;
                        if (result.components.number) div.dataset.number = result.components.number;
                        if (result.components.city) div.dataset.city = result.components.city;
                        if (result.components.state) div.dataset.state = result.components.state;
                    }
                    
                    div.addEventListener('click', () => {
                        inputElement.value = nombreMostrado;
                        sugerenciasDiv.style.display = 'none';
                        
                        // Actualizar datos según el tipo seleccionado
                        if (tipo === 'provincia') {
                            provinciaInput.value = nombreMostrado;
                            
                            // Si cambia la provincia, limpiar ciudad y dirección
                            ciudadInput.value = '';
                            direccionInput.value = '';
                        } 
                        else if (tipo === 'ciudad') {
                            ciudadInput.value = nombreMostrado;
                            
                            // Si está la provincia en el resultado y no coincide, actualizar
                            if (div.dataset.state && 
                                provinciaInput.value.trim() !== div.dataset.state && 
                                div.dataset.state.trim() !== '') {
                                provinciaInput.value = div.dataset.state;
                            }
                            
                            // Limpiar dirección si cambia la ciudad
                            direccionInput.value = '';
                        }
                        else if (tipo === 'direccion') {
                            direccionInput.value = nombreMostrado;
                            
                            // Actualizar ciudad y provincia si están en el resultado
                            if (div.dataset.city && ciudadInput.value.trim() === '') {
                                ciudadInput.value = div.dataset.city;
                            }
                            if (div.dataset.state && provinciaInput.value.trim() === '') {
                                provinciaInput.value = div.dataset.state;
                            }
                        }
                        
                        // Guardar coordenadas para el mapa
                        inputElement.dataset.lat = div.dataset.lat;
                        inputElement.dataset.lon = div.dataset.lng;
                        selectedLat = div.dataset.lat;
                        selectedLng = div.dataset.lng;
                        
                        // Actualizar campos ocultos de latitud y longitud
                        if (document.getElementById('latitud')) {
                            document.getElementById('latitud').value = selectedLat;
                        }
                        if (document.getElementById('longitud')) {
                            document.getElementById('longitud').value = selectedLng;
                        }
                        
                        // Actualizar ubicación completa
                        actualizarUbicacionCompleta();
                        
                        // Evento para desencadenar validación del formulario
                        const event = new Event('change', { bubbles: true });
                        inputElement.dispatchEvent(event);
                    });
                    
                    sugerenciasDiv.appendChild(div);
                });
                
                sugerenciasDiv.style.display = 'block';
            } else {
                sugerenciasDiv.style.display = 'none';
            }
        } catch (error) {
            console.error('Error en autocompletado:', error);
            sugerenciasDiv.style.display = 'none';
            
            // Intentar con el método antiguo como fallback
            try {
                // Construir la consulta dependiendo del tipo (provincia o ciudad)
                let url = `https://nominatim.openstreetmap.org/search?format=json&q=${texto}`;
                if (tipo === 'provincia') {
                    url += '&featureType=state';
                } else if (tipo === 'ciudad') {
                    url += '&featureType=city';
                    // Si hay provincia seleccionada, filtrar por ella
                    if (provinciaInput.value) {
                        url += `&state=${encodeURIComponent(provinciaInput.value)}`;
                    }
                }
                
                const response = await fetch(url);
                const data = await response.json();
                
                sugerenciasDiv.innerHTML = '';
                data.slice(0, 5).forEach(lugar => {
                    const div = document.createElement('div');
                    div.className = 'list-group-item list-group-item-action';
                    
                    // Mostrar solo el nombre relevante, no la dirección completa
                    let nombreMostrado = '';
                    if (tipo === 'provincia') {
                        // Extraer solo el nombre de la provincia/estado
                        nombreMostrado = lugar.address?.state || lugar.display_name.split(',')[0];
                    } else if (tipo === 'ciudad') {
                        // Extraer solo el nombre de la ciudad/localidad
                        nombreMostrado = lugar.address?.city || lugar.address?.town || lugar.address?.village || lugar.display_name.split(',')[0];
                    }
                    
                    div.textContent = nombreMostrado;
                    div.dataset.lat = lugar.lat;
                    div.dataset.lon = lugar.lon;
                    
                    div.addEventListener('click', () => {
                        inputElement.value = nombreMostrado;
                        sugerenciasDiv.style.display = 'none';
                        
                        // Almacenar coordenadas para posible uso en el mapa
                        inputElement.dataset.lat = lugar.lat;
                        inputElement.dataset.lon = lugar.lon;
                        
                        // Si seleccionamos una provincia, limpiar la ciudad
                        if (tipo === 'provincia') {
                            ciudadInput.value = '';
                        }
                        
                        // Actualizar ubicación completa
                        actualizarUbicacionCompleta();
                    });
                    
                    sugerenciasDiv.appendChild(div);
                });
                
                if (data.length > 0) {
                    sugerenciasDiv.style.display = 'block';
                }
            } catch (fallbackError) {
                console.error('Error en método de fallback:', fallbackError);
            }
        }
    }
    
    // Configurar eventos de autocompletado para provincia
    if (provinciaInput) {
        provinciaInput.addEventListener('input', function() {
            manejarAutocompletado(provinciaInput, sugerenciasProvinciaDiv, 'provincia');
        });
        
        // Ocultar sugerencias al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (e.target !== provinciaInput && e.target !== sugerenciasProvinciaDiv) {
                sugerenciasProvinciaDiv.style.display = 'none';
            }
        });
    }
    
    // Configurar eventos de autocompletado para ciudad
    if (ciudadInput) {
        ciudadInput.addEventListener('input', function() {
            manejarAutocompletado(ciudadInput, sugerenciasCiudadDiv, 'ciudad');
        });
        
        // Ocultar sugerencias al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (e.target !== ciudadInput && e.target !== sugerenciasCiudadDiv) {
                sugerenciasCiudadDiv.style.display = 'none';
            }
        });
    }
    
    // Actualizar ubicación completa cuando se modifique cualquier campo
    if (direccionInput) {
        direccionInput.addEventListener('input', actualizarUbicacionCompleta);
    }
    
    // Inicializar mapa interactivo
    if (mostrarMapaBtn && mapaUbicacionDiv) {
        mostrarMapaBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Click en botón mostrar/ocultar mapa");
            
            // Usar la función de toggleMap de leaflet-map.js
            const isVisible = toggleMap('mapaUbicacion');
            
            // Si el mapa está visible ahora, inicializarlo y configurar eventos
            if (isVisible) {
                // Inicializar el mapa usando la función de leaflet-map.js
                const map = initMap('mapaUbicacion');
                
                if (map) {
                    // Configurar evento de click usando la función de leaflet-map.js
                    setupMapClickEvent(map, function(lat, lng, addressData) {
                        console.log("Click en el mapa detectado:", lat, lng);
                        
                        // Actualizar coordenadas mostradas
                        selectedLat = lat;
                        selectedLng = lng;
                        
                        if (latitudSpan && longitudSpan) {
                            latitudSpan.textContent = lat;
                            longitudSpan.textContent = lng;
                            
                            // Mostrar el panel de coordenadas
                            if (coordenadasDiv) {
                                coordenadasDiv.style.display = 'flex';
                            }
                        }
                        
                        // Actualizar campos ocultos de coordenadas si existen
                        const latitudInput = document.getElementById('latitud');
                        const longitudInput = document.getElementById('longitud');
                        
                        if (latitudInput) latitudInput.value = lat;
                        if (longitudInput) longitudInput.value = lng;
                        
                        // Si tenemos datos de dirección de la geocodificación inversa
                        if (addressData && addressData.address) {
                            console.log("Datos de dirección:", addressData.address);
                            
                            // Actualizar campos de dirección si corresponde
                            if (direccionInput && addressData.address.road) {
                                let direccionTexto = addressData.address.road;
                                if (addressData.address.house_number) {
                                    direccionTexto += " " + addressData.address.house_number;
                                }
                                direccionInput.value = direccionTexto;
                            }
                            
                            // Actualizar ciudad si corresponde
                            if (ciudadInput && 
                                (addressData.address.city || 
                                 addressData.address.town || 
                                 addressData.address.village)) {
                                ciudadInput.value = addressData.address.city || 
                                                    addressData.address.town || 
                                                    addressData.address.village;
                            }
                            
                            // Actualizar provincia si corresponde
                            if (provinciaInput && addressData.address.state) {
                                provinciaInput.value = addressData.address.state;
                            }
                            
                            // Actualizar ubicación completa
                            actualizarUbicacionCompleta();
                        }
                    });
                    
                    // Centrar en lugar específico si hay datos
                    if (selectedLat && selectedLng) {
                        // Usar el marcador existente en ecosmartMarker
                        addOrUpdateMarker(map, selectedLat, selectedLng, 15);
                    } 
                    // Si hay coordenadas en los campos de ciudad o provincia, usarlas
                    else if (ciudadInput && ciudadInput.dataset.lat && ciudadInput.dataset.lon) {
                        addOrUpdateMarker(map, 
                                        parseFloat(ciudadInput.dataset.lat), 
                                        parseFloat(ciudadInput.dataset.lon), 12);
                    } 
                    else if (provinciaInput && provinciaInput.dataset.lat && provinciaInput.dataset.lon) {
                        addOrUpdateMarker(map, 
                                        parseFloat(provinciaInput.dataset.lat), 
                                        parseFloat(provinciaInput.dataset.lon), 8);
                    }
                    // Si hay Argentina seleccionada, mostrarla por defecto
                    else if (provinciaInput && provinciaInput.value.toLowerCase().includes('argent')) {
                        map.setView([-38.416097, -63.616672], 4);
                    }
                }
            } else {
                // Si se oculta el mapa, ocultar también las coordenadas
                if (coordenadasDiv) {
                    coordenadasDiv.style.display = 'none';
                }
            }
        });
        
        // Botón para usar las coordenadas seleccionadas
        if (usarCoordenadasBtn) {
            usarCoordenadasBtn.addEventListener('click', async function() {
                if (selectedLat && selectedLng) {
                    try {
                        // Realizar geocodificación inversa para obtener la dirección
                        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${selectedLat}&lon=${selectedLng}&zoom=18&addressdetails=1`);
                        const data = await response.json();
                        
                        if (data && data.address) {
                            // Actualizar los campos individuales
                            if (data.address.state) {
                                provinciaInput.value = data.address.state;
                            }
                            
                            if (data.address.city || data.address.town || data.address.village) {
                                ciudadInput.value = data.address.city || data.address.town || data.address.village;
                            }
                            
                            // Construir la dirección
                            let direccion = '';
                            if (data.address.road) {
                                direccion += data.address.road;
                                if (data.address.house_number) {
                                    direccion += ' ' + data.address.house_number;
                                }
                            }
                            
                            direccionInput.value = direccion;
                            
                            // Actualizar ubicación completa
                            actualizarUbicacionCompleta();
                        }
                    } catch (error) {
                        console.error('Error en geocodificación inversa:', error);
                    }
                }
            });
        }
    }
});

/**
 * EcoSmart Advisor - JavaScript principal
 * Funcionalidades generales para todas las páginas
 */

// Ejecutar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Inicializar popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Funcionalidad para volver arriba
    const btnVolverArriba = document.getElementById('btn-volver-arriba');
    if (btnVolverArriba) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                btnVolverArriba.classList.add('show');
            } else {
                btnVolverArriba.classList.remove('show');
            }
        });
        
        btnVolverArriba.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    }
    
    // Animación para números en métricas
    animateNumbers();
});

/**
 * Anima los números en elementos con la clase 'animate-number'
 */
function animateNumbers() {
    const numberElements = document.querySelectorAll('.animate-number');
    
    numberElements.forEach(element => {
        const targetValue = parseFloat(element.getAttribute('data-target') || element.textContent);
        const duration = parseInt(element.getAttribute('data-duration') || '1000');
        const decimals = parseInt(element.getAttribute('data-decimals') || '0');
        
        animateValue(element, 0, targetValue, duration, decimals);
    });
}

/**
 * Anima un valor desde inicio hasta fin en la duración especificada
 * @param {HTMLElement} element - Elemento DOM a animar
 * @param {number} start - Valor inicial
 * @param {number} end - Valor final
 * @param {number} duration - Duración en milisegundos
 * @param {number} decimals - Número de decimales a mostrar
 */
function animateValue(element, start, end, duration, decimals) {
    let startTimestamp = null;
    const prefix = element.getAttribute('data-prefix') || '';
    const suffix = element.getAttribute('data-suffix') || '';
    
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentValue = progress * (end - start) + start;
        
        element.textContent = prefix + currentValue.toFixed(decimals) + suffix;
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    
    window.requestAnimationFrame(step);
}

/**
 * Inicializa gráficos para la página de resultados
 * @param {string} chartType - Tipo de gráfico ('solar', 'eolico', 'termotanque')
 * @param {Object} data - Datos para el gráfico
 */
function initCharts(chartType, data) {
    // Esta función se implementará según sea necesario en las páginas específicas
    console.log('Inicialización de gráficos para:', chartType, data);
}

/**
 * Validación general de formularios
 * @param {HTMLFormElement} form - Formulario a validar
 * @returns {boolean} - True si el formulario es válido
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    // Reiniciar mensajes de error
    form.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Validar campos requeridos
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Validar campos de tipo email
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !validateEmail(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Validar campos numéricos
    const numberFields = form.querySelectorAll('input[type="number"]');
    numberFields.forEach(field => {
        if (field.value && (isNaN(parseFloat(field.value)) || parseFloat(field.value) < 0)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Valida un email
 * @param {string} email - Email a validar
 * @returns {boolean} - True si el email es válido
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Actualiza dinámicamente elementos en la UI basados en selecciones del usuario
 * @param {string} targetId - ID del elemento a actualizar
 * @param {string} value - Nuevo valor
 */
function updateUIElement(targetId, value) {
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
        if (targetElement.tagName === 'INPUT' || targetElement.tagName === 'SELECT' || targetElement.tagName === 'TEXTAREA') {
            targetElement.value = value;
        } else {
            targetElement.textContent = value;
        }
    }
}

/**
 * Maneja los mensajes de alerta y notificaciones
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de alerta ('success', 'danger', 'warning', 'info')
 * @param {string} container - ID del contenedor donde mostrar la alerta
 */
function showAlert(message, type = 'info', container = 'alertContainer') {
    const alertContainer = document.getElementById(container);
    if (!alertContainer) return;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertElement);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertElement);
        bsAlert.close();
    }, 5000);
}