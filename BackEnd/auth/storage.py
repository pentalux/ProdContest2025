import time
from collections import defaultdict
from database.db import Database
from subscription_manager import SubscriptionManager

class AuthStorage:
    def __init__(self):
        self.temp_storage = {}
        self.user_messages = defaultdict(list)
        self.pending_contacts = {}
        self.user_data_collection = {}
        self.database = Database()
        self.subscription_manager = SubscriptionManager()
        print("AuthStorage initialized")

    def create_session(self, auth_id):
        """Создает новую сессию авторизации"""
        self.temp_storage[auth_id] = {
            'status': 'pending',
            'user_data': None,
            'created_at': time.time(),
            'chat_id': None
        }
        print(f"Session created: {auth_id}")
        print(f"Current sessions: {list(self.temp_storage.keys())}")
        return auth_id

    def get_session(self, auth_id):
        """Получает сессию по auth_id"""
        session = self.temp_storage.get(auth_id)
        print(f"Getting session {auth_id}: {session is not None}")
        return session

    def update_session(self, auth_id, updates):
        if auth_id in self.temp_storage:
            self.temp_storage[auth_id].update(updates)
            print(f"Session updated: {auth_id}")
            return True
        print(f"Session not found for update: {auth_id}")
        return False

    def complete_session(self, auth_id, user_data):
        if auth_id in self.temp_storage:
            # Проверяем, существует ли пользователь уже
            existing_user = self.database.get_user_by_telegram_id(user_data['telegram_id'])
            
            if existing_user:
                # Пользователь уже существует - обновляем подписку и возвращаем существующие данные
                subscription = self.subscription_manager.get_user_subscription(existing_user['site_balance'])
                existing_user['subscription'] = subscription
                existing_user['is_admin'] = user_data.get('is_admin', False)
                
                self.temp_storage[auth_id].update({
                    'status': 'completed',
                    'user_data': existing_user
                })
                print(f"Existing user session completed: {auth_id}")
            else:
                # Новый пользователь - сохраняем в базу данных
                unique_id = self.database.save_user(user_data)
                
                if unique_id:
                    # Получаем полные данные пользователя из БД
                    db_user = self.database.get_user_by_unique_id(unique_id)
                    # Обновляем подписку
                    subscription = self.subscription_manager.get_user_subscription(db_user['site_balance'])
                    db_user['subscription'] = subscription
                    
                    self.temp_storage[auth_id].update({
                        'status': 'completed',
                        'user_data': db_user
                    })
                    print(f"New user session completed: {auth_id}")
                    return True
        else:
            print(f"Session not found for completion: {auth_id}")
        
        return False

    def delete_session(self, auth_id):
        if auth_id in self.temp_storage:
            del self.temp_storage[auth_id]
            print(f"Session deleted: {auth_id}")

    def save_user_temp_data(self, chat_id, data):
        self.user_data_collection[chat_id] = data
        print(f"Temp data saved for chat {chat_id}")

    def get_user_temp_data(self, chat_id):
        data = self.user_data_collection.get(chat_id)
        print(f"Getting temp data for chat {chat_id}: {data is not None}")
        return data

    def delete_user_temp_data(self, chat_id):
        if chat_id in self.user_data_collection:
            del self.user_data_collection[chat_id]
            print(f"Temp data deleted for chat {chat_id}")

    def cleanup_expired(self):
        """Очищает просроченные сессии"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.temp_storage.items():
            if current_time - data['created_at'] > 600:  # 10 минут
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.temp_storage[key]
        
        if expired_keys:
            print(f"Cleaned up expired sessions: {expired_keys}")

    def link_chat_to_auth(self, chat_id, auth_id):
        self.pending_contacts[chat_id] = auth_id
        print(f"Linked chat {chat_id} to auth {auth_id}")

    def get_auth_by_chat(self, chat_id):
        auth_id = self.pending_contacts.get(chat_id)
        print(f"Getting auth for chat {chat_id}: {auth_id}")
        return auth_id

    def remove_pending_contact(self, chat_id):
        if chat_id in self.pending_contacts:
            del self.pending_contacts[chat_id]
            print(f"Removed pending contact for chat {chat_id}")

    def get_user_from_db(self, unique_id):
        """Получает пользователя из базы данных и обновляет подписку"""
        user = self.database.get_user_by_unique_id(unique_id)
        if user:
            # Всегда обновляем подписку при получении пользователя
            subscription = self.subscription_manager.get_user_subscription(user['site_balance'])
            user['subscription'] = subscription
        return user

    def get_all_users_from_db(self):
        """Получает всех пользователей из базы данных"""
        users = self.database.get_all_users()
        # Добавляем информацию о подписке для каждого пользователя
        for user in users:
            user['subscription'] = self.subscription_manager.get_user_subscription(user.get('site_balance', 0))
        return users

    def update_user_balance(self, unique_id, user_balance=None, site_balance=None):
        return self.database.update_balance(unique_id, user_balance, site_balance)