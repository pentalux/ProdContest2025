import requests
from config import Config

class BotHandler:
    def __init__(self, auth_storage):
        self.auth_storage = auth_storage
        self.bot_token = Config.BOT_TOKEN

    def process_update(self, update):
        if 'message' in update:
            self._handle_message(update['message'])

    def _handle_message(self, message):
        chat_id = message['chat']['id']
        text = message.get('text', '')

        if text.startswith('/start'):
            self._handle_start_command(chat_id, text)
        elif 'contact' in message:
            self._handle_contact(chat_id, message['contact'])

    def _handle_start_command(self, chat_id, text):
        parts = text.split()
        if len(parts) > 1:
            auth_id = parts[1]
            
            if self.auth_storage.get_session(auth_id):
                self.auth_storage.link_chat_to_auth(chat_id, auth_id)
                self.auth_storage.update_session(auth_id, {'chat_id': chat_id})
                self._send_phone_button(chat_id)
            else:
                self._send_message(chat_id, "❌ Неверная или устаревшая ссылка авторизации.")
        else:
            self._send_message(chat_id, "🔐 Для авторизации используйте ссылку с сайта.")

    def _handle_contact(self, chat_id, contact):
        auth_id = self.auth_storage.get_auth_by_chat(chat_id)
        
        if auth_id and self.auth_storage.get_session(auth_id):
            user_data = {
                'telegram_id': contact['user_id'],
                'phone_number': contact['phone_number'],
                'first_name': contact.get('first_name', ''),
                'last_name': contact.get('last_name', ''),
                'username': contact.get('username', '')
            }
            
            self.auth_storage.complete_session(auth_id, user_data)
            self.auth_storage.remove_pending_contact(chat_id)
            
            self._send_message(chat_id, "✅ Авторизация успешна! Вы можете вернуться на сайт.")
        else:
            self._send_message(chat_id, "❌ Сессия авторизации не найдена.")

    def _send_phone_button(self, chat_id):
        keyboard = {
            'keyboard': [[{
                'text': '📱 Отправить номер телефона',
                'request_contact': True
            }]],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        self._send_message(
            chat_id, 
            "🔐 Для авторизации на сайте поделитесь своим номером телефона:", 
            reply_markup=keyboard
        )

    def _send_message(self, chat_id, text, reply_markup=None):
        url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None