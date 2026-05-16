from pydantic import BaseModel, ConfigDict, Field

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    account_number: str
    balance: int

class AmountRequest(BaseModel):
    amount: int = Field(gt=0, description="A tranzakció összege (csak pozitív)")

class TransferRequest(BaseModel):
    target_account: str
    amount: int = Field(gt=0)

class TransactionResponse(BaseModel):
    success: bool
    message: str
    current_balance: int | None = None 