from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    organization_number: str
    name: str
    business_description: Optional[str] = None
    industry_code: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    business_description: Optional[str] = None
    industry_code: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None

class Company(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True