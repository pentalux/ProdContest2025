import requests
from config import Config
from admin_manager import AdminManager

class BotHandler:
    def __init__(self, auth_storage):
        self.auth_storage = auth_storage
        self.bot_token = Config.BOT_TOKEN
        self.user_states = {}
        self.admin_manager = AdminManager()

    def process_update(self, update):
        if 'message' in update:
            self._handle_message(update['message'])

    def _handle_message(self, message):
        chat_id = message['chat']['id']
        text = message.get('text', '')

        if text.startswith('/start'):
            self._handle_start_command(chat_id, text)
        elif text.startswith('/admin'):
            self._handle_admin_command(chat_id, text)
        elif text.startswith('/editadmin'):
            self._handle_edit_admin_command(chat_id, text)
        elif 'contact' in message:
            self._handle_contact(chat_id, message['contact'])
        elif self.user_states.get(chat_id) == 'waiting_fio':
            self._handle_fio_input(chat_id, text)
        elif text == '/cancel':
            self._cancel_registration(chat_id)

    def _handle_start_command(self, chat_id, text):
        parts = text.split()
        if len(parts) > 1:
            auth_id = parts[1]
            
            session = self.auth_storage.get_session(auth_id)
            
            if session:
                self.auth_storage.link_chat_to_auth(chat_id, auth_id)
                self.auth_storage.update_session(auth_id, {'chat_id': chat_id})
                
                existing_user = self.auth_storage.database.get_user_by_telegram_id(chat_id)
                
                if existing_user:
                    self._complete_existing_user_session(auth_id, existing_user, chat_id)
                else:
                    self._start_fio_collection(chat_id)
            else:
                self._send_message(chat_id, "❌ Неверная или устаревшая ссылка авторизации.")
        else:
            self._send_message(chat_id, "🔐 Для авторизации используйте ссылку с сайта.")

    def _complete_existing_user_session(self, auth_id, user_data, chat_id):
        from subscription_manager import SubscriptionManager
        subscription_manager = SubscriptionManager()
        subscription = subscription_manager.get_user_subscription(user_data['site_balance'])
        user_data['subscription'] = subscription
        user_data['is_admin'] = self.admin_manager.is_admin(user_data['telegram_id'])
        
        self.auth_storage.complete_session(auth_id, user_data)
        
        full_name = f"{user_data['last_name']} {user_data['first_name']} {user_data['middle_name']}".strip()
        confirmation_message = (
            "✅ Авторизация успешна!\n\n"
            f"👤 <b>Добро пожаловать назад, {user_data['first_name']}!</b>\n"
            f"💰 <b>Балансы:</b> Пользователь: {user_data['user_balance']} руб., Сайт: {user_data['site_balance']} руб.\n"
            f"🎯 <b>Текущая подписка:</b> {subscription['name']} {subscription['level']}\n"
        )
        
        if user_data['is_admin']:
            confirmation_message += "\n👑 <b>Вы администратор!</b>"
        
        confirmation_message += "\n\nВы можете вернуться на сайт."
        
        self._send_message(chat_id, confirmation_message, parse_mode='HTML', reply_markup={'remove_keyboard': True})

    def _handle_admin_command(self, chat_id, text):
        parts = text.split()
        if len(parts) < 2:
            self._send_message(chat_id, "❌ Использование: /admin <пароль>")
            return
        
        password = parts[1]
        
        if self.admin_manager.check_password(password):
            if self.admin_manager.add_admin(chat_id):
                self._send_message(chat_id, "✅ Вы успешно стали администратором!")
            else:
                self._send_message(chat_id, "❌ Ошибка при добавлении в администраторы.")
        else:
            self._send_message(chat_id, "❌ Неверный пароль администратора.")

    def _handle_edit_admin_command(self, chat_id, text):
        if not self.admin_manager.is_admin(chat_id):
            self._send_message(chat_id, "❌ У вас нет прав для выполнения этой команды.")
            return
        
        parts = text.split()
        if len(parts) < 2:
            self._send_message(chat_id, "❌ Использование: /editadmin <новый_пароль>")
            return
        
        new_password = parts[1]
        
        if self.admin_manager.change_password(new_password):
            self._send_message(chat_id, "✅ Пароль администратора успешно изменен!")
        else:
            self._send_message(chat_id, "❌ Ошибка при изменении пароля.")

    def _start_fio_collection(self, chat_id):
        self.user_states[chat_id] = 'waiting_fio'
        
        message = (
            "👤 Для завершения регистрации, пожалуйста, введите ваше ФИО (Фамилия Имя Отчество):\n\n"
            "Пример: <code>Иванов Иван Иванович</code>\n\n"
            "Для отмены введите /cancel"
        )
        
        self._send_message(chat_id, message, parse_mode='HTML')

    def _handle_fio_input(self, chat_id, text):
        if self._validate_fio(text):
            fio_parts = text.split()
            fio_data = {
                'last_name': fio_parts[0],
                'first_name': fio_parts[1],
                'middle_name': fio_parts[2] if len(fio_parts) > 2 else ''
            }
            
            self.auth_storage.save_user_temp_data(chat_id, fio_data)
            self.user_states[chat_id] = 'waiting_contact'
            self._send_phone_button(chat_id)
        else:
            self._send_message(
                chat_id,
                "❌ Неверный формат ФИО. Пожалуйста, введите Фамилию Имя Отчество через пробел:\n\n"
                "Пример: <code>Иванов Иван Иванович</code>",
                parse_mode='HTML'
            )

    def _validate_fio(self, fio_text):
        parts = fio_text.split()
        return len(parts) >= 2 and all(len(part) >= 2 for part in parts[:2])

    def _handle_contact(self, chat_id, contact):
        auth_id = self.auth_storage.get_auth_by_chat(chat_id)
        
        if auth_id and self.auth_storage.get_session(auth_id):
            fio_data = self.auth_storage.get_user_temp_data(chat_id)
            
            if not fio_data:
                self._send_message(chat_id, "❌ Сначала введите ФИО.")
                self._start_fio_collection(chat_id)
                return
            
            user_data = {
                'telegram_id': contact['user_id'],
                'phone_number': contact['phone_number'],
                'first_name': fio_data['first_name'],
                'last_name': fio_data['last_name'],
                'middle_name': fio_data['middle_name']
            }
            
            success = self.auth_storage.complete_session(auth_id, user_data)
            
            if success:
                self.auth_storage.remove_pending_contact(chat_id)
                self.auth_storage.delete_user_temp_data(chat_id)
                
                if chat_id in self.user_states:
                    del self.user_states[chat_id]
                
                is_admin = self.admin_manager.is_admin(contact['user_id'])
                full_name = f"{user_data['last_name']} {user_data['first_name']} {user_data['middle_name']}".strip()
                confirmation_message = (
                    "✅ Регистрация завершена!\n\n"
                    f"👤 <b>ФИО:</b> {full_name}\n"
                    f"📱 <b>Телефон:</b> {user_data['phone_number']}\n"
                    f"💰 <b>Балансы:</b> Пользователь: 0 руб., Сайт: 0 руб.\n"
                )
                
                if is_admin:
                    confirmation_message += "\n👑 <b>Вы администратор!</b>"
                
                confirmation_message += "\n\nВы можете вернуться на сайт."
                
                self._send_message(chat_id, confirmation_message, parse_mode='HTML', reply_markup={'remove_keyboard': True})
            else:
                self._send_message(chat_id, "❌ Ошибка при сохранении данных.")
        else:
            self._send_message(chat_id, "❌ Сессия авторизации не найдена или устарела.")

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
            "📱 Теперь поделитесь своим номером телефона для завершения регистрации:",
            reply_markup=keyboard
        )

    def _cancel_registration(self, chat_id):
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
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None