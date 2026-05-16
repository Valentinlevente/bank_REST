from sqlalchemy import Column, String, Integer, CheckConstraint
from database import Base

class Account(Base):
    __tablename__ = "accounts"


    account_number = Column(String, primary_key=True, index=True)
    balance = Column(Integer, default=0, nullable=False)


    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_positive'),
    )