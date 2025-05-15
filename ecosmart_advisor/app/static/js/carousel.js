// Script para el carrusel aleatorio
document.addEventListener('DOMContentLoaded', function() {
    const carrusel = document.getElementById('carouselEnergiasRenovables');
    
    if (carrusel) {
        console.log("Carrusel inicializado correctamente");
        
        // Evento para detectar cambios de diapositiva
        carrusel.addEventListener('slide.bs.carousel', function (event) {
            console.log("Cambiando a diapositiva:", event.to);
        });
        
        // Verificar si hay imágenes cargadas dinámicamente
        const imagenesCarrusel = carrusel.querySelectorAll('img');
        
        imagenesCarrusel.forEach((img, index) => {
            if (img.complete) {
                console.log(`Imagen ${index} ya cargada: ${img.src.substring(0, 50)}...`);
            } else {
                img.addEventListener('load', function() {
                    console.log(`Imagen ${index} cargada dinámicamente: ${img.src.substring(0, 50)}...`);
                });
                img.addEventListener('error', function() {
                    console.error(`Error al cargar imagen ${index}`);
                });
            }
        });
    }
});