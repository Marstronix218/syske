from datetime import date, datetime, time, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .api.router import api_router
from .config import settings
from .database import Base, engine, get_db
from .models import DayPlan, PlanStatus, User
from .services import review, scheduler as scheduler_service

app = FastAPI(title=settings.app_name)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_daily_jobs():
    with engine.begin() as connection:
        Base.metadata.create_all(bind=connection)


def _schedule_daily_review(background: BackgroundScheduler):
    def job():
        from .database import session_scope

        with session_scope() as db:
            users = db.query(User).all()
            today = date.today()
            for user in users:
                try:
                    review.generate_daily_summary(db, user.id, today)
                except ValueError:
                    continue

    background.add_job(job, "cron", hour=21, minute=0)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    _run_daily_jobs()
    if settings.enable_scheduler:
        background = BackgroundScheduler(timezone=settings.timezone)
        _schedule_daily_review(background)
        background.start()
        app.state.scheduler = background


@app.on_event("shutdown")
def on_shutdown():
    background = getattr(app.state, "scheduler", None)
    if background:
        background.shutdown(wait=False)


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/plan/demo")
def demo_plan(user_id: int = Query(...), db: Session = Depends(get_db)) -> dict:
    today = date.today()
    plan = scheduler_service.generate_day_plan(db, user_id=user_id, target_date=today)
    return {"plan_id": plan.id, "items": len(plan.items)}
