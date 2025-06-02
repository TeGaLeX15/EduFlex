// flashMessages.js
document.addEventListener('DOMContentLoaded', function () {
    let flashMessages = document.querySelectorAll('.flash-toast');

    flashMessages.forEach(function (flashMessage) {
        // Плавно показываем сообщение
        flashMessage.classList.add('show');

        // Убираем флеш-сообщение через 4 секунды (анимированное исчезновение)
        setTimeout(function () {
            flashMessage.classList.remove('show');
        }, 3000); // Сообщение исчезает через 3 секунды

        // Удаляем флеш-сообщение после исчезновения
        setTimeout(function () {
            flashMessage.remove();
        }, 3500); // Удаление через 0.5 секунд после исчезновения
    });
});
