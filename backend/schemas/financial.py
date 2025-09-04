from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class FinancialBase(BaseModel):
    company_id: str
    year: int
    revenue: Optional[Decimal] = None
    profit: Optional[Decimal] = None
    assets: Optional[Decimal] = None
    liabilities: Optional[Decimal] = None
    equity: Optional[Decimal] = None

class FinancialCreate(FinancialBase):
    pass

class FinancialUpdate(BaseModel):
    revenue: Optional[Decimal] = None
    profit: Optional[Decimal] = None
    assets: Optional[Decimal] = None
    liabilities: Optional[Decimal] = None
    equity: Optional[Decimal] = None

class Financial(FinancialBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True