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

    // Función genérica para manejar autocompletado de un campo
    async function manejarAutocompletado(inputElement, sugerenciasDiv, tipo) {
        const texto = inputElement.value;
        if (texto.length < 3) {
            sugerenciasDiv.style.display = 'none';
            return;
        }

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

                    // Si hay mapa inicializado, actualizar su posición
                    if (map && marker) {
                        const latLng = [parseFloat(lugar.lat), parseFloat(lugar.lon)];
                        map.setView(latLng, 10);
                        marker.setLatLng(latLng);

                        // Actualizar valores mostrados
                        latitudSpan.textContent = lugar.lat;
                        longitudSpan.textContent = lugar.lon;
                        selectedLat = lugar.lat;
                        selectedLng = lugar.lon;
                        coordenadasDiv.style.display = 'flex';
                    }
                });

                sugerenciasDiv.appendChild(div);
            });

            if (data.length > 0) {
                sugerenciasDiv.style.display = 'block';
            } else {
                sugerenciasDiv.style.display = 'none';
            }

        } catch (error) {
            console.error(`Error en autocompletado de ${tipo}:`, error);
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
        mostrarMapaBtn.addEventListener('click', function() {
            const estaMostrado = mapaUbicacionDiv.style.display !== 'none';

            if (estaMostrado) {
                // Ocultar mapa
                mapaUbicacionDiv.style.display = 'none';
                coordenadasDiv.style.display = 'none';
            } else {
                // Mostrar mapa
                mapaUbicacionDiv.style.display = 'block';

                // Si el mapa no está inicializado, crearlo
                if (!map) {
                    // Posición inicial (centrar en una ubicación por defecto o usar la seleccionada)
                    let initialLat = -34.603722;  // Buenos Aires por defecto
                    let initialLng = -58.381592;

                    // Si hay una provincia o ciudad seleccionada con coordenadas, usarlas
                    if (ciudadInput.dataset.lat && ciudadInput.dataset.lon) {
                        initialLat = parseFloat(ciudadInput.dataset.lat);
                        initialLng = parseFloat(ciudadInput.dataset.lon);
                    } else if (provinciaInput.dataset.lat && provinciaInput.dataset.lon) {
                        initialLat = parseFloat(provinciaInput.dataset.lat);
                        initialLng = parseFloat(provinciaInput.dataset.lon);
                    }

                    // Crear el mapa
                    map = L.map('mapaUbicacion').setView([initialLat, initialLng], 10);

                    // Añadir capa de OpenStreetMap
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '© OpenStreetMap contributors'
                    }).addTo(map);

                    // Añadir marcador arrastrable
                    marker = L.marker([initialLat, initialLng], {
                        draggable: true
                    }).addTo(map);

                    // Actualizar coordenadas al arrastrar el marcador
                    marker.on('dragend', function(e) {
                        const position = marker.getLatLng();
                        latitudSpan.textContent = position.lat.toFixed(6);
                        longitudSpan.textContent = position.lng.toFixed(6);
                        selectedLat = position.lat;
                        selectedLng = position.lng;
                        coordenadasDiv.style.display = 'flex';
                    });

                    // Permitir hacer clic en el mapa para mover el marcador
                    map.on('click', function(e) {
                        marker.setLatLng(e.latlng);
                        latitudSpan.textContent = e.latlng.lat.toFixed(6);
                        longitudSpan.textContent = e.latlng.lng.toFixed(6);
                        selectedLat = e.latlng.lat;
                        selectedLng = e.latlng.lng;
                        coordenadasDiv.style.display = 'flex';
                    });

                    // Ajustar tamaño del mapa (necesario a veces)
                    setTimeout(function() {
                        map.invalidateSize();
                    }, 100);
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

// Inicializar mapa
var map;
function initMap() {
    if (document.getElementById('map')) {
        if (map) {
            map.remove();
        }
        map = L.map('map').setView([40.416775, -3.703790], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Asegurar que el mapa se renderice correctamente
        setTimeout(() => {
            map.invalidateSize();
        }, 100);
    }
}

// Asegurar que el mapa se inicialice cuando se muestre
document.addEventListener('DOMContentLoaded', function() {
    const mapButton = document.querySelector('[data-bs-target="#mapModal"]');
    if (mapButton) {
        mapButton.addEventListener('click', function() {
            setTimeout(initMap, 300);
        });
    }
});

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