# SQLAlchemy ORM models (database table definitions)

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    industry: Mapped[str | None] = mapped_column(String, nullable=True)
    contract_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    seats_purchased: Mapped[int] = mapped_column(Integer, nullable=False)
    seats_active: Mapped[int] = mapped_column(Integer, nullable=False)
    logins_last_30_days: Mapped[int] = mapped_column(Integer, nullable=False)
    support_tickets_open: Mapped[int] = mapped_column(Integer, nullable=False)
    nps_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<Account id={self.id} company_name={self.company_name!r} "
            f"seats={self.seats_active}/{self.seats_purchased}>"
        )
