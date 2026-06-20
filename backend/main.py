# FastAPI application entry point — creates the app instance and registers routers

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from backend.database import Base, engine
from backend.routers import accounts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaaS Onboarding Health Dashboard", version="0.1.0")

app.include_router(accounts.router, prefix="/api/v1", tags=["accounts"])


@app.get("/")
def root():
    return {"status": "ok", "message": "Dashboard API is running"}
