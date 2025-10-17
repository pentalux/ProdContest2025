import requests
import time
import threading
from config import Config  # Добавьте этот импорт

class BotPolling:
    def __init__(self, bot_handler):
        self.bot_handler = bot_handler
        self.offset = 0
        self.running = False

    def start_polling(self):
        self.running = True
        polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        polling_thread.start()
        print("Bot polling started...")

    def stop_polling(self):
        self.running = False

    def _polling_loop(self):
        while self.running:
            try:
                url = f'https://api.telegram.org/bot{Config.BOT_TOKEN}/getUpdates'  # Используем Config
                params = {
                    'offset': self.offset,
                    'timeout': 30,
                    'allowed_updates': ['message', 'callback_query']
                }
                
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('ok') and data.get('result'):
                        for update in data['result']:
                            self.offset = update['update_id'] + 1
                            self.bot_handler.process_update(update)
            
            except requests.exceptions.Timeout:
                continue
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(5)