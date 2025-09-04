import httpx
from typing import Dict, Optional
from core.config import settings

async def fetch_company_data(organization_number: str) -> Dict:
    """
    Fetch company data from Bolagsverket API.
    For MVP, returns mock data. Replace with actual API integration.
    """
    
    # Mock data for MVP - replace with actual API call
    mock_data = {
        "556016-0680": {
            "name": "ICA Gruppen AB",
            "business_description": "Retail and wholesale trade of food and consumer goods",
            "industry_code": "47.11"
        },
        "556036-0793": {
            "name": "Volvo AB",
            "business_description": "Manufacturing of trucks, buses and construction equipment",
            "industry_code": "29.10"
        },
        "default": {
            "name": f"Company {organization_number}",
            "business_description": "General business operations",
            "industry_code": "00.00"
        }
    }
    
    # Return mock data for now
    return mock_data.get(organization_number, mock_data["default"])
    
    # Uncomment below for actual API integration:
    """
    if not settings.bolagsverket_api_key:
        raise ValueError("Bolagsverket API key not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.bolagsverket.se/info/v1/companies/{organization_number}",
                headers={
                    "Authorization": f"Bearer {settings.bolagsverket_api_key}",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("namn", "Unknown Company"),
                    "business_description": data.get("verksamhetsbeskrivning", ""),
                    "industry_code": data.get("branschkod", "")
                }
            elif response.status_code == 404:
                raise ValueError(f"Company with organization number {organization_number} not found")
            else:
                raise ValueError(f"Failed to fetch company data: {response.status_code}")
                
        except httpx.RequestError as e:
            raise ValueError(f"Network error when fetching company data: {str(e)}")
    """

async def validate_organization_number(org_number: str) -> bool:
    """
    Validate Swedish organization number format.
    """
    if not org_number or len(org_number) != 10:
        return False
    
    if not org_number.isdigit():
        return False
    
    # Luhn algorithm validation for Swedish organization numbers
    def luhn_check(number_str: str) -> bool:
        digits = [int(d) for d in number_str]
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0
    
    return luhn_check(org_number)