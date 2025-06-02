document.getElementById('loginForm').addEventListener('input', function(e) {
  e.preventDefault();

  const username = document.getElementById('username');
  const password = document.getElementById('password');
  const loginBtn = document.getElementById('loginBtn');

  // Элементы ошибок
  const usernameError = document.getElementById('usernameError');
  const passwordError = document.getElementById('passwordError');

  // Проверка логина
  const usernameValid = /^[a-zA-Z0-9]+$/.test(username.value.trim());
  if (!username.value.trim()) {
      usernameError.textContent = '';
  } else if (!usernameValid) {
      usernameError.textContent = 'Логин должен содержать только латинские буквы и цифры.';
  } else {
      usernameError.textContent = '';
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

  // Если оба поля валидны, активируем кнопку
  if (usernameValid && passwordValid) {
      loginBtn.disabled = false;
  } else {
      loginBtn.disabled = true;
  }
});