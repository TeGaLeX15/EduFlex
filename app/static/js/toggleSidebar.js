function toggleSidebar() {
    const layout = document.querySelector(".layout");
    layout.classList.toggle("sidebar-collapsed");

    // Сохраняем текущее состояние в localStorage
    if (layout.classList.contains("sidebar-collapsed")) {
        localStorage.setItem("sidebarState", "collapsed");
    } else {
        localStorage.setItem("sidebarState", "expanded");
    }
}

// При загрузке страницы проверяем сохранённое состояние и устанавливаем его
document.addEventListener("DOMContentLoaded", () => {
    const layout = document.querySelector(".layout");
    const savedState = localStorage.getItem("sidebarState");

    if (savedState === "collapsed") {
        layout.classList.add("sidebar-collapsed");
    } else {
        layout.classList.remove("sidebar-collapsed");
    }
});
