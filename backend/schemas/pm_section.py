from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class SectionType(str, Enum):
    PURPOSE = "purpose"
    BUSINESS_DESCRIPTION = "business_description"
    MARKET_ANALYSIS = "market_analysis"
    FINANCIAL_ANALYSIS = "financial_analysis"
    CREDIT_ANALYSIS = "credit_analysis"
    CREDIT_PROPOSAL = "credit_proposal"

class PMSectionBase(BaseModel):
    case_id: str
    section_type: SectionType
    title: str

class PMSectionCreate(PMSectionBase):
    ai_content: Optional[str] = None
    user_content: Optional[str] = None

class PMSectionUpdate(BaseModel):
    user_content: str

class PMSection(PMSectionBase):
    id: str
    ai_content: Optional[str] = None
    user_content: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True