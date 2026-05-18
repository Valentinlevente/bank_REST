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

@app.get("/accounts", response_model=list[schemas.AccountResponse])
def list_all_accounts(db: Session = Depends(database.get_db)):
    return db.query(models.Account).all()

@app.get("/accounts/logs")
def list_account_logs(db: Session = Depends(database.get_db)):
    return db.query(models.AccountTransaction).all()

@app.get("/accounts/{account_number}", response_model=schemas.AccountResponse)
def get_balance(account_number: str, db: Session = Depends(database.get_db)):
    account = get_account_or_404(db, account_number)
    return account

@app.post("/accounts/{account_number}/deposit", response_model=schemas.TransactionResponse)
def deposit(account_number: str, request: schemas.AmountRequest, db: Session = Depends(database.get_db)):
    account = get_account_or_404(db, account_number)
    
    account.balance += request.amount
    
    log = models.AccountTransaction(account_number=account_number, type="DEPOSIT", amount=request.amount, status="SUCCESS")
    db.add(log)
    
    db.commit()
    return {"success": True, "message": "Sikeres jóváírás.", "current_balance": account.balance}

@app.post("/accounts/{account_number}/withdraw", response_model=schemas.TransactionResponse)
def withdraw(account_number: str, request: schemas.AmountRequest, db: Session = Depends(database.get_db)):
    account = get_account_or_404(db, account_number)
    
    if account.balance < request.amount:
        log = models.AccountTransaction(account_number=account_number, type="WITHDRAW", amount=request.amount, status="FAILED")
        db.add(log)
        db.commit()
        raise HTTPException(status_code=400, detail="Nincs elegendő fedezet a számlán.")
        
    account.balance -= request.amount
    
    log = models.AccountTransaction(account_number=account_number, type="WITHDRAW", amount=request.amount, status="SUCCESS")
    db.add(log)
    
    db.commit()
    return {"success": True, "message": "Sikeres terhelés.", "current_balance": account.balance}

@app.post("/accounts/{account_number}/transfer", response_model=schemas.TransactionResponse)
def transfer(account_number: str, request: schemas.TransferRequest, db: Session = Depends(database.get_db)):
    source_account = get_account_or_404(db, account_number)
    target_account = get_account_or_404(db, request.target_account)
    
    if source_account.balance < request.amount:
        log = models.AccountTransaction(account_number=account_number, type="TRANSFER_SRC", amount=request.amount, status="FAILED")
        db.add(log)
        db.commit()
        raise HTTPException(status_code=400, detail="Nincs elegendő fedezet az utaláshoz.")
        
    try:
        source_account.balance -= request.amount
        target_account.balance += request.amount

        log_src = models.AccountTransaction(account_number=account_number, type="TRANSFER_SRC", amount=request.amount, status="SUCCESS")
        log_trg = models.AccountTransaction(account_number=request.target_account, type="TRANSFER_TRG", amount=request.amount, status="SUCCESS")
        db.add(log_src)
        db.add(log_trg)
        
        db.commit()
        return {"success": True, "message": "Sikeres átutalás.", "current_balance": source_account.balance}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Belső szerverhiba történt az átutalás során.")