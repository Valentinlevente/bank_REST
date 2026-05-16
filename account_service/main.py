from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database, models, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Bankszámla Szolgáltatás")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_account_or_404(db: Session, account_number: str):
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="A megadott bankszámla nem található.")
    return account

@app.get("/accounts/{account_number}", response_model=schemas.AccountResponse)
def get_balance(account_number: str, db: Session = Depends(database.get_db)):
    account = get_account_or_404(db, account_number)
    return account

@app.post("/accounts/{account_number}/deposit", response_model=schemas.TransactionResponse)
def deposit(account_number: str, request: schemas.AmountRequest, db: Session = Depends(database.get_db)):
    account = get_account_or_404(db, account_number)
    
    account.balance += request.amount
    db.commit()
    
    return {"success": True, "message": "Sikeres jóváírás.", "current_balance": account.balance}

@app.post("/accounts/{account_number}/withdraw", response_model=schemas.TransactionResponse)
def withdraw(account_number: str, request: schemas.AmountRequest, db: Session = Depends(database.get_db)):
    account = get_account_or_404(db, account_number)
    
    if account.balance < request.amount:
        raise HTTPException(status_code=400, detail="Nincs elegendő fedezet a számlán.")
        
    account.balance -= request.amount
    db.commit()
    
    return {"success": True, "message": "Sikeres terhelés.", "current_balance": account.balance}

@app.post("/accounts/{account_number}/transfer", response_model=schemas.TransactionResponse)
def transfer(account_number: str, request: schemas.TransferRequest, db: Session = Depends(database.get_db)):
    source_account = get_account_or_404(db, account_number)
    target_account = get_account_or_404(db, request.target_account)
    
    if source_account.balance < request.amount:
        raise HTTPException(status_code=400, detail="Nincs elegendő fedezet az utaláshoz.")
        
    try:
        source_account.balance -= request.amount
        target_account.balance += request.amount
        
        db.commit()
        return {"success": True, "message": "Sikeres átutalás.", "current_balance": source_account.balance}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Belső szerverhiba történt az átutalás során.")
    
@app.get("/accounts")
def list_all_accounts(db: Session = Depends(database.get_db)):
    return db.query(models.Account).all()