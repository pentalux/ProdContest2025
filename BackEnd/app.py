from flask import Flask, request, jsonify, render_template, redirect, url_for
import secrets
import time
from auth.storage import AuthStorage
from bot.handlers import BotHandler
from admin_manager import AdminManager
from subscription_manager import SubscriptionManager
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Инициализация компонентов
auth_storage = AuthStorage()
bot_handler = BotHandler(auth_storage)
admin_manager = AdminManager()
subscription_manager = SubscriptionManager()

# Хранилище сессий пользователей
user_sessions = {}

def update_user_subscription(user_data):
    """Обновляет подписку пользователя на основе текущего баланса"""
    subscription = subscription_manager.get_user_subscription(user_data['site_balance'])
    user_data['subscription'] = subscription
    return user_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    user_id = request.args.get('user_id')
    if not user_id or user_id not in user_sessions:
        return redirect(url_for('index'))
    
    user_data = user_sessions[user_id]
    user_data = update_user_subscription(user_data)
    user_sessions[user_id] = user_data
    
    return render_template('main.html', user=user_data)

@app.route('/profile')
def profile():
    user_id = request.args.get('user_id')
    if not user_id or user_id not in user_sessions:
        return redirect(url_for('index'))
    
    user_data = user_sessions[user_id]
    user_data = update_user_subscription(user_data)
    user_sessions[user_id] = user_data
    
    is_admin = admin_manager.is_admin(user_data['telegram_id'])
    
    return render_template('profile.html', user=user_data, is_admin=is_admin)

@app.route('/admin')
def admin_panel():
    user_id = request.args.get('user_id')
    if not user_id or user_id not in user_sessions:
        return redirect(url_for('index'))
    
    user_data = user_sessions[user_id]
    
    if not admin_manager.is_admin(user_data['telegram_id']):
        return redirect(url_for('main', user_id=user_id))
    
    all_users = auth_storage.get_all_users_from_db()
    
    return render_template('admin.html', user=user_data, users=all_users)

@app.route('/admin-subscriptions')
def admin_subscriptions():
    user_id = request.args.get('user_id')
    if not user_id or user_id not in user_sessions:
        return redirect(url_for('index'))
    
    user_data = user_sessions[user_id]
    
    if not admin_manager.is_admin(user_data['telegram_id']):
        return redirect(url_for('main', user_id=user_id))
    
    subscriptions = subscription_manager.get_subscriptions()
    
    return render_template('admin_subscriptions.html', user=user_data, subscriptions=subscriptions)

@app.route('/admin-edit-user/<user_unique_id>')
def admin_edit_user(user_unique_id):
    admin_user_id = request.args.get('user_id')
    if not admin_user_id or admin_user_id not in user_sessions:
        return redirect(url_for('index'))
    
    admin_user_data = user_sessions[admin_user_id]
    
    if not admin_manager.is_admin(admin_user_data['telegram_id']):
        return redirect(url_for('main', user_id=admin_user_id))
    
    user_to_edit = auth_storage.get_user_from_db(user_unique_id)
    
    if not user_to_edit:
        return redirect(url_for('admin_panel', user_id=admin_user_id))
    
    subscription = subscription_manager.get_user_subscription(user_to_edit['site_balance'])
    user_to_edit['subscription'] = subscription
    
    return render_template('admin_edit_user.html', 
                         admin_user=admin_user_data, 
                         user=user_to_edit)

@app.route('/update-user-data', methods=['POST'])
def update_user_data():
    admin_user_id = request.form.get('admin_user_id')
    user_unique_id = request.form.get('user_unique_id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    middle_name = request.form.get('middle_name')
    phone_number = request.form.get('phone_number')
    user_balance = int(request.form.get('user_balance', 0))
    site_balance = int(request.form.get('site_balance', 0))
    
    if not admin_user_id or admin_user_id not in user_sessions:
        return jsonify({'success': False, 'error': 'Admin user not found'})
    
    admin_user_data = user_sessions[admin_user_id]
    
    if not admin_manager.is_admin(admin_user_data['telegram_id']):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    success = auth_storage.database.update_user_data(
        user_unique_id, 
        first_name, 
        last_name, 
        middle_name, 
        phone_number, 
        user_balance, 
        site_balance
    )
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Update failed'})

@app.route('/update-subscription', methods=['POST'])
def update_subscription():
    user_id = request.form.get('user_id')
    subscription_id = int(request.form.get('subscription_id'))
    new_min_balance = int(request.form.get('min_balance'))
    new_description = request.form.get('description')
    
    if not user_id or user_id not in user_sessions:
        return jsonify({'success': False, 'error': 'User not found'})
    
    user_data = user_sessions[user_id]
    
    if not admin_manager.is_admin(user_data['telegram_id']):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    success = subscription_manager.update_subscription(subscription_id, new_min_balance, new_description)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Update failed'})

@app.route('/check-user-data')
def check_user_data():
    """API для проверки и обновления данных пользователя"""
    user_id = request.args.get('user_id')
    if not user_id or user_id not in user_sessions:
        return jsonify({'success': False, 'error': 'User not found'})
    
    user_data = auth_storage.get_user_from_db(user_id)
    
    if user_data:
        user_sessions[user_id] = user_data
        user_data['is_admin'] = admin_manager.is_admin(user_data['telegram_id'])
        
        return jsonify({
            'success': True,
            'user': user_data
        })
    else:
        return jsonify({'success': False, 'error': 'User data not found'})

@app.route('/init-auth')
def init_auth():
    auth_storage.cleanup_expired()
    
    auth_id = secrets.token_hex(16)
    auth_storage.create_session(auth_id)
    
    bot_url = f'https://t.me/{Config.BOT_USERNAME}?start={auth_id}'
    
    return jsonify({
        'auth_id': auth_id,
        'bot_url': bot_url
    })

@app.route('/check-auth/<auth_id>')
def check_auth(auth_id):
    session = auth_storage.get_session(auth_id)
    
    if not session:
        return jsonify({'status': 'not_found'})
    
    if session['status'] == 'completed':
        user_data = session['user_data']
        auth_storage.delete_session(auth_id)
        
        user_data['is_admin'] = admin_manager.is_admin(user_data['telegram_id'])
        user_sessions[user_data['unique_id']] = user_data
        
        redirect_url = url_for('main', user_id=user_data['unique_id'])
        
        return jsonify({
            'status': 'completed', 
            'user': user_data,
            'redirect_url': redirect_url
        })
    
    return jsonify({'status': session['status']})

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    import threading
    from bot.polling import BotPolling
    
    bot_polling = BotPolling(bot_handler)
    polling_thread = threading.Thread(target=bot_polling.start_polling, daemon=True)
    polling_thread.start()
    
    print("Starting application...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)