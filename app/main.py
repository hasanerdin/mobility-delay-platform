from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.routes import router as delays_router

app = FastAPI(
    title="Mobility Delay Platform",
    description="Analytics API for Deutsche Bahn delay data",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(delays_router)