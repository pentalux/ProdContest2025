import json
from config import Config

class AdminManager:
    def __init__(self):
        self.admin_file = Config.ADMIN_DATA_FILE
        self.password_file = Config.ADMIN_PASSWORD_FILE

    def is_admin(self, telegram_id):
        """Проверяет является ли пользователь админом"""
        try:
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                admins = json.load(f)
            return str(telegram_id) in admins
        except Exception as e:
            print(f"Error reading admin file: {e}")
            return False

    def add_admin(self, telegram_id):
        """Добавляет пользователя в админы"""
        try:
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                admins = json.load(f)
            
            telegram_id_str = str(telegram_id)
            if telegram_id_str not in admins:
                admins.append(telegram_id_str)
                
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(admins, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False

    def get_all_admins(self):
        """Получает список всех админов"""
        try:
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error getting admins: {e}")
            return []

    def check_password(self, password):
        """Проверяет пароль админа"""
        try:
            with open(self.password_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('password') == password
        except Exception as e:
            print(f"Error checking password: {e}")
            return False

    def change_password(self, new_password):
        """Меняет пароль админа"""
        try:
            with open(self.password_file, 'w', encoding='utf-8') as f:
                json.dump({"password": new_password}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False