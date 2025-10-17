import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '567845675')
    BOT_TOKEN = '7328105407:AAE0hoKYS6MLzNsQnEGS-bT-DB2dCwxFc2U'
    BOT_USERNAME = 'private239bot'
    SESSION_TIMEOUT = 600  # 10 минут
    DATABASE_NAME = 'users.db'