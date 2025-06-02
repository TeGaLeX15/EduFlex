function toggleTheme() {
    // Переключаем класс dark-theme для корня документа
    document.documentElement.classList.toggle('dark-theme');
    
    // Меняем изображение в зависимости от текущей темы
    const themeIcon = document.getElementById('theme-icon');
    if (document.documentElement.classList.contains('dark-theme')) {
        themeIcon.src = 'https://cdn-icons-png.flaticon.com/512/869/869869.png'; // Солнце
    } else {
        themeIcon.src = 'https://cdn-icons-png.flaticon.com/512/1163/1163645.png'; // Месяц
    }

    // Сохраняем выбранную тему в localStorage
    localStorage.setItem('theme', document.documentElement.classList.contains('dark-theme') ? 'dark' : 'light');
}

// При загрузке страницы проверяем сохраненную тему
window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-theme');
        themeIcon.src = 'https://cdn-icons-png.flaticon.com/512/869/869869.png'; // Солнце
    } else {
        themeIcon.src = 'https://cdn-icons-png.flaticon.com/512/1163/1163645.png'; // Месяц
    }
});
