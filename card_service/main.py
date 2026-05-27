from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database, models, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Bankkártya Szolgáltatás")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/cards")
def list_all_cards(db: Session = Depends(database.get_db)):
    return db.query(models.Card).all()

@app.get("/cards/logs")
def list_card_logs(db: Session = Depends(database.get_db)):
    return db.query(models.CardTransaction).all()

@app.post("/charge", response_model=schemas.TransactionResponse)
def charge_card(request: schemas.ChargeRequest, db: Session = Depends(database.get_db)):
    
    card = db.query(models.Card).filter(models.Card.card_number == request.card_number).first()
    
    if not card:
        log = models.CardTransaction(card_number=request.card_number, amount=request.amount, status="FAILED")
        db.add(log)
        db.commit()
        raise HTTPException(status_code=404, detail="A megadott bankkártya nem található.")

    log = models.CardTransaction(card_number=request.card_number, amount=request.amount, status="SUCCESS")
    db.add(log)
    db.commit()

    return {
        "success": True,
        "message": f"A kártya érvényes, és a kapcsolt számla: {card.account_number}.",
        "account_number": card.account_number,
    }


@app.post("/refund", response_model=schemas.TransactionResponse)
def refund_card(request: schemas.RefundRequest, db: Session = Depends(database.get_db)):
    
    card = db.query(models.Card).filter(models.Card.card_number == request.card_number).first()
    
    if not card:
        log = models.CardTransaction(card_number=request.card_number, amount=request.amount, status="FAILED")
        db.add(log)
        db.commit()
        raise HTTPException(status_code=404, detail="A megadott bankkártya nem található.")

    log = models.CardTransaction(card_number=request.card_number, amount=request.amount, status="SUCCESS")
    db.add(log)
    db.commit()

    return {
        "success": True,
        "message": f"A kártya visszatérítéshez kapcsolódó számla: {card.account_number}.",
        "account_number": card.account_number,
    }
