import requests
from config import Config

class BotHandler:
    def __init__(self, auth_storage):
        self.auth_storage = auth_storage
        self.bot_token = Config.BOT_TOKEN
        self.user_states = {}  # chat_id -> состояние диалога

    def process_update(self, update):
        print(f"Received update: {update}")  # Debug log
        if 'message' in update:
            self._handle_message(update['message'])

    def _handle_message(self, message):
        chat_id = message['chat']['id']
        text = message.get('text', '')
        print(f"Processing message from {chat_id}: {text}")  # Debug log

        if text.startswith('/start'):
            self._handle_start_command(chat_id, text)
        elif 'contact' in message:
            print(f"Received contact from {chat_id}")  # Debug log
            self._handle_contact(chat_id, message['contact'])
        elif self.user_states.get(chat_id) == 'waiting_fio':
            self._handle_fio_input(chat_id, text)
        elif text == '/cancel':
            self._cancel_registration(chat_id)

    def _handle_start_command(self, chat_id, text):
        parts = text.split()
        if len(parts) > 1:
            auth_id = parts[1]
            
            if self.auth_storage.get_session(auth_id):
                self.auth_storage.link_chat_to_auth(chat_id, auth_id)
                self.auth_storage.update_session(auth_id, {'chat_id': chat_id})
                self._start_fio_collection(chat_id)
            else:
                self._send_message(chat_id, "❌ Неверная или устаревшая ссылка авторизации.")
        else:
            self._send_message(chat_id, "🔐 Для авторизации используйте ссылку с сайта.")

    def _start_fio_collection(self, chat_id):
        """Начинает сбор ФИО пользователя"""
        self.user_states[chat_id] = 'waiting_fio'
        
        message = (
            "👤 Для завершения регистрации, пожалуйста, введите ваше ФИО (Фамилия Имя Отчество):\n\n"
            "Пример: <code>Иванов Иван Иванович</code>\n\n"
            "Для отмены введите /cancel"
        )
        
        self._send_message(chat_id, message, parse_mode='HTML')

    def _handle_fio_input(self, chat_id, text):
        """Обрабатывает ввод ФИО"""
        if self._validate_fio(text):
            # Сохраняем ФИО во временное хранилище
            fio_parts = text.split()
            fio_data = {
                'last_name': fio_parts[0],
                'first_name': fio_parts[1],
                'middle_name': fio_parts[2] if len(fio_parts) > 2 else ''
            }
            
            self.auth_storage.save_user_temp_data(chat_id, fio_data)
            self.user_states[chat_id] = 'waiting_contact'
            
            # Запрашиваем номер телефона
            self._send_phone_button(chat_id)
        else:
            self._send_message(
                chat_id,
                "❌ Неверный формат ФИО. Пожалуйста, введите Фамилию Имя Отчество через пробел:\n\n"
                "Пример: <code>Иванов Иван Иванович</code>",
                parse_mode='HTML'
            )

    def _validate_fio(self, fio_text):
        """Проверяет корректность формата ФИО"""
        parts = fio_text.split()
        return len(parts) >= 2 and all(len(part) >= 2 for part in parts[:2])

    def _handle_contact(self, chat_id, contact):
        """Обрабатывает получение контакта"""
        print(f"Processing contact for chat_id: {chat_id}")  # Debug log
        
        auth_id = self.auth_storage.get_auth_by_chat(chat_id)
        print(f"Auth ID found: {auth_id}")  # Debug log
        
        if auth_id and self.auth_storage.get_session(auth_id):
            # Получаем сохраненные данные ФИО
            fio_data = self.auth_storage.get_user_temp_data(chat_id)
            print(f"FIO data found: {fio_data}")  # Debug log
            
            if not fio_data:
                self._send_message(chat_id, "❌ Сначала введите ФИО.")
                self._start_fio_collection(chat_id)
                return
            
            # Собираем полные данные пользователя
            user_data = {
                'telegram_id': contact['user_id'],
                'phone_number': contact['phone_number'],
                'first_name': fio_data['first_name'],
                'last_name': fio_data['last_name'],
                'middle_name': fio_data['middle_name']
            }
            
            print(f"User data prepared: {user_data}")  # Debug log
            
            # Завершаем сессию
            success = self.auth_storage.complete_session(auth_id, user_data)
            print(f"Session completion: {success}")  # Debug log
            
            if success:
                self.auth_storage.remove_pending_contact(chat_id)
                self.auth_storage.delete_user_temp_data(chat_id)
                
                # Очищаем состояние
                if chat_id in self.user_states:
                    del self.user_states[chat_id]
                
                # Отправляем подтверждение с данными
                full_name = f"{user_data['last_name']} {user_data['first_name']} {user_data['middle_name']}".strip()
                confirmation_message = (
                    "✅ Регистрация завершена!\n\n"
                    f"👤 <b>ФИО:</b> {full_name}\n"
                    f"📱 <b>Телефон:</b> {user_data['phone_number']}\n"
                    f"💰 <b>Балансы:</b> Пользователь: 0 руб., Сайт: 0 руб.\n\n"
                    "Вы можете вернуться на сайт."
                )
                
                self._send_message(chat_id, confirmation_message, parse_mode='HTML', reply_markup={'remove_keyboard': True})
            else:
                self._send_message(chat_id, "❌ Ошибка при сохранении данных.")
        else:
            print(f"No session found for auth_id: {auth_id}")  # Debug log
            self._send_message(chat_id, "❌ Сессия авторизации не найдена или устарела.")

    def _send_phone_button(self, chat_id):
        """Отправляем кнопку запроса номера телефона"""
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
            "📱 Теперь поделитесь своим номером телефона для завершения регистрации:",
            reply_markup=keyboard
        )

    def _cancel_registration(self, chat_id):
        """Отменяет процесс регистрации"""
        if chat_id in self.user_states:
            del self.user_states[chat_id]
        
        self.auth_storage.delete_user_temp_data(chat_id)
        
        auth_id = self.auth_storage.get_auth_by_chat(chat_id)
        if auth_id:
            self.auth_storage.remove_pending_contact(chat_id)
            self.auth_storage.delete_session(auth_id)
        
        self._send_message(
            chat_id,
            "❌ Регистрация отменена.",
            reply_markup={'remove_keyboard': True}
        )

    def _send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        """Отправляем сообщение в Telegram"""
        url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        if parse_mode:
            payload['parse_mode'] = parse_mode
        
        try:
            print(f"Sending message to {chat_id}: {text}")  # Debug log
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            print(f"Telegram API response: {result}")  # Debug log
            return result
        except Exception as e:
            print(f"Error sending message: {e}")
            return None