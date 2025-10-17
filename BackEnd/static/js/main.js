function openProfile() {
    window.location.href = "/profile?user_id=" + userId;
}

// Обработчики для кнопок навигации
document.querySelector('.prev-btn')?.addEventListener('click', function() {
    alert('Навигация назад');
});

document.querySelector('.next-btn')?.addEventListener('click', function() {
    alert('Навигация вперед');
});

// Функция для обновления данных пользователя
async function updateUserData() {
    try {
        const response = await fetch('/check-user-data?user_id=' + userId);
        const data = await response.json();
        
        if (data.success) {
            const user = data.user;
            
            // Обновляем данные на странице
            document.getElementById('user-first-name').textContent = user.first_name;
            document.getElementById('subscription-name').textContent = user.subscription.name + ' ' + user.subscription.level;
            document.getElementById('subscription-level').textContent = user.subscription.level;
            document.getElementById('subscription-description').textContent = user.subscription.description;
            document.getElementById('site-balance').textContent = user.site_balance;
            document.getElementById('user-balance').textContent = user.user_balance;
            
            if (user.subscription.next_level) {
                document.getElementById('next-level').textContent = user.subscription.next_level;
                document.getElementById('next-balance').textContent = user.subscription.next_min_balance;
            }
            
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