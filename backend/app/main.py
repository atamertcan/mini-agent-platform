from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI(title="Mini Agent Platform")

app.include_router(auth_router)
