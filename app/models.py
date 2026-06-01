from sqlalchemy import Column, Integer, String, Date, DateTime, JSON
from datetime import datetime
from .database import Base



class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    expiration_date = Column(Date, nullable=False)
    added_at = Column(DateTime, default=datetime.now)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    inventory_snapshot = Column(String, nullable=True)  # hash for dedup