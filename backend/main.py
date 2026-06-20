# FastAPI application entry point — creates the app instance and registers routers

from dotenv import load_dotenv

load_dotenv()

import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.database import Base, engine
from backend.routers import accounts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaaS Onboarding Health Dashboard", version="0.1.0")

app.include_router(accounts.router, prefix="/api/v1", tags=["accounts"])

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/", response_class=HTMLResponse)
def root():
    with open(os.path.join(FRONTEND_DIR, "index.html")) as f:
        return f.read()


app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
