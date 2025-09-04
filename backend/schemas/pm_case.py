from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class PMCaseStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPORTED = "exported"

class PMCaseBase(BaseModel):
    company_id: str
    title: str
    status: PMCaseStatus = PMCaseStatus.DRAFT

class PMCaseCreate(BaseModel):
    organization_number: str
    title: Optional[str] = None

class PMCaseUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[PMCaseStatus] = None

class PMCase(PMCaseBase):
    id: str
    version: int
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True