document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".step-btn");
    const texts = document.querySelectorAll(".step-text");
    let currentStep = 1;
    let intervalId;

    // Функция переключения шага
    function switchStep(step) {
        // Активная кнопка
        buttons.forEach(b => b.classList.remove("active"));
        const activeButton = document.querySelector(`.step-btn[data-step="${step}"]`);
        activeButton.classList.add("active");

        // Показ текста
        texts.forEach(t => {
            t.classList.remove("active");
            if (t.dataset.step === String(step)) {
                t.classList.add("active");
                t.style.animation = "fadeIn 0.5s ease-out";
            }
        });
    }

    // Запуск автоматического переключения
    function startAutoSwitch() {
        intervalId = setInterval(() => {
            currentStep = (currentStep % buttons.length) + 1;
            switchStep(currentStep);
        }, 5000);
    }

    // Перезапуск таймера
    function resetAutoSwitch() {
        clearInterval(intervalId);
        startAutoSwitch();
    }

    // Инициализация первого шага
    switchStep(currentStep);
    startAutoSwitch();

    // Обработчик клика на кнопки
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const step = btn.dataset.step;
            currentStep = parseInt(step);
            switchStep(currentStep);
            resetAutoSwitch(); // Сбросить таймер
        });
    });
});
