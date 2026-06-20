# Pydantic schemas for request validation and response serialization

# AccountCreate and AccountRead are kept separate so that server-generated fields
# (id, created_at) are never accepted as user input, only returned in responses.

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AccountBase(BaseModel):
    company_name: str
    industry: str | None = None
    contract_start_date: date
    seats_purchased: int
    seats_active: int
    logins_last_30_days: int
    support_tickets_open: int
    nps_score: int | None = None


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class HealthScoreResult(BaseModel):
    score: int
    risk_level: str
    signals: list[str]


class AccountReadWithScore(AccountRead):
    health: HealthScoreResult
    recommendation: str | None = None
