from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import database, models, schemas
from sqlalchemy.orm import Session
import requests

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
ACCOUNT_SERVICE_URL = "http://account_service:8000"

@app.post("/charge", response_model=schemas.TransactionResponse)
def charge_card(request: schemas.ChargeRequest, db: Session = Depends(database.get_db)):
    
    card = db.query(models.Card).filter(models.Card.card_number == request.card_number).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="A megadott bankkártya nem található.")

    target_url = f"{ACCOUNT_SERVICE_URL}/accounts/{card.account_number}/withdraw"
    
    payload = {"amount": request.amount}

    try:
        response = requests.post(target_url, json=payload)
        if response.status_code != 200:
            error_detail = response.json().get("detail", "Ismeretlen hiba a terhelés során.")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
            
        return {"success": True, "message": f"Sikeres kártyás terhelés. Cél számla: {card.account_number}"}
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="A Bankszámla szolgáltatás jelenleg nem elérhető.")

@app.get("/cards")
def list_all_cards(db: Session = Depends(database.get_db)):
    return db.query(models.Card).all()