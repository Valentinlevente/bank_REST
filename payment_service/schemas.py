from pydantic import BaseModel, Field

class PaymentRequest(BaseModel):
    source_card: str
    target_account: str
    amount: int = Field(gt=0)

class PaymentResponse(BaseModel):
    transaction_id: int
    status: str
    message: str