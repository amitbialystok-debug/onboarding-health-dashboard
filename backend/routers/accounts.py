# API router for account-related endpoints under /api/v1/accounts

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Account
from backend.schemas import AccountCreate, AccountRead

router = APIRouter()


@router.post("/accounts", response_model=AccountRead, status_code=201)
def create_account(body: AccountCreate, db: Session = Depends(get_db)):
    account = Account(**body.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/accounts", response_model=list[AccountRead])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.get("/accounts/{account_id}", response_model=AccountRead)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
