/* 
    ============================================================================
    SCRIPT.JS - DreamWalker Plane
    ============================================================================
    Funcionalidades:
    - Animação de scroll (data-anime)
    - Botão de loading (enviar formulário)
    ============================================================================
*/

/* ==================== ANIMAÇÃO DE SCROLL ==================== */
// Para elementos com atributo data-anime
const animeItems = document.querySelectorAll("[data-anime]");

const animeScroll = () => {
    const windowHeight = window.innerHeight;
    const windowTop = window.scrollY;
    
    animeItems.forEach((element) => {
        const elementTop = element.offsetTop;
        const elementVisible = 150;
        
        if (windowTop + windowHeight > elementTop + elementVisible) {
            element.classList.add("animate");
        } else {
            // Opcional: remove a classe se quiser que repita
            // element.classList.remove("animate");
        }
    });
}

// Executa ao carregar
animeScroll();

// Executa ao scrollar
window.addEventListener("scroll", animeScroll);

/* ==================== BOTÃO DE LOADING ==================== */
// Para formulários com botão de envio
const forms = document.querySelectorAll('form[data-loading]');

forms.forEach(form => {
    form.addEventListener("submit", () => {
        const btnSend = form.querySelector('#btn-send');
        const btnLoader = form.querySelector('#btn-send-loader');
        
        if (btnSend && btnLoader) {
            btnSend.style.display = "none";
            btnLoader.style.display = "block";
        }
    });
});