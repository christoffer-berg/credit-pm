from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

from api.routes import companies, cases, sections, migrate, market_analysis
# Temporarily disabled routes that require additional dependencies
# from api.routes import financials, export, audit
from core.config import settings
from core.database import get_database
from services.auth import verify_token

load_dotenv()

app = FastAPI(
    title="Credit PM Generator API",
    description="Backend service for automated credit memo generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "Credit PM Generator API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["cases"])  
app.include_router(sections.router, prefix="/api/v1/sections", tags=["sections"])
app.include_router(migrate.router, prefix="/api/v1/migrate", tags=["migrate"])
app.include_router(market_analysis.router, prefix="/api/v1", tags=["market-analysis"])
# Temporarily disabled
# app.include_router(financials.router, prefix="/api/v1/financials", tags=["financials"])
# app.include_router(export.router, prefix="/api/v1/export", tags=["export"])
# app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)