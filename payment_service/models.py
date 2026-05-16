from sqlalchemy import Column, String, Integer, DateTime
from database import Base
import datetime

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    source_card = Column(String, nullable=False)
    target_account = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="PENDING") 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)