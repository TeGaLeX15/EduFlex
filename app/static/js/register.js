document.getElementById('registerForm').addEventListener('input', function (e) {
    e.preventDefault();

    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const registerBtn = document.getElementById('registerBtn');

    // Элементы ошибок
    const usernameError = document.getElementById('usernameError');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    // Проверка логина
    const usernameValid = /^[a-zA-Z0-9]+$/.test(username.value.trim());
    if (!username.value.trim()) {
        usernameError.textContent = '';
    } else if (!usernameValid) {
        usernameError.textContent = 'Логин должен содержать только латинские буквы и цифры.';
    } else {
        usernameError.textContent = '';
    }

    // Проверка почты
    const emailValid = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email.value.trim());
    if (!email.value.trim()) {
        emailError.textContent = '';
    } else if (!emailValid) {
        emailError.textContent = 'Введите корректный адрес электронной почты.';
    } else {
        emailError.textContent = '';
    }

    // Проверка пароля
    const passwordValid = password.value.trim().length >= 6;
    if (!password.value.trim()) {
        passwordError.textContent = '';
    } else if (!passwordValid) {
        passwordError.textContent = 'Пароль должен содержать не менее 6 символов.';
    } else {
        passwordError.textContent = '';
    }

    // Проверка совпадения паролей
    const passwordsMatch = password.value.trim() === confirmPassword.value.trim();
    if (!confirmPassword.value.trim()) {
        confirmPasswordError.textContent = '';
    } else if (!passwordsMatch) {
        confirmPasswordError.textContent = 'Пароли не совпадают.';
    } else {
        confirmPasswordError.textContent = '';
    }

    // Если все поля валидны, активируем кнопку
    if (usernameValid && emailValid && passwordValid && passwordsMatch) {
        registerBtn.disabled = false;
    } else {
        registerBtn.disabled = true;
    }
});