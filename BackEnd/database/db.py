import sqlite3
import hashlib

class Database:
    def __init__(self):
        self.db_name = 'users.db'
        self.init_database()

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            unique_id TEXT PRIMARY KEY,
            telegram_id INTEGER NOT NULL,
            phone_number TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            middle_name TEXT,
            user_balance INTEGER DEFAULT 0,
            site_balance INTEGER DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()
        print("База данных инициализирована успешно!")

    def get_connection(self):
        """Возвращает соединение с базой данных"""
        return sqlite3.connect(self.db_name)

    def _generate_unique_id(self, phone_number, first_name, last_name):
        """Генерирует уникальный ID на основе телефона и ФИО"""
        data_string = f"{phone_number}{first_name}{last_name}".encode('utf-8')
        return hashlib.sha256(data_string).hexdigest()[:16]

    def user_exists(self, unique_id):
        """Проверяет существует ли пользователь с таким unique_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT unique_id FROM users WHERE unique_id = ?', (unique_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None

    def save_user(self, user_data):
        """Сохраняет пользователя в базу данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Генерируем уникальный ID
        unique_id = self._generate_unique_id(
            user_data['phone_number'],
            user_data['first_name'],
            user_data['last_name']
        )
        
        try:
            cursor.execute('''
            INSERT INTO users 
            (unique_id, telegram_id, phone_number, first_name, last_name, middle_name, user_balance, site_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                unique_id,
                user_data['telegram_id'],
                user_data['phone_number'],
                user_data['first_name'],
                user_data['last_name'],
                user_data.get('middle_name', ''),
                0,  # user_balance
                0   # site_balance
            ))
            
            conn.commit()
            conn.close()
            
            print(f"Пользователь сохранен с уникальным ID: {unique_id}")
            return unique_id
            
        except sqlite3.IntegrityError:
            print("Пользователь с таким unique_id уже существует")
            # Если пользователь уже есть, возвращаем его unique_id
            conn.close()
            return unique_id
        except Exception as e:
            print(f"Ошибка при сохранении пользователя: {e}")
            conn.close()
            return None

    def get_user_by_unique_id(self, unique_id):
        """Получает пользователя по unique_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE unique_id = ?', (unique_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return self._row_to_dict(result)
        return None

    def get_user_by_telegram_id(self, telegram_id):
        """Получает пользователя по telegram_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return self._row_to_dict(result)
        return None

    def _row_to_dict(self, row):
        """Преобразует строку базы данных в словарь"""
        return {
            'unique_id': row[0],
            'telegram_id': row[1],
            'phone_number': row[2],
            'first_name': row[3],
            'last_name': row[4],
            'middle_name': row[5],
            'user_balance': row[6],
            'site_balance': row[7]
        }

    def update_balance(self, unique_id, user_balance=None, site_balance=None):
        """Обновляет балансы пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if user_balance is not None:
            updates.append("user_balance = ?")
            params.append(user_balance)
        
        if site_balance is not None:
            updates.append("site_balance = ?")
            params.append(site_balance)
        
        if updates:
            params.append(unique_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE unique_id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()