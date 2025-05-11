
// Configuración del mapa y autocompletado
document.addEventListener('DOMContentLoaded', function() {
    const ubicacionInput = document.getElementById('ubicacion');
    const sugerenciasDiv = document.getElementById('sugerenciasUbicacion');
    const btnMapa = document.getElementById('btnMapa');
    const mapaModal = new bootstrap.Modal(document.getElementById('mapaModal'));
    let map, marker;

    if (ubicacionInput) {
        // Autocompletado
        ubicacionInput.addEventListener('input', async function() {
            const texto = this.value;
            if (texto.length < 3) {
                sugerenciasDiv.style.display = 'none';
                return;
            }

            try {
                const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${texto}`);
                const data = await response.json();
                
                sugerenciasDiv.innerHTML = '';
                data.slice(0, 5).forEach(lugar => {
                    const div = document.createElement('div');
                    div.className = 'list-group-item list-group-item-action';
                    div.textContent = lugar.display_name;
                    div.addEventListener('click', () => {
                        ubicacionInput.value = lugar.display_name;
                        sugerenciasDiv.style.display = 'none';
                    });
                    sugerenciasDiv.appendChild(div);
                });
                sugerenciasDiv.style.display = 'block';
            } catch (error) {
                console.error('Error en autocompletado:', error);
            }
        });

        // Configuración del mapa
        btnMapa.addEventListener('click', function() {
            mapaModal.show();
            setTimeout(() => {
                if (!map) {
                    map = L.map('mapa').setView([-34.6037, -58.3816], 4);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '© OpenStreetMap contributors'
                    }).addTo(map);
                    marker = L.marker([-34.6037, -58.3816], {draggable: true}).addTo(map);
                    
                    map.on('click', function(e) {
                        marker.setLatLng(e.latlng);
                    });
                }
                map.invalidateSize();
            }, 250);
        });

        // Confirmar ubicación seleccionada en el mapa
        document.getElementById('confirmarUbicacion').addEventListener('click', function() {
            const latlng = marker.getLatLng();
            ubicacionInput.value = `${latlng.lat.toFixed(6)},${latlng.lng.toFixed(6)}`;
            mapaModal.hide();
        });
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