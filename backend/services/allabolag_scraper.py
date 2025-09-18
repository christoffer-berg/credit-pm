import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, List, Any
from decimal import Decimal
from datetime import datetime, date
import logging
from urllib.parse import urljoin
from schemas.financial_data import AllabolagCompanyData, FinancialStatement

logger = logging.getLogger(__name__)

class AllabolagScraper:
    def __init__(self):
        self.base_url = "https://www.allabolag.se"
        self.session = None
        
    async def __aenter__(self):
        # Create session with headers to mimic a browser
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _parse_financial_value(self, value_str: str) -> Optional[Decimal]:
        """Parse financial values from Swedish format (e.g., '1 234 567 kr' or '1,5 Mkr')"""
        if not value_str or value_str.strip() in ['-', '0', '']:
            return None
        
        # Remove currency symbols and spaces
        clean_value = re.sub(r'[kr\s]', '', value_str.lower())
        
        # Handle millions (Mkr, mkr)
        if 'mkr' in value_str.lower() or 'miljoner' in value_str.lower():
            multiplier = 1000000
        # Handle thousands (tkr, Tkr)
        elif 'tkr' in value_str.lower() or 'tusen' in value_str.lower():
            multiplier = 1000
        else:
            multiplier = 1
            
        # Replace comma with dot for decimal parsing
        clean_value = clean_value.replace(',', '.')
        
        # Extract numeric value
        match = re.search(r'[-+]?\d*\.?\d+', clean_value)
        if match:
            try:
                return Decimal(str(float(match.group()) * multiplier))
            except (ValueError, TypeError):
                return None
        
        return None

    async def search_company(self, org_number: str = None, company_name: str = None) -> Optional[str]:
        """Search for a company and return the bokslut URL"""
        if not org_number and not company_name:
            raise ValueError("Either org_number or company_name must be provided")
        
        try:
            # Try direct URL first if org_number is provided
            if org_number:
                clean_org_number = re.sub(r'[-\s]', '', org_number)
                direct_url = f"{self.base_url}/{clean_org_number}"
                
                async with self.session.get(direct_url) as response:
                    if response.status == 200:
                        # Check if this is a valid company page
                        content = await response.text()
                        if "bokslut" in content.lower():
                            return f"{direct_url}/bokslut"
            
            # Fall back to search
            search_query = org_number if org_number else company_name
            search_url = f"{self.base_url}/sok/{search_query}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for company links in search results
                    company_links = soup.find_all('a', href=re.compile(r'/\d+$'))
                    if company_links:
                        first_company = company_links[0]['href']
                        return urljoin(self.base_url, first_company + "/bokslut")
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for company: {e}")
            return None

    async def fetch_company_data(self, org_number: str = None, company_name: str = None) -> Optional[AllabolagCompanyData]:
        """Fetch basic company information"""
        try:
            bokslut_url = await self.search_company(org_number, company_name)
            if not bokslut_url:
                return None
                
            # Get company overview page
            company_url = bokslut_url.replace("/bokslut", "")
            
            async with self.session.get(company_url) as response:
                if response.status != 200:
                    return None
                    
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract company information
                company_data = AllabolagCompanyData(
                    org_number=org_number or "unknown",
                    company_name=company_name or "unknown"
                )
                
                # Try to extract company name if not provided
                if not company_name:
                    title_elem = soup.find('h1')
                    if title_elem:
                        company_data.company_name = title_elem.get_text(strip=True)
                
                # Extract key financial figures from overview
                financial_rows = soup.find_all('tr')
                for row in financial_rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'omsättning' in label or 'turnover' in label:
                            company_data.turnover = self._parse_financial_value(value)
                        elif 'resultat' in label and 'efter' in label:
                            company_data.profit = self._parse_financial_value(value)
                        elif 'eget kapital' in label or 'equity' in label:
                            company_data.equity = self._parse_financial_value(value)
                        elif 'anställda' in label or 'employees' in label:
                            try:
                                company_data.employees = int(re.sub(r'\D', '', value))
                            except ValueError:
                                pass
                
                return company_data
                
        except Exception as e:
            logger.error(f"Error fetching company data: {e}")
            return None

    async def fetch_financial_statements(self, org_number: str = None, company_name: str = None) -> List[FinancialStatement]:
        """Fetch financial statements for a company"""
        try:
            bokslut_url = await self.search_company(org_number, company_name)
            if not bokslut_url:
                return []
            
            async with self.session.get(bokslut_url) as response:
                if response.status != 200:
                    return []
                    
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                statements = []
                
                # Look for financial data tables
                tables = soup.find_all('table')
                
                for table in tables:
                    # Try to identify year columns and financial rows
                    header_row = table.find('thead') or table.find('tr')
                    if not header_row:
                        continue
                        
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                    year_columns = []
                    
                    # Find year columns
                    for i, header in enumerate(headers):
                        if re.match(r'\d{4}', header):
                            try:
                                year = int(header)
                                if 2000 <= year <= datetime.now().year:
                                    year_columns.append((i, year))
                            except ValueError:
                                continue
                    
                    if not year_columns:
                        continue
                    
                    # Process data rows
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    # Initialize statements for each year
                    year_statements = {}
                    for col_idx, year in year_columns:
                        year_statements[year] = FinancialStatement(
                            year=year,
                            period_start=date(year, 1, 1),
                            period_end=date(year, 12, 31),
                            source="allabolag"
                        )
                    
                    # Parse financial data rows
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) <= max(col_idx for col_idx, _ in year_columns):
                            continue
                            
                        row_label = cells[0].get_text(strip=True).lower()
                        
                        # Map row labels to financial statement fields
                        field_mapping = {
                            'nettoomsättning': 'revenue',
                            'omsättning': 'revenue',
                            'rörelsens intäkter': 'revenue',
                            'kostnad för sålda varor': 'cost_of_goods_sold',
                            'varukostnad': 'cost_of_goods_sold',
                            'rörelseresultat': 'ebit',
                            'resultat efter finansiella poster': 'profit_before_tax',
                            'årets resultat': 'net_profit',
                            'periodens resultat': 'net_profit',
                            'årets skatt': 'tax_expense',
                            'balansomslutning': 'total_assets',
                            'summa tillgångar': 'total_assets',
                            'eget kapital': 'equity',
                            'skulder': 'total_liabilities',
                            'kortfristiga skulder': 'current_liabilities',
                            'långfristiga skulder': 'long_term_liabilities',
                            'medelantalet anställda': 'employees'
                        }
                        
                        # Find matching field
                        field_name = None
                        for key, field in field_mapping.items():
                            if key in row_label:
                                field_name = field
                                break
                        
                        if field_name:
                            # Extract values for each year
                            for col_idx, year in year_columns:
                                if col_idx < len(cells):
                                    cell_value = cells[col_idx].get_text(strip=True)
                                    if field_name == 'employees':
                                        try:
                                            setattr(year_statements[year], field_name, int(re.sub(r'\D', '', cell_value)))
                                        except ValueError:
                                            pass
                                    else:
                                        parsed_value = self._parse_financial_value(cell_value)
                                        if parsed_value is not None:
                                            setattr(year_statements[year], field_name, parsed_value)
                    
                    # Add statements with data to results
                    for statement in year_statements.values():
                        # Only include statements with at least some financial data
                        if any([statement.revenue, statement.net_profit, statement.total_assets, statement.equity]):
                            statements.append(statement)
                
                # Sort by year
                statements.sort(key=lambda x: x.year, reverse=True)
                return statements[:5]  # Return last 5 years
                
        except Exception as e:
            logger.error(f"Error fetching financial statements: {e}")
            return []

    async def validate_org_number(self, org_number: str) -> bool:
        """Validate if an organizational number exists on allabolag.se"""
        try:
            company_url = await self.search_company(org_number=org_number)
            return company_url is not None
        except Exception:
            return False


# Utility functions for use in API endpoints
async def fetch_allabolag_data(org_number: str = None, company_name: str = None) -> Dict[str, Any]:
    """Fetch both company data and financial statements"""
    async with AllabolagScraper() as scraper:
        company_data = await scraper.fetch_company_data(org_number, company_name)
        financial_statements = await scraper.fetch_financial_statements(org_number, company_name)
        
        return {
            "company_data": company_data.dict() if company_data else None,
            "financial_statements": [stmt.dict() for stmt in financial_statements],
            "success": company_data is not None or len(financial_statements) > 0
        }