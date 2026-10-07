import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.tools import router as tools_router

logging.basicConfig(level=logging.WARNING)
logging.getLogger("app").setLevel(logging.INFO)

app = FastAPI(title="Mini Agent Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in get_settings().cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(tools_router)
