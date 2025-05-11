
// Configuración del mapa y autocompletado
document.addEventListener('DOMContentLoaded', function() {
    const ubicacionInput = document.getElementById('ubicacion');
    const sugerenciasDiv = document.getElementById('sugerenciasUbicacion');
    
    // Variable para controlar el tiempo entre búsquedas (debounce)
    let typingTimer;
    const doneTypingInterval = 500; // Tiempo en ms
    
    // Variable para trackear la última consulta
    let lastQuery = '';
    
    if (ubicacionInput && sugerenciasDiv) {
        // Limpiar sugerencias al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (e.target !== ubicacionInput && !sugerenciasDiv.contains(e.target)) {
                sugerenciasDiv.style.display = 'none';
            }
        });
        
        // Manejar navegación por teclado en sugerencias
        ubicacionInput.addEventListener('keydown', function(e) {
            const sugerencias = sugerenciasDiv.querySelectorAll('.list-group-item');
            const activeItem = sugerenciasDiv.querySelector('.active');
            
            if (sugerencias.length > 0 && sugerenciasDiv.style.display === 'block') {
                // Flecha abajo
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (!activeItem) {
                        sugerencias[0].classList.add('active');
                    } else {
                        const nextItem = activeItem.nextElementSibling;
                        if (nextItem) {
                            activeItem.classList.remove('active');
                            nextItem.classList.add('active');
                        }
                    }
                }
                
                // Flecha arriba
                else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (activeItem) {
                        const prevItem = activeItem.previousElementSibling;
                        activeItem.classList.remove('active');
                        if (prevItem) {
                            prevItem.classList.add('active');
                        }
                    }
                }
                
                // Enter para seleccionar
                else if (e.key === 'Enter' && activeItem) {
                    e.preventDefault();
                    ubicacionInput.value = activeItem.textContent;
                    sugerenciasDiv.style.display = 'none';
                }
                
                // Escape para cerrar
                else if (e.key === 'Escape') {
                    sugerenciasDiv.style.display = 'none';
                }
            }
        });
        
        // Autocompletado con debounce
        ubicacionInput.addEventListener('input', function() {
            clearTimeout(typingTimer);
            
            const texto = this.value.trim();
            if (texto.length < 3) {
                sugerenciasDiv.style.display = 'none';
                return;
            }
            
            // Si el texto no ha cambiado, no hacer nada
            if (texto === lastQuery) return;
            
            // Esperar a que el usuario termine de escribir
            typingTimer = setTimeout(async function() {
                lastQuery = texto;
                
                try {
                    // Agregar parámetros para mejorar la búsqueda
                    const params = new URLSearchParams({
                        format: 'json',
                        q: texto,
                        limit: 5,
                        addressdetails: 1,
                        namedetails: 1
                    });
                    
                    sugerenciasDiv.innerHTML = '<div class="list-group-item text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"></div> Buscando...</div>';
                    sugerenciasDiv.style.display = 'block';
                    
                    const response = await fetch(`https://nominatim.openstreetmap.org/search?${params.toString()}`);
                    const data = await response.json();
                    
                    // Si no hay resultados
                    if (data.length === 0) {
                        sugerenciasDiv.innerHTML = '<div class="list-group-item text-center text-muted">No se encontraron resultados</div>';
                        return;
                    }
                    
                    // Mostrar resultados
                    sugerenciasDiv.innerHTML = '';
                    data.forEach(lugar => {
                        // Formatear el nombre para que sea más legible y completo
                        let nombreLugar = '';
                        
                        // Extraer el nombre de la ciudad/localidad, provincia/estado y país
                        const partes = [];
                        
                        if (lugar.address) {
                            // Localidad principal (ciudad, pueblo, villa, etc.)
                            if (lugar.address.city) partes.push(lugar.address.city);
                            else if (lugar.address.town) partes.push(lugar.address.town);
                            else if (lugar.address.village) partes.push(lugar.address.village);
                            else if (lugar.address.municipality) partes.push(lugar.address.municipality);
                            else if (lugar.address.hamlet) partes.push(lugar.address.hamlet);
                            else if (lugar.address.locality) partes.push(lugar.address.locality);
                            
                            // Siempre incluir provincia/estado si está disponible
                            if (lugar.address.state) partes.push(lugar.address.state);
                            else if (lugar.address.province) partes.push(lugar.address.province);
                            else if (lugar.address.county) partes.push(lugar.address.county);
                            else if (lugar.address.region) partes.push(lugar.address.region);
                            
                            // Siempre incluir país
                            if (lugar.address.country) partes.push(lugar.address.country);
                        }
                        
                        nombreLugar = partes.length > 0 ? partes.join(', ') : lugar.display_name;
                        
                        // Si no se pudo obtener un nombre legible, usar el nombre completo proporcionado por la API
                        if (partes.length < 2) {
                            nombreLugar = lugar.display_name;
                        }
                        
                        const div = document.createElement('div');
                        div.className = 'list-group-item list-group-item-action';
                        div.textContent = nombreLugar;
                        div.setAttribute('data-lat', lugar.lat);
                        div.setAttribute('data-lon', lugar.lon);
                        div.setAttribute('data-full', lugar.display_name);
                        
                        div.addEventListener('click', () => {
                            ubicacionInput.value = nombreLugar;
                            sugerenciasDiv.style.display = 'none';
                        });
                        
                        sugerenciasDiv.appendChild(div);
                    });
                } catch (error) {
                    console.error('Error en autocompletado:', error);
                    sugerenciasDiv.innerHTML = '<div class="list-group-item text-center text-danger">Error al buscar ubicaciones</div>';
                }
            }, doneTypingInterval);
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