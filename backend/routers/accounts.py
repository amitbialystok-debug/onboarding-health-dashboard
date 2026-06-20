# API router for account-related endpoints under /api/v1/accounts

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db

router = APIRouter()


@router.get("/accounts")
def list_accounts(db: Session = Depends(get_db)):
    return []
