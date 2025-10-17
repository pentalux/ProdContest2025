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
                // Всех пользователей перекидываем на главную страницу
                window.location.href = data.redirect_url;
            } else if (data.status === 'pending') {
                showStatus('⌛ Ожидание завершения регистрации в Telegram...<br><small>Пожалуйста, введите ФИО и поделитесь номером телефона в боте</small>', 'pending');
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

window.addEventListener('beforeunload', function() {
    if (checkInterval) {
        clearInterval(checkInterval);
    }
});