from app.models import FoodItem
from hashlib import sha256

def inventory_snapshot(fooditems: list[FoodItem]) -> str:
    to_hash: str = ''
    for food in fooditems.sorted(key=lambda x: x.id):
        to_hash += str(f'{food.name} - {food.quantity} - {food.expiration_date}')
    return sha256(to_hash.encode()).hexdigest()
