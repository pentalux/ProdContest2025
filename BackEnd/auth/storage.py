import time
from collections import defaultdict
from config import Config

class AuthStorage:
    def __init__(self):
        self.temp_storage = {}
        self.user_messages = defaultdict(list)
        self.pending_contacts = {}

    def create_session(self, auth_id):
        self.temp_storage[auth_id] = {
            'status': 'pending',
            'user_data': None,
            'created_at': time.time()
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
            self.temp_storage[auth_id].update({
                'status': 'completed',
                'user_data': user_data
            })
            return True
        return False

    def delete_session(self, auth_id):
        if auth_id in self.temp_storage:
            del self.temp_storage[auth_id]

    def cleanup_expired(self):
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.temp_storage.items():
            if current_time - data['created_at'] > Config.SESSION_TIMEOUT:
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