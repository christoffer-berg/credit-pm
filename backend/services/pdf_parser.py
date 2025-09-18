import pypdf as PyPDF2
import pdfplumber
import pandas as pd
import re
import asyncio
import aiofiles
import os
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime, date
import logging
from pathlib import Path
import json
from schemas.financial_data import FinancialStatement, PDFUploadResponse

logger = logging.getLogger(__name__)

class FinancialPDFParser:
    def __init__(self, upload_dir: str = "uploads/financial_docs"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Common Swedish financial terms and their English equivalents
        self.financial_terms_mapping = {
            # Income statement
            'nettoomsättning': 'revenue',
            'omsättning': 'revenue',
            'rörelsens intäkter': 'revenue',
            'nettointäkter': 'revenue',
            'kostnad för sålda varor': 'cost_of_goods_sold',
            'varukostnad': 'cost_of_goods_sold',
            'rörelsekostnad': 'operating_expenses',
            'rörelsekostnader': 'operating_expenses',
            'rörelseresultat': 'ebit',
            'resultat före finansiella poster': 'ebit',
            'finansiella intäkter': 'financial_income',
            'finansiella kostnader': 'financial_expenses',
            'resultat efter finansiella poster': 'profit_before_tax',
            'resultat före skatt': 'profit_before_tax',
            'skatt på årets resultat': 'tax_expense',
            'årets skatt': 'tax_expense',
            'skattekostnad': 'tax_expense',
            'årets resultat': 'net_profit',
            'periodens resultat': 'net_profit',
            'nettovinst': 'net_profit',
            'avskrivning': 'depreciation',
            'avskrivningar': 'depreciation',
            
            # Balance sheet
            'balansomslutning': 'total_assets',
            'summa tillgångar': 'total_assets',
            'omsättningstillgångar': 'current_assets',
            'anläggningstillgångar': 'fixed_assets',
            'eget kapital': 'equity',
            'skulder': 'total_liabilities',
            'kortfristiga skulder': 'current_liabilities',
            'långfristiga skulder': 'long_term_liabilities',
            'summa skulder': 'total_liabilities',
            'likvida medel': 'cash_ending',
            'kassa och bank': 'cash_ending',
            
            # Other
            'medelantalet anställda': 'employees',
            'antal anställda': 'employees'
        }
        
        # Patterns for financial values
        self.value_patterns = [
            r'([-+]?\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)',  # 1,234,567.89 or 1 234 567,89
            r'([-+]?\d+(?:[.,]\d{1,2})?)',  # Simple numbers
        ]

    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return the file path"""
        # Create unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
        unique_filename = f"{timestamp}_{safe_filename}"
        
        file_path = self.upload_dir / unique_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return str(file_path)

    def _parse_financial_value(self, value_str: str) -> Optional[Decimal]:
        """Parse financial values from Swedish format"""
        if not value_str or value_str.strip() in ['-', '0', '', 'n/a', 'N/A']:
            return None
        
        # Remove common currency symbols and units
        clean_value = re.sub(r'[tkr|mkr|kr|sek|€|$|£]', '', value_str.lower())
        clean_value = re.sub(r'[\s\xa0]', '', clean_value)  # Remove spaces and non-breaking spaces
        
        # Handle multipliers
        multiplier = 1
        if 'mkr' in value_str.lower() or 'miljoner' in value_str.lower():
            multiplier = 1000000
        elif 'tkr' in value_str.lower() or 'tusen' in value_str.lower():
            multiplier = 1000
        
        # Replace comma with dot for decimal parsing (Swedish format)
        clean_value = clean_value.replace(',', '.')
        
        # Extract numeric value
        for pattern in self.value_patterns:
            match = re.search(pattern, clean_value)
            if match:
                try:
                    numeric_str = match.group(1).replace(' ', '').replace(',', '')
                    return Decimal(str(float(numeric_str) * multiplier))
                except (ValueError, TypeError):
                    continue
        
        return None

    def _extract_years_from_text(self, text: str) -> List[int]:
        """Extract year values from text"""
        year_pattern = r'\b(20\d{2}|19\d{2})\b'
        years = []
        for match in re.finditer(year_pattern, text):
            year = int(match.group(1))
            if 1990 <= year <= datetime.now().year:
                years.append(year)
        return sorted(list(set(years)), reverse=True)

    async def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text content from PDF using multiple methods"""
        text_content = ""
        tables = []
        
        try:
            # Method 1: pdfplumber for better table extraction
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n--- Page {i+1} ---\n{page_text}"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            if table and len(table) > 1:  # Ensure table has content
                                tables.append({
                                    'page': i + 1,
                                    'data': table
                                })
            
            # Method 2: Fallback to PyPDF2 if pdfplumber fails
            if not text_content:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text_content += f"\n--- Page {page_num+1} ---\n{page.extract_text()}"
            
            return {
                'text': text_content,
                'tables': tables,
                'page_count': len(pdf.pages) if 'pdf' in locals() else len(pdf_reader.pages)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return {'text': '', 'tables': [], 'page_count': 0}

    def _identify_financial_statement_type(self, text: str) -> str:
        """Identify if text contains income statement, balance sheet, or cash flow"""
        text_lower = text.lower()
        
        income_keywords = ['resultaträkning', 'income statement', 'profit and loss', 'nettoomsättning']
        balance_keywords = ['balansräkning', 'balance sheet', 'tillgångar', 'skulder', 'eget kapital']
        cashflow_keywords = ['kassaflödesanalys', 'cash flow', 'likvida medel', 'kassaflöde']
        
        income_score = sum(1 for keyword in income_keywords if keyword in text_lower)
        balance_score = sum(1 for keyword in balance_keywords if keyword in text_lower)
        cashflow_score = sum(1 for keyword in cashflow_keywords if keyword in text_lower)
        
        if income_score >= balance_score and income_score >= cashflow_score:
            return 'income_statement'
        elif balance_score >= cashflow_score:
            return 'balance_sheet'
        else:
            return 'cash_flow'

    def _parse_financial_table(self, table: List[List[str]]) -> Dict[str, Dict[str, Any]]:
        """Parse a financial table and extract data by year"""
        if not table or len(table) < 2:
            return {}
        
        # Convert table to pandas DataFrame for easier manipulation
        try:
            df = pd.DataFrame(table[1:], columns=table[0])  # First row as headers
            
            # Find year columns
            year_columns = []
            for col in df.columns:
                if col and isinstance(col, str):
                    years = self._extract_years_from_text(col)
                    if years:
                        year_columns.append((col, years[0]))
            
            if not year_columns:
                return {}
            
            # Initialize result structure
            results = {}
            for col_name, year in year_columns:
                results[year] = {}
            
            # Parse each row
            for _, row in df.iterrows():
                if not row.iloc[0]:  # Skip empty rows
                    continue
                    
                row_label = str(row.iloc[0]).strip().lower()
                
                # Find matching financial term
                field_name = None
                for swedish_term, english_field in self.financial_terms_mapping.items():
                    if swedish_term in row_label:
                        field_name = english_field
                        break
                
                if field_name:
                    # Extract values for each year column
                    for col_name, year in year_columns:
                        try:
                            cell_value = str(row[col_name]) if col_name in row.index else ""
                            if field_name == 'employees':
                                # Parse as integer for employee count
                                employees_match = re.search(r'\d+', cell_value.replace(' ', ''))
                                if employees_match:
                                    results[year][field_name] = int(employees_match.group())
                            else:
                                # Parse as financial value
                                parsed_value = self._parse_financial_value(cell_value)
                                if parsed_value is not None:
                                    results[year][field_name] = float(parsed_value)
                        except (KeyError, ValueError, TypeError):
                            continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing financial table: {e}")
            return {}

    async def parse_financial_pdf(self, file_path: str) -> Dict[str, Any]:
        """Main function to parse financial PDF and extract structured data"""
        try:
            # Extract content from PDF
            pdf_content = await self.extract_text_from_pdf(file_path)
            
            if not pdf_content['text'] and not pdf_content['tables']:
                return {
                    'success': False,
                    'error': 'Could not extract content from PDF',
                    'financial_statements': []
                }
            
            # Initialize results
            financial_data = {}
            
            # Parse tables first (usually more structured)
            for table_info in pdf_content['tables']:
                table_data = self._parse_financial_table(table_info['data'])
                for year, data in table_data.items():
                    if year not in financial_data:
                        financial_data[year] = {}
                    financial_data[year].update(data)
            
            # If no tables found, try to parse from text
            if not financial_data:
                # Extract years from text
                years = self._extract_years_from_text(pdf_content['text'])
                
                # Simple text parsing for key financial figures
                for year in years:
                    year_data = {}
                    
                    # Look for financial figures near year mentions
                    year_pattern = rf'\b{year}\b'
                    text_lines = pdf_content['text'].split('\n')
                    
                    for i, line in enumerate(text_lines):
                        if re.search(year_pattern, line):
                            # Check surrounding lines for financial data
                            context_lines = text_lines[max(0, i-3):min(len(text_lines), i+4)]
                            context_text = ' '.join(context_lines).lower()
                            
                            for swedish_term, english_field in self.financial_terms_mapping.items():
                                if swedish_term in context_text:
                                    # Try to find financial value nearby
                                    values = re.findall(r'([-+]?\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{1,2})?)', context_text)
                                    if values:
                                        parsed_value = self._parse_financial_value(values[0])
                                        if parsed_value:
                                            year_data[english_field] = float(parsed_value)
                    
                    if year_data:
                        financial_data[year] = year_data
            
            # Convert to FinancialStatement objects
            financial_statements = []
            for year, data in financial_data.items():
                if data:  # Only include years with actual data
                    statement = FinancialStatement(
                        year=year,
                        period_start=date(year, 1, 1),
                        period_end=date(year, 12, 31),
                        source="pdf_upload",
                        **{k: Decimal(str(v)) for k, v in data.items() if k != 'employees'},
                        **({"employees": data["employees"]} if "employees" in data else {})
                    )
                    financial_statements.append(statement)
            
            # Sort by year (newest first)
            financial_statements.sort(key=lambda x: x.year, reverse=True)
            
            return {
                'success': len(financial_statements) > 0,
                'financial_statements': [stmt.dict() for stmt in financial_statements],
                'years_found': list(financial_data.keys()),
                'raw_content': {
                    'text_preview': pdf_content['text'][:1000],  # First 1000 chars
                    'table_count': len(pdf_content['tables']),
                    'page_count': pdf_content['page_count']
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'financial_statements': []
            }

    async def process_uploaded_file(self, file_content: bytes, filename: str, company_id: str) -> PDFUploadResponse:
        """Process an uploaded PDF file and return parsing results"""
        try:
            # Save the file
            file_path = await self.save_uploaded_file(file_content, filename)
            
            # Parse the PDF
            parsing_result = await self.parse_financial_pdf(file_path)
            
            response = PDFUploadResponse(
                filename=filename,
                file_size=len(file_content),
                upload_path=file_path,
                extracted_data=parsing_result,
                parsing_status="completed" if parsing_result['success'] else "failed",
                error_message=parsing_result.get('error')
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing uploaded file {filename}: {e}")
            return PDFUploadResponse(
                filename=filename,
                file_size=len(file_content),
                upload_path="",
                parsing_status="failed",
                error_message=str(e)
            )

# Utility function for API endpoints
async def parse_financial_pdf_file(file_content: bytes, filename: str, company_id: str = None) -> Dict[str, Any]:
    """Utility function to parse uploaded financial PDF"""
    parser = FinancialPDFParser()
    result = await parser.process_uploaded_file(file_content, filename, company_id or "")
    return result.dict()