import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean
from database import Base

class Card(Base):
    __tablename__ = "cards"

    card_number = Column(String, primary_key=True, index=True)
    account_number = Column(String, index=True, nullable=False)

class CardTransaction(Base):
    __tablename__ = "card_transactions"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)