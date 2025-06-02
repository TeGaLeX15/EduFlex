document.addEventListener('DOMContentLoaded', function() {
    // Обработчик для кнопок лайка и дизлайка
    document.querySelectorAll('.like-btn, .dislike-btn').forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const voteType = this.getAttribute('data-vote-type');
            const isDisabled = this.classList.contains('disabled');  // Проверяем, заблокирована ли кнопка

            // Если кнопка заблокирована (пользователь уже голосовал), отменяем голос
            if (isDisabled) {
                fetch(`/review/${reviewId}/vote/remove`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token() }}'  // Для безопасности
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Обновляем количество лайков и дизлайков на странице
                        const reviewCard = document.querySelector(`[data-review-id="${reviewId}"]`);
                        reviewCard.querySelector('.like-btn').textContent = `👍 ${data.likes_count}`;
                        reviewCard.querySelector('.dislike-btn').textContent = `👎 ${data.dislikes_count}`;
                        
                        // Разблокируем кнопки, чтобы можно было проголосовать заново
                        reviewCard.querySelector('.like-btn').disabled = false;
                        reviewCard.querySelector('.dislike-btn').disabled = false;

                        // Удаляем класс disabled, чтобы кнопки стали активными
                        reviewCard.querySelector('.like-btn').classList.remove('disabled');
                        reviewCard.querySelector('.dislike-btn').classList.remove('disabled');
                    } else {
                        alert(data.error);  // Если ошибка, показываем сообщение
                    }
                })
                .catch(error => console.error('Error:', error));

            } else {
                // Отправляем запрос на сервер для голосования
                fetch(`/review/${reviewId}/vote/${voteType}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token() }}'  // Для безопасности
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Обновляем количество лайков и дизлайков на странице
                        const reviewCard = document.querySelector(`[data-review-id="${reviewId}"]`);
                        reviewCard.querySelector('.like-btn').textContent = `👍 ${data.likes_count}`;
                        reviewCard.querySelector('.dislike-btn').textContent = `👎 ${data.dislikes_count}`;
                        
                        // Разблокируем кнопки, чтобы можно было проголосовать заново
                        reviewCard.querySelector('.like-btn').disabled = false;
                        reviewCard.querySelector('.dislike-btn').disabled = false;

                        // Удаляем класс disabled, чтобы кнопки стали активными
                        reviewCard.querySelector('.like-btn').classList.remove('disabled');
                        reviewCard.querySelector('.dislike-btn').classList.remove('disabled');
                    } else {
                        alert(data.error);  // Если ошибка, показываем сообщение
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });
});