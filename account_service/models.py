import datetime
from sqlalchemy import Column, DateTime, String, Integer, CheckConstraint
from database import Base

class Account(Base):
    __tablename__ = "accounts"


    account_number = Column(String, primary_key=True, index=True)
    balance = Column(Integer, default=0, nullable=False)


    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_positive'),
    )

class AccountTransaction(Base):
    __tablename__ = "account_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)