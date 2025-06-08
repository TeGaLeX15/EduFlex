function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    menu.classList.toggle('show');
}

document.addEventListener('click', function (e) {
    const menu = document.getElementById('mobileMenu');
    const toggleBtn = document.querySelector('.mobile-menu-toggle');
    if (!menu.contains(e.target) && !toggleBtn.contains(e.target)) {
        menu.classList.remove('show');
    }
});

window.addEventListener('resize', function () {
    const menu = document.getElementById('mobileMenu');
    if (window.innerWidth > 1024 && menu.classList.contains('show')) {
        menu.classList.remove('show');
    }
});