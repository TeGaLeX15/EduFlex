let currentQuestion = 0;
let questions = []; // Массив вопросов
let totalQuestions = 0; // Число вопросов (будет изменено при загрузке данных)
let quizTitle = ''; // Название квиза

// Функция для обновления прогресса
function updateProgress() {
  const progress = ((currentQuestion + 1) / totalQuestions) * 100;
  document.getElementById('progress').style.width = progress + '%';
  document.getElementById('progress-percent').textContent = Math.round(progress) + '%';
  document.getElementById('question-number').textContent = currentQuestion + 1;
  toggleNavigationButtons();  // Обновить видимость кнопок навигации
}

// Функция для загрузки текущего вопроса
function loadQuestion() {
  const questionData = questions[currentQuestion];
  document.getElementById('question-text').textContent = questionData.text;

  // Заполнение опций
  questionData.options.forEach((option, index) => {
    document.getElementById(`option${index}`).nextElementSibling.textContent = option;
  });
}

// Функция для загрузки всего квиза
function loadQuiz(quizData) {
  quizTitle = quizData.title;
  questions = quizData.questions;
  totalQuestions = questions.length;

  document.getElementById('quiz-title').textContent = quizTitle;
  loadQuestion(); // Загружаем первый вопрос
  updateProgress(); // Обновляем прогресс
}

// Функция для навигации по вопросам
function navigateQuestion(action) {
  if (action === 'next') {
    if (currentQuestion < totalQuestions - 1) {
      currentQuestion++;
    }
  } else if (action === 'prev' && currentQuestion > 0) {
    currentQuestion--;
  } else if (action === 'skip' && currentQuestion < totalQuestions - 1) {
    currentQuestion++;
  }

  if (currentQuestion >= totalQuestions) currentQuestion = totalQuestions - 1; // Ограничиваем по максимальному числу вопросов
  if (currentQuestion < 0) currentQuestion = 0;

  updateProgress();
  loadQuestion();
}

// Функция для переключения кнопок навигации
function toggleNavigationButtons() {
  // Показать/скрыть кнопку "Назад"
  if (currentQuestion === 0) {
    document.getElementById('prev-btn').style.display = 'none';
  } else {
    document.getElementById('prev-btn').style.display = 'inline-block';
  }

  // Показать/скрыть кнопку "Далее" и "Завершить"
  if (currentQuestion === totalQuestions - 1) {
    document.getElementById('next-btn').style.display = 'none';
    document.getElementById('finish-btn').style.display = 'inline-block'; // Показать кнопку "Завершить"
  } else {
    document.getElementById('next-btn').style.display = 'inline-block';
    document.getElementById('finish-btn').style.display = 'none';
  }
}

// Функция для загрузки данных квиза
function fetchQuizData() {
  fetch('../static/js/courses.json')
    .then(response => response.json())
    .then(data => {
      const quizData = data.python[0].quizes[0];  // Получение данных первого квиза
      loadQuiz(quizData); // Загрузка квиза
    })
    .catch(error => {
      console.error('Ошибка при загрузке данных квиза:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
  fetchQuizData(); // Загружаем данные квиза при загрузке страницы
  document.getElementById('prev-btn').style.display = 'none'; // Скрыть кнопку "Назад" на первом вопросе
});
