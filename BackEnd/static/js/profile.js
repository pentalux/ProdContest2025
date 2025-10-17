function goBack() {
    window.location.href = "/main?user_id=" + userId;
}

function openAdminPanel() {
    window.location.href = "/admin?user_id=" + userId;
}

function openSubscriptionsAdmin() {
    window.location.href = "/admin-subscriptions?user_id=" + userId;
}

function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        window.location.href = "/";
    }
}

// Функция для обновления данных пользователя
async function updateUserData() {
    try {
        const response = await fetch('/check-user-data?user_id=' + userId);
        const data = await response.json();
        
        if (data.success) {
            const user = data.user;
            
            // Обновляем данные на странице
            document.getElementById('user-full-name').textContent = user.last_name + ' ' + user.first_name + ' ' + (user.middle_name || '');
            document.getElementById('user-phone').textContent = user.phone_number;
            document.getElementById('user-balance').textContent = user.user_balance + ' руб.';
            document.getElementById('site-balance').textContent = user.site_balance + ' руб.';
            document.getElementById('subscription-name').textContent = user.subscription.name + ' ' + user.subscription.level;
            document.getElementById('subscription-level').textContent = user.subscription.level;
            document.getElementById('subscription-min-balance').textContent = user.subscription.min_balance;
            
            // Обновляем класс подписки для стилей
            const subscriptionCard = document.getElementById('subscription-card');
            subscriptionCard.className = 'subscription-card ' + user.subscription.level.toLowerCase();
        }
    } catch (error) {
        console.error('Ошибка при обновлении данных:', error);
    }
}

// Обновляем данные каждые 30 секунд
setInterval(updateUserData, 30000);

// Также обновляем при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    updateUserData();
});