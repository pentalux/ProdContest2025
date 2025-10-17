// Component ported from https://codepen.io/JuanFuentes/full/rgXKGQ
// Основные функции авторизации
function startTelegramAuth() {
    const statusElement = document.getElementById('status');
    const userInfoElement = document.getElementById('user-info');
    
    // Очистка предыдущих сообщений
    statusElement.textContent = '';
    statusElement.className = 'status-message';
    userInfoElement.style.display = 'none';
    
    // Показать статус подключения
    statusElement.textContent = 'Подключение к Telegram...';
    statusElement.className = 'status-message info';
    
    // Имитация процесса авторизации
    setTimeout(() => {
        // В реальном приложении здесь будет интеграция с Telegram Widget
        // Для демонстрации используем имитацию успешной авторизации
        
        const userData = {
            id: Math.floor(Math.random() * 1000000000),
            firstName: 'Иван',
            lastName: 'Петров',
            username: 'ivan_petrov',
            photoUrl: 'https://i.pravatar.cc/150?img=' + Math.floor(Math.random() * 70)
        };
        
        displayUserInfo(userData);
        statusElement.textContent = 'Авторизация прошла успешно!';
        statusElement.className = 'status-message success';
        
        // Сохраняем данные пользователя в localStorage
        localStorage.setItem('telegramUser', JSON.stringify(userData));
        
        // Показываем кнопку выхода
        showLogoutButton();
    }, 2000);
}

function displayUserInfo(user) {
    const userInfoElement = document.getElementById('user-info');
    userInfoElement.innerHTML = `
        <img src="${user.photoUrl}" alt="Фото пользователя" width="80" height="80">
        <h3>${user.firstName} ${user.lastName}</h3>
        <p>@${user.username}</p>
        <p>ID: ${user.id}</p>
        <button onclick="logout()" class="logout-btn">Выйти</button>
    `;
    userInfoElement.style.display = 'block';
    
    // Скрываем кнопку авторизации
    document.querySelector('.telegram-btn').style.display = 'none';
}

function showLogoutButton() {
    // Кнопка уже добавляется в displayUserInfo
}

function logout() {
    const statusElement = document.getElementById('status');
    const userInfoElement = document.getElementById('user-info');
    
    // Очищаем данные
    localStorage.removeItem('telegramUser');
    
    // Сбрасываем интерфейс
    userInfoElement.style.display = 'none';
    document.querySelector('.telegram-btn').style.display = 'block';
    
    statusElement.textContent = 'Вы вышли из системы';
    statusElement.className = 'status-message info';
    
    setTimeout(() => {
        statusElement.textContent = '';
        statusElement.className = 'status-message';
    }, 3000);
}

// Функции для модального окна регистрации
function showRegistration() {
    document.getElementById('registration-modal').style.display = 'flex';
}

function closeRegistration() {
    document.getElementById('registration-modal').style.display = 'none';
    document.getElementById('registration-form').reset();
}

// Обработка формы регистрации
document.getElementById('registration-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const name = this.querySelector('input[type="text"]').value;
    const email = this.querySelector('input[type="email"]').value;
    
    // Имитация регистрации
    const statusElement = document.getElementById('status');
    statusElement.textContent = `Регистрация успешна! Добро пожаловать, ${name}!`;
    statusElement.className = 'status-message success';
    
    closeRegistration();
    
    // Очищаем сообщение через 5 секунд
    setTimeout(() => {
        statusElement.textContent = '';
        statusElement.className = 'status-message';
    }, 5000);
});

// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const savedUser = localStorage.getItem('telegramUser');
    
    if (savedUser) {
        const userData = JSON.parse(savedUser);
        displayUserInfo(userData);
        
        const statusElement = document.getElementById('status');
        statusElement.textContent = 'Вы уже авторизованы';
        statusElement.className = 'status-message info';
    }
    
    // Закрытие модального окна при клике вне его
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('registration-modal');
        if (event.target === modal) {
            closeRegistration();
        }
    });
});

// Стили для кнопки выхода
const style = document.createElement('style');
style.textContent = `
    .logout-btn {
        background: #dc3545;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
        margin-top: 10px;
        font-weight: 500;
    }
    
    .logout-btn:hover {
        background: #c82333;
    }
`;
document.head.appendChild(style);