import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import schemas, ai_client
from app.database import engine, get_db, Base, SessionLocal
from app.repositories.food import FoodRepository
from app.repositories.recomendation import RecommendationRepository

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Food Manager AI", lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")


# FastAPI Dependency: Injects repository instead of raw DB session
def get_food_repo(db: Session = Depends(get_db)) -> FoodRepository:
    return FoodRepository(db)


def get_rec_repo(db: Session = Depends(get_db)) -> RecommendationRepository:
    return RecommendationRepository(db)


async def generate_and_save_recommendations():
    db = SessionLocal()
    try:
        repo = FoodRepository(db)
        rec_repo = RecommendationRepository(db)

        foods = repo.get_all()
        if not foods:
            logger.info("Inventory empty. Skipping AI recommendation.")
            return

        inventory = [
            {"name": f.name, "quantity": f.quantity, "expires": f.expiration_date.isoformat()}
            for f in foods
        ]
        snapshot_hash = inventory_snapshot(foods)
        existing_snapshot = rec_repo.get_by_inventory_snapshot(snapshot_hash)
        if existing_snapshot:
            logger.info("Recomendation exists in database")
            return


        logger.info("Running AI recommendation in background...")
        rec_data = await ai_client.get_daily_recommendations(inventory)  # ← Returns clean dict now
        rec_data['inventory_snapshot'] = snapshot_hash
        rec_repo.save(rec_data)  # ← Save the dict directly to JSONB column
        logger.info("Recommendation saved to database")
    except Exception as e:
        logger.error(f"Background AI task failed: {e}")
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/api/foods", response_model=schemas.FoodResponse)
async def add_food(
        background_tasks: BackgroundTasks,
        food: schemas.FoodCreate,
        repo: FoodRepository = Depends(get_food_repo),
):
    background_tasks.add_task(generate_and_save_recommendations)
    return repo.create(food)


@app.get("/api/foods", response_model=list[schemas.FoodResponse])
async def list_foods(
        background_tasks: BackgroundTasks,
        repo: FoodRepository = Depends(get_food_repo),
):
    return repo.get_all()


@app.delete("/api/foods/{food_id}")
async def remove_food(
        background_tasks: BackgroundTasks,
        food_id: int,
        repo: FoodRepository = Depends(get_food_repo),
):
    deleted = repo.delete_by_id(food_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Food not found")
    background_tasks.add_task(generate_and_save_recommendations)
    return {"message": "Food removed successfully"}


@app.post("/api/recommendations/generate")
async def trigger_recommendation(background_tasks: BackgroundTasks):
    """Manually trigger AI recommendation"""
    background_tasks.add_task(generate_and_save_recommendations)
    return {"message": "Recommendation job started. Check back in a few seconds."}


@app.get("/api/recommendations/latest", response_model=schemas.RecommendationResponse)
async def get_latest_recommendation(rec_repo: RecommendationRepository = Depends(get_rec_repo)):
    latest = rec_repo.get_latest()
    if not latest:
        raise HTTPException(status_code=404, detail="No recommendations saved yet")
    return latest
