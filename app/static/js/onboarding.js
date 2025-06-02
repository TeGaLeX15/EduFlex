const slides = document.getElementById('slides');
const nextBtn = document.getElementById('nextBtn');
const prevBtn = document.getElementById('prevBtn');
const skipBtn = document.getElementById('skipBtn');
const startBtn = document.getElementById('startBtn');
const topicCards = document.querySelectorAll('.topic-card');
let currentSlide = 0;
let selectedTopics = new Set();
const totalSlides = document.querySelectorAll('.slide').length;

function updateSlide() {
  slides.style.transform = `translateX(-${currentSlide * 100}%)`;

  // Назад — только не на первом
  prevBtn.style.visibility = currentSlide === 0 ? 'hidden' : 'visible';

  // Пропустить — всегда видно
  skipBtn.style.visibility = currentSlide === 3 ? 'hidden' : 'visible';

  // Блокируем кнопку "Далее" на последнем слайде
  if (currentSlide === totalSlides - 1) {
    nextBtn.disabled = true; // Отключаем кнопку на последнем слайде
  } else {
    nextBtn.disabled = false;
  }

  // Блокируем или активируем кнопку "Далее" для выбора интересов
  if (currentSlide === 2) {
    nextBtn.disabled = selectedTopics.size === 0; // Блокируем, если нет выбора интересов
  }

  // Обновление кнопки "Далее"
  if (currentSlide === totalSlides - 1) {
    nextBtn.style.visibility = 'hidden'; // Скрыть кнопку на последнем слайде
  } else {
    nextBtn.style.visibility = 'visible'; // Показывать кнопку на других слайдах
  }
}

nextBtn.addEventListener('click', () => {
  if (currentSlide < totalSlides - 1) {
    currentSlide++;
    updateSlide();
  }
});

prevBtn.addEventListener('click', () => {
  if (currentSlide > 0) {
    currentSlide--;
    updateSlide();
  }
});

skipBtn.addEventListener('click', () => {
  window.location.href = '/';
});

topicCards.forEach(card => {
  card.addEventListener('click', () => {
    card.classList.toggle('selected');
    const topic = card.dataset.topic;
    if (selectedTopics.has(topic)) {
      selectedTopics.delete(topic);
    } else {
      selectedTopics.add(topic);
    }
    // Обновляем и кнопку "Начать", и "Далее"
    startBtn.disabled = selectedTopics.size === 0;
    if (currentSlide === 2) {
      nextBtn.disabled = selectedTopics.size === 0;
    }
  });
});

// Обновленный обработчик кнопки "Начать"
startBtn.addEventListener('click', () => {
  // Отправляем выбранные интересы на сервер
  fetch('/onboarding/save_interest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      interests: Array.from(selectedTopics)  // Преобразуем Set в массив
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Server response:', data);  // Логируем ответ сервера
    if (data.status === 'ok') {
      // Успешно сохранено, редирект на главную
      window.location.href = '/';
    } else {
      alert(`Произошла ошибка: ${data.message}`);
    }
  })
  .catch(error => {
    console.error('Ошибка:', error);
    alert('Произошла ошибка. Попробуйте снова.');
  });
});

updateSlide();