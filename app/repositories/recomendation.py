from sqlalchemy.orm import Session
from app.models import Recommendation

class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, ai_data: dict) -> Recommendation:
        rec = Recommendation(data=ai_data)
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def get_latest(self) -> Recommendation | None:
        return self.db.query(Recommendation).order_by(Recommendation.created_at.desc()).first()