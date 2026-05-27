from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import database, models, schemas


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Fizetés Szolgáltatás")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CARD_SERVICE_URL = "http://card_service:8000"
ACCOUNT_SERVICE_URL = "http://account_service:8000"

@app.post("/pay", response_model=schemas.PaymentResponse)
def process_payment(request: schemas.PaymentRequest, db: Session = Depends(database.get_db)):
    
    new_transaction = models.PaymentTransaction(
        source_card=request.source_card,
        target_account=request.target_account,
        amount=request.amount,
        status="PENDING"
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    charge_payload = {"card_number": request.source_card, "amount": request.amount}

    try:
        charge_resp = requests.post(f"{CARD_SERVICE_URL}/charge", json=charge_payload)
    except requests.exceptions.ConnectionError:
        new_transaction.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=503, detail="A kártya szolgáltatás nem elérhető, a tranzakció sikertelen.")

    if charge_resp.status_code != 200:
        new_transaction.status = "FAILED"
        db.commit()

        error_detail = charge_resp.json().get("detail", "Kártya terhelése sikertelen.")
        raise HTTPException(status_code=400, detail=error_detail)

    deposit_payload = {"amount": request.amount}
    refund_payload = {"card_number": request.source_card, "amount": request.amount}

    def attempt_refund():
        try:
            return requests.post(f"{CARD_SERVICE_URL}/refund", json=refund_payload)
        except requests.exceptions.ConnectionError:
            return None

    try:
        deposit_resp = requests.post(f"{ACCOUNT_SERVICE_URL}/accounts/{request.target_account}/deposit", json=deposit_payload)
    except requests.exceptions.ConnectionError:
        refund_resp = attempt_refund()
        new_transaction.status = "FAILED_COMPENSATION_REQUESTED"
        db.commit()

        if refund_resp is None:
            raise HTTPException(
                status_code=503,
                detail="A cél számla nem elérhető, és a kompenzációs visszatérítés nem hajtható végre. Ellenőrizd a tranzakciót."
            )

        raise HTTPException(
            status_code=500,
            detail="A cél számla nem elérhető. A terhelést visszavontuk (kompenzáció)."
        )

    if deposit_resp.status_code != 200:
        refund_resp = attempt_refund()
        new_transaction.status = "FAILED_COMPENSATION_REQUESTED"
        db.commit()

        if refund_resp is None or refund_resp.status_code != 200:
            detail = "A cél számla nem elérhető, és a kompenzációs visszatérítés nem sikerült. Ellenőrizd a tranzakciót."
            raise HTTPException(status_code=500, detail=detail)

        raise HTTPException(
            status_code=500,
            detail="A cél számla nem elérhető. A terhelést visszavontuk (kompenzáció)."
        )

    new_transaction.status = "SUCCESS"
    db.commit()
    
    return {
        "transaction_id": new_transaction.id,
        "status": "SUCCESS",
        "message": "Sikeres bankkártyás fizetés!"
    }

@app.get("/payments")
def list_all_payments(db: Session = Depends(database.get_db)):
    return db.query(models.PaymentTransaction).all()
