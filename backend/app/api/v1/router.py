from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(tasks_router)
