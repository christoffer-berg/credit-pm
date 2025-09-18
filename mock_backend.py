#!/usr/bin/env python3
"""
Minimal mock backend for testing Credit PM frontend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="Mock Credit PM API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_CASES = [
    {
        "id": "6a40f269-7724-4ec3-b6b0-73ac7d5bcab0",
        "company_name": "Test Company A",
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "company_id": "comp-123",
        "org_number": "556677-8899"
    },
    {
        "id": "ca86f224-2743-4224-8b3d-994bd3833724", 
        "company_name": "Test Company B",
        "status": "draft",
        "created_at": "2024-01-16T14:20:00Z",
        "updated_at": "2024-01-16T14:20:00Z",
        "company_id": "comp-124",
        "org_number": "556677-9988"
    }
]

MOCK_SECTIONS = {
    "6a40f269-7724-4ec3-b6b0-73ac7d5bcab0": [
        {
            "id": "section-1",
            "case_id": "6a40f269-7724-4ec3-b6b0-73ac7d5bcab0",
            "title": "Executive Summary",
            "content": "This is a mock executive summary for testing purposes.",
            "section_type": "executive_summary",
            "order_index": 0
        },
        {
            "id": "section-2", 
            "case_id": "6a40f269-7724-4ec3-b6b0-73ac7d5bcab0",
            "title": "Company Overview",
            "content": "Mock company overview content for testing the PDF uploader functionality.",
            "section_type": "company_overview", 
            "order_index": 1
        }
    ],
    "ca86f224-2743-4224-8b3d-994bd3833724": [
        {
            "id": "section-3",
            "case_id": "ca86f224-2743-4224-8b3d-994bd3833724", 
            "title": "Financial Analysis",
            "content": "Mock financial analysis content.",
            "section_type": "financial_analysis",
            "order_index": 0
        }
    ]
}

@app.get("/")
async def root():
    return {"message": "Mock Credit PM API is running"}

@app.get("/api/v1/cases")
async def get_cases():
    return {"cases": MOCK_CASES}

@app.get("/api/v1/cases/{case_id}")
async def get_case(case_id: str):
    case = next((c for c in MOCK_CASES if c["id"] == case_id), None)
    if not case:
        return {"error": "Case not found"}, 404
    return case

@app.get("/api/v1/sections/{case_id}")
async def get_sections(case_id: str):
    sections = MOCK_SECTIONS.get(case_id, [])
    return {"sections": sections}

@app.post("/api/v1/financials/{company_id}/upload")
async def upload_financial_data(company_id: str):
    return {
        "message": "Mock file upload successful",
        "company_id": company_id,
        "status": "processed"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)