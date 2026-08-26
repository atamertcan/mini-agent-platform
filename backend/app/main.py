from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router

app = FastAPI(title="Mini Agent Platform")

app.include_router(auth_router)
app.include_router(agents_router)
