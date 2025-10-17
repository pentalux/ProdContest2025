import requests
import time
from config import Config

class BotPolling:
    def __init__(self, bot_handler):
        self.bot_handler = bot_handler
        self.offset = 0

    def start_polling(self):
        print("Bot polling started...")
        while True:
            try:
                url = f'https://api.telegram.org/bot{Config.BOT_TOKEN}/getUpdates'
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