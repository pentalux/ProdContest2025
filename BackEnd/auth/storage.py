import time
from collections import defaultdict
from database.db import Database
from subscription_manager import SubscriptionManager

class AuthStorage:
    def __init__(self):
        self.temp_storage = {}
        self.pending_contacts = {}
        self.user_data_collection = {}
        self.database = Database()
        self.subscription_manager = SubscriptionManager()

    def create_session(self, auth_id):
        self.temp_storage[auth_id] = {
            'status': 'pending',
            'user_data': None,
            'created_at': time.time(),
            'chat_id': None
        }
        return auth_id

    def get_session(self, auth_id):
        return self.temp_storage.get(auth_id)

    def update_session(self, auth_id, updates):
        if auth_id in self.temp_storage:
            self.temp_storage[auth_id].update(updates)
            return True
        return False

    def complete_session(self, auth_id, user_data):
        if auth_id in self.temp_storage:
            existing_user = self.database.get_user_by_telegram_id(user_data['telegram_id'])
            
            if existing_user:
                subscription = self.subscription_manager.get_user_subscription(existing_user['site_balance'])
                existing_user['subscription'] = subscription
                
                self.temp_storage[auth_id].update({
                    'status': 'completed',
                    'user_data': existing_user
                })
            else:
                unique_id = self.database.save_user(user_data)
                
                if unique_id:
                    db_user = self.database.get_user_by_unique_id(unique_id)
                    subscription = self.subscription_manager.get_user_subscription(db_user['site_balance'])
                    db_user['subscription'] = subscription
                    
                    self.temp_storage[auth_id].update({
                        'status': 'completed',
                        'user_data': db_user
                    })
                    return True
        return False

    def delete_session(self, auth_id):
        if auth_id in self.temp_storage:
            del self.temp_storage[auth_id]

    def save_user_temp_data(self, chat_id, data):
        self.user_data_collection[chat_id] = data

    def get_user_temp_data(self, chat_id):
        return self.user_data_collection.get(chat_id)

    def delete_user_temp_data(self, chat_id):
        if chat_id in self.user_data_collection:
            del self.user_data_collection[chat_id]

    def cleanup_expired(self):
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.temp_storage.items():
            if current_time - data['created_at'] > 600:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.temp_storage[key]

    def link_chat_to_auth(self, chat_id, auth_id):
        self.pending_contacts[chat_id] = auth_id

    def get_auth_by_chat(self, chat_id):
        return self.pending_contacts.get(chat_id)

    def remove_pending_contact(self, chat_id):
        if chat_id in self.pending_contacts:
            del self.pending_contacts[chat_id]

    def get_user_from_db(self, unique_id):
        user = self.database.get_user_by_unique_id(unique_id)
        if user:
            subscription = self.subscription_manager.get_user_subscription(user['site_balance'])
            user['subscription'] = subscription
        return user

    def get_all_users_from_db(self):
        users = self.database.get_all_users()
        for user in users:
            user['subscription'] = self.subscription_manager.get_user_subscription(user.get('site_balance', 0))
        return users