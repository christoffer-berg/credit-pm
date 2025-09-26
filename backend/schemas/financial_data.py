from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import date, datetime
from decimal import Decimal

class FinancialStatement(BaseModel):
    year: int
    period_start: date
    period_end: date
    revenue: Optional[Decimal] = None
    cost_of_goods_sold: Optional[Decimal] = None
    gross_profit: Optional[Decimal] = None
    operating_expenses: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    depreciation: Optional[Decimal] = None
    ebit: Optional[Decimal] = None
    financial_income: Optional[Decimal] = None
    financial_expenses: Optional[Decimal] = None
    profit_before_tax: Optional[Decimal] = None
    tax_expense: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    
    # Balance sheet items
    current_assets: Optional[Decimal] = None
    fixed_assets: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    current_liabilities: Optional[Decimal] = None
    long_term_liabilities: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    equity: Optional[Decimal] = None
    
    # Cash flow items
    operating_cash_flow: Optional[Decimal] = None
    investing_cash_flow: Optional[Decimal] = None
    financing_cash_flow: Optional[Decimal] = None
    net_cash_flow: Optional[Decimal] = None
    cash_beginning: Optional[Decimal] = None
    cash_ending: Optional[Decimal] = None
    
    # Additional metrics
    employees: Optional[int] = None
    currency: str = "SEK"
    is_consolidated: bool = False
    source: str = "manual"  # manual, allabolag, pdf_upload
    
    class Config:
        json_encoders = {
            Decimal: float,
            date: lambda v: v.isoformat()
        }

class FinancialDataCreate(BaseModel):
    company_id: str
    financial_statements: List[FinancialStatement]
    source_document: Optional[str] = None  # PDF filename or URL
    
class FinancialDataUpdate(BaseModel):
    financial_statements: List[FinancialStatement]

class FinancialProjection(BaseModel):
    year: int
    revenue_growth: Optional[Decimal] = None
    # Allow mixed types coming from calculations/DB JSON
    margin_assumptions: Dict[str, Any] = {}
    projected_revenue: Optional[Decimal] = None
    projected_ebitda: Optional[Decimal] = None
    projected_net_profit: Optional[Decimal] = None
    assumptions: List[str] = []
    confidence_level: str = "medium"  # low, medium, high
    
class FinancialAnalysis(BaseModel):
    company_id: str
    historical_data: List[FinancialStatement]
    projections: List[FinancialProjection]
    key_metrics: Dict[str, Any] = {}
    analysis_text: Optional[str] = None
    generated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: float
        }

class AllabolagCompanyData(BaseModel):
    org_number: str
    company_name: str
    industry: Optional[str] = None
    employees: Optional[int] = None
    turnover: Optional[Decimal] = None
    profit: Optional[Decimal] = None
    equity: Optional[Decimal] = None
    last_financial_year: Optional[int] = None
    status: str = "active"
    
class PDFUploadResponse(BaseModel):
    filename: str
    file_size: int
    upload_path: str
    extracted_data: Optional[Dict[str, Any]] = None
    parsing_status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None
