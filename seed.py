from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

print("🛠️  Tesztadatok generálása SQLAlchemy segítségével...\n")

ACCOUNT_DB_URL = "sqlite:///./account_service/account.db"
CARD_DB_URL = "sqlite:///./card_service/card.db"

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    account_number = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)

class Card(Base):
    __tablename__ = "cards"
    card_number = Column(String, primary_key=True)
    account_number = Column(String, nullable=False)


def seed_data():
    engine_acc = create_engine(ACCOUNT_DB_URL)
    Base.metadata.create_all(bind=engine_acc)
    SessionAcc = sessionmaker(bind=engine_acc)
    session_acc = SessionAcc()

    acc1_num = "1111222233334444"
    acc2_num = "5555666677778888"

    if not session_acc.query(Account).filter_by(account_number=acc1_num).first():
        session_acc.add(Account(account_number=acc1_num, balance=50000))
    if not session_acc.query(Account).filter_by(account_number=acc2_num).first():
        session_acc.add(Account(account_number=acc2_num, balance=15000))
    
    session_acc.commit()
    session_acc.close()
    print("Bankszámlák feltöltve (account_service/account.db)")


    engine_card = create_engine(CARD_DB_URL)
    Base.metadata.create_all(bind=engine_card)
    SessionCard = sessionmaker(bind=engine_card)
    session_card = SessionCard()

    card1_num = "1234-5678-9012-3456"
    card2_num = "9876-5432-1098-7654"

    if not session_card.query(Card).filter_by(card_number=card1_num).first():
        session_card.add(Card(card_number=card1_num, account_number=acc1_num))
    if not session_card.query(Card).filter_by(card_number=card2_num).first():
        session_card.add(Card(card_number=card2_num, account_number=acc2_num))

    session_card.commit()
    session_card.close()
    print("Bankkártyák feltöltve (card_service/card.db)")
    print("\nKész! A rendszer SQLAlchemy-vel lett seedelve.")

if __name__ == "__main__":
    seed_data()