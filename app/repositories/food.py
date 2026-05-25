from sqlalchemy.orm import Session
from app.models import FoodItem
from app.schemas import FoodCreate

class FoodRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, food_data: FoodCreate) -> FoodItem:
        db_food = FoodItem(**food_data.model_dump())
        self.db.add(db_food)
        self.db.commit()
        self.db.refresh(db_food)
        return db_food

    def get_all(self, skip: int = 0, limit: int = 100) -> list[FoodItem]:
        return (
            self.db.query(FoodItem)
            .order_by(FoodItem.expiration_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_by_id(self, food_id: int) -> FoodItem | None:
        food = self.db.query(FoodItem).filter(FoodItem.id == food_id).first()
        if food:
            self.db.delete(food)
            self.db.commit()
        return food