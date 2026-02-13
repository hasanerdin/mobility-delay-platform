from fastapi import FastAPI

from app.api.health import router as health_router


app = FastAPI(title="Mobility Delay Platform")

app.include_router(health_router)