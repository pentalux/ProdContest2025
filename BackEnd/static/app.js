let authId = null;
let checkInterval = null;

function startTelegramAuth() {
    console.log('Starting Telegram auth...');
    showStatus('Инициализация авторизации...', 'pending');
    document.getElementById('auth-btn').disabled = true;
    
    fetch('/init-auth')
        .then(response => response.json())
        .then(data => {
            authId = data.auth_id;
            showStatus('Открываю Telegram...', 'pending');
            
            window.open(data.bot_url, '_blank');
            startCheckingAuth();
        })
        .catch(error => {
            console.error('Error:', error);
            showStatus('Ошибка инициализации авторизации', 'error');
            document.getElementById('auth-btn').disabled = false;
        });
}

function startCheckingAuth() {
    if (checkInterval) {
        clearInterval(checkInterval);
    }
    
    checkInterval = setInterval(() => {
        checkAuthStatus();
    }, 2000);
}

function checkAuthStatus() {
    if (!authId) return;
    
    fetch('/check-auth/' + authId)
        .then(response => response.json())
        .then(data => {
            console.log('Auth status:', data);
            
            if (data.status === 'completed') {
                clearInterval(checkInterval);
                showSuccess(data.user);
            } else if (data.status === 'pending') {
                showStatus('⌛ Ожидание подтверждения в Telegram...<br><small>Пожалуйста, поделитесь номером телефона в боте</small>', 'pending');
            } else if (data.status === 'not_found') {
                showStatus('❌ Сессия авторизации устарела', 'error');
                document.getElementById('auth-btn').disabled = false;
                clearInterval(checkInterval);
            }
        })
        .catch(error => {
            console.error('Error checking auth:', error);
            showStatus('Ошибка при проверке статуса', 'error');
        });
}

function showStatus(message, type) {
    const statusElement = document.getElementById('status');
    statusElement.innerHTML = message;
    statusElement.className = type;
    statusElement.style.display = 'block';
}

function showSuccess(user) {
    document.getElementById('auth-section').style.display = 'none';
    
    const userInfo = `
        <h2>✅ Авторизация успешна!</h2>
        <div class="user-info">
            <strong>Данные пользователя:</strong><br>
            👤 Имя: ${user.first_name} ${user.last_name || ''}<br>
            📱 Телефон: ${user.phone_number}<br>
            🔑 Telegram ID: ${user.telegram_id}
        </div>
        <button onclick="logout()">Выйти</button>
    `;
    
    document.getElementById('user-info').innerHTML = userInfo;
    document.getElementById('user-info').style.display = 'block';
    
    localStorage.setItem('telegram_user', JSON.stringify(user));
}

function logout() {
    localStorage.removeItem('telegram_user');
    document.getElementById('user-info').style.display = 'none';
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('auth-btn').disabled = false;
    document.getElementById('status').style.display = 'none';
    authId = null;
}

window.addEventListener('load', function() {
    const savedUser = localStorage.getItem('telegram_user');
    if (savedUser) {
        const user = JSON.parse(savedUser);
        showSuccess(user);
    }
});

window.addEventListener('beforeunload', function() {
    if (checkInterval) {
        clearInterval(checkInterval);
    }
});