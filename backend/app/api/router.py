from fastapi import APIRouter

from .routes import auth, coach, edges, gamification, graph, habits, plan, review, tasks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(habits.router, prefix="/habit", tags=["habits"])
api_router.include_router(tasks.router, prefix="/task", tags=["tasks"])
api_router.include_router(edges.router, prefix="/edges", tags=["edges"])
api_router.include_router(plan.router, prefix="/plan", tags=["plan"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(coach.router, prefix="/coach", tags=["coach"])
