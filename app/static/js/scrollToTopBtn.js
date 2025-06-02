// Плавная прокрутка наверх
let scrollToTopBtn = document.getElementById("scrollToTopBtn");

// Показ кнопки при прокрутке
window.onscroll = function () {
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        scrollToTopBtn.style.display = "block"; // Показываем кнопку
    } else {
        scrollToTopBtn.style.display = "none"; // Скрываем кнопку
    }
};

// При клике на кнопку, прокручиваем страницу вверх
scrollToTopBtn.addEventListener("click", function () {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});