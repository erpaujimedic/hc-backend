# File: app/schemas/transaction.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    patient_id: str = Field(..., description="ID pasien yang melakukan transaksi")
    amount: float = Field(..., description="Total biaya transaksi")
    description: Optional[str] = Field(None, description="Keterangan transaksi")

class TransactionCreate(TransactionBase):
    """Skema untuk menerima data pembuatan transaksi baru dari Frontend"""
    pass

class TransactionResponse(TransactionBase):
    """Skema untuk mengembalikan data transaksi ke Frontend"""
    id: str
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True