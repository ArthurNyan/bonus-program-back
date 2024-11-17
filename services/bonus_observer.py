class BonusObserver:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def notify(self, user_id, amount):
        for callback in self._subscribers:
            callback(user_id, amount)

bonus_observer = BonusObserver()

def update_bonus_level(user_id, amount):
    # Логика обновления бонусного уровня на основе новых транзакций
    print(f"Updated bonus level for user {user_id} with transaction amount {amount}")

bonus_observer.subscribe(update_bonus_level)
