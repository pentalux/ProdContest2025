import os
import json

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '567845675')
    BOT_TOKEN = '8495999262:AAE3alV0b464Xjv0IhQ24bT-6yUgk2GHz-c'
    BOT_USERNAME = 'tbankkeybot'
    SESSION_TIMEOUT = 600  # 10 минут
    DATABASE_NAME = 'users.db'
    ADMIN_DATA_FILE = 'admins.json'
    ADMIN_PASSWORD_FILE = 'admin_password.json'
    SUBSCRIPTIONS_FILE = 'subscriptions.json'
    
    # Инициализация файлов
    @staticmethod
    def init_files():
        # Инициализация файла админов
        if not os.path.exists(Config.ADMIN_DATA_FILE):
            with open(Config.ADMIN_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
        # Инициализация файла пароля
        if not os.path.exists(Config.ADMIN_PASSWORD_FILE):
            with open(Config.ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
                json.dump({"password": "tbankclass"}, f, ensure_ascii=False, indent=2)
        
        # Инициализация файла подписок
        if not os.path.exists(Config.SUBSCRIPTIONS_FILE):
            default_subscriptions = {
                "subscriptions": [
                    {
                        "id": 0,
                        "name": "Pro",
                        "level": "Black",
                        "min_balance": 0,
                        "description": "Базовая подписка с минимальными возможностями",
                        "features": [
                            "Доступ к базовому функционалу",
                            "Ограниченная поддержка",
                            "Стандартные лимиты"
                        ]
                    },
                    {
                        "id": 1,
                        "name": "Premium",
                        "level": "Bronze",
                        "min_balance": 1000,
                        "description": "Бронзовая подписка Pro с расширенными возможностями",
                        "features": [
                            "Расширенный функционал",
                            "Приоритетная поддержка",
                            "Увеличенные лимиты",
                            "Доступ к базовым аналитикам"
                        ]
                    },
                    {
                        "id": 2,
                        "name": "Premium",
                        "level": "Silver", 
                        "min_balance": 5000,
                        "description": "Серебряная подписка Pro с премиум функциями",
                        "features": [
                            "Полный функционал Pro",
                            "Экспресс-поддержка 24/7",
                            "Высокие лимиты",
                            "Расширенная аналитика",
                            "Персональный менеджер"
                        ]
                    },
                    {
                        "id": 3,
                        "name": "Premium",
                        "level": "Gold",
                        "min_balance": 15000,
                        "description": "Золотая премиум подписка с эксклюзивными возможностями",
                        "features": [
                            "Эксклюзивный функционал Premium",
                            "Персональная поддержка",
                            "Максимальные лимиты",
                            "Глубокая аналитика и отчеты",
                            "Доступ к бета-функциям",
                            "Приоритет в очередях"
                        ]
                    },
                    {
                        "id": 4,
                        "name": "Premium",
                        "level": "Diamond",
                        "min_balance": 50000,
                        "description": "Алмазная премиум подписка с максимальными привилегиями",
                        "features": [
                            "Все возможности платформы",
                            "Выделенная команда поддержки",
                            "Безлимитные возможности",
                            "Кастомная аналитика",
                            "Ранний доступ к новым функциям",
                            "Эксклюзивные мероприятия",
                            "Индивидуальные решения"
                        ]
                    }
                ]
            }
            with open(Config.SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_subscriptions, f, ensure_ascii=False, indent=2)

# Инициализируем файлы при импорте
Config.init_files()