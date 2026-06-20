# API router for account-related endpoints under /api/v1/accounts

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Account
from backend.schemas import AccountCreate, AccountRead, AccountReadWithScore
from backend.services.health_score import compute_health_score

router = APIRouter()


@router.post("/accounts", response_model=AccountRead, status_code=201)
def create_account(body: AccountCreate, db: Session = Depends(get_db)):
    account = Account(**body.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/accounts", response_model=list[AccountReadWithScore])
def list_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return [
        AccountReadWithScore(**AccountRead.model_validate(a).model_dump(), health=compute_health_score(a))
        for a in accounts
    ]


@router.get("/accounts/{account_id}", response_model=AccountReadWithScore)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountReadWithScore(
        **AccountRead.model_validate(account).model_dump(),
        health=compute_health_score(account),
    )
