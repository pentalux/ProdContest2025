import json
from config import Config

class SubscriptionManager:
    def __init__(self):
        self.subscriptions_file = Config.SUBSCRIPTIONS_FILE

    def get_subscriptions(self):
        """Получает список всех подписок"""
        try:
            with open(self.subscriptions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            subscriptions = data.get('subscriptions', [])
            
            # Добавляем информацию о следующей подписке
            for i, subscription in enumerate(subscriptions):
                if i < len(subscriptions) - 1:
                    subscription['next_level'] = subscriptions[i + 1]['level']
                    subscription['next_min_balance'] = subscriptions[i + 1]['min_balance']
                else:
                    subscription['next_level'] = 'Максимальная'
                    subscription['next_min_balance'] = subscription['min_balance']
            
            return subscriptions
        except Exception as e:
            print(f"Error reading subscriptions: {e}")
            return []

    def get_user_subscription(self, site_balance):
        """Определяет подписку пользователя на основе баланса"""
        subscriptions = self.get_subscriptions()
        user_subscription = subscriptions[0]  # Базовая подписка по умолчанию
        
        for subscription in subscriptions:
            if site_balance >= subscription['min_balance']:
                user_subscription = subscription
            else:
                break
                
        return user_subscription

    def update_subscription(self, subscription_id, new_min_balance=None, new_description=None):
        """Обновляет условия подписки и описание"""
        try:
            with open(self.subscriptions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            subscriptions = data.get('subscriptions', [])
            for subscription in subscriptions:
                if subscription['id'] == subscription_id:
                    if new_min_balance is not None:
                        subscription['min_balance'] = new_min_balance
                    if new_description is not None:
                        subscription['description'] = new_description
                    break
            
            with open(self.subscriptions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating subscription: {e}")
            return False

    def update_subscription_description(self, subscription_id, new_description):
        """Обновляет только описание подписки"""
        return self.update_subscription(subscription_id, new_description=new_description)

    def get_subscription_by_id(self, subscription_id):
        """Получает подписку по ID"""
        subscriptions = self.get_subscriptions()
        for subscription in subscriptions:
            if subscription['id'] == subscription_id:
                return subscription
        return None