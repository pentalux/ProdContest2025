from flask import Flask, request, jsonify, render_template
import secrets
from auth.storage import AuthStorage
from bot.handlers import BotHandler
from bot.polling import BotPolling

app = Flask(__name__)
app.secret_key = '567845675'


auth_storage = AuthStorage()
bot_handler = BotHandler(auth_storage)
bot_polling = BotPolling(bot_handler)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init-auth')
def init_auth():
    auth_storage.cleanup_expired()
    
    auth_id = secrets.token_hex(16)
    auth_storage.create_session(auth_id)
    
    bot_url = f'https://t.me/private239bot?start={auth_id}'
    
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
        return jsonify({'status': 'completed', 'user': user_data})
    
    return jsonify({'status': session['status']})

# Убраны роуты для админки и API пользователей

if __name__ == '__main__':
    # Запускаем polling при старте приложения
    bot_polling.start_polling()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)