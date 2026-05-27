from pydantic import BaseModel, Field

class ChargeRequest(BaseModel):
    card_number: str
    amount: int = Field(gt=0, description="A terhelés összege (csak pozitív)")

class RefundRequest(BaseModel):
    card_number: str
    amount: int = Field(gt=0, description="A visszatérítés összege (csak pozitív)")

class TransactionResponse(BaseModel):
    success: bool
    message: str
    account_number: str | None = None
