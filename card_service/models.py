from sqlalchemy import Column, String, Boolean
from database import Base

class Card(Base):
    __tablename__ = "cards"

    card_number = Column(String, primary_key=True, index=True)
    account_number = Column(String, index=True, nullable=False)