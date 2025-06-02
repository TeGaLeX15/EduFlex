// static/js/leaveReviewValidation.js
document.addEventListener('DOMContentLoaded', function () {
    const reviewText = document.getElementById('reviewText');
    const submitBtn = document.getElementById('submitBtn');
    const reviewError = document.getElementById('reviewError');
    const starRating = document.querySelector('input[name="rating"]:checked');
    const reviewForm = document.getElementById('reviewForm');

    // Функция для проверки, можно ли отправить отзыв
    function validateForm() {
        const textLength = reviewText.value.trim().length;
        const isRatingSelected = document.querySelector('input[name="rating"]:checked') !== null;

        // Проверка, что отзыв содержит минимум 25 символов
        if (textLength < 25) {
            reviewError.style.display = 'block';
            submitBtn.disabled = true;
        } else {
            reviewError.style.display = 'none';
        }

        // Включаем кнопку отправки, если все условия выполнены
        if (textLength >= 25 && isRatingSelected) {
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
        }
    }

    // Проверка при вводе текста
    reviewText.addEventListener('input', validateForm);

    // Проверка при изменении оценки
    const starInputs = document.querySelectorAll('input[name="rating"]');
    starInputs.forEach(input => input.addEventListener('change', validateForm));

    // Инициализация проверки при загрузке
    validateForm();
});
