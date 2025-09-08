// año dinamico
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// menu movil accessible
const btnMenu = document.getElementById("btn-menu");
const menu = document.getElementById("menu");
if (btnMenu && menu){
    btnMenu.addEventListener("click",() =>{
        const abierto = menu.classList.toggle("open");
        btnMenu.setAttribute("aria-expend", abierto ? "true" : "false");
    });
}
// scroll suavizado para  las referencias
const links = document.querySelectorAll('a[href^="#"]');
links.forEach((a) => {
    a.addEventListener("click", (e) => {
        const targetId = a.getAttribute("href");
        if (!targetId || targetId === "#") return;
        const target = document.querySelector(targetId);
        if (target) {
e.preventDefault();
target.scrollIntoView({ behavior: "smooth", block: "start" });
}
});
});

