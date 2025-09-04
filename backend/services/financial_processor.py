from typing import List, Dict, Any, Optional
from fastapi import UploadFile
import io
from datetime import datetime
from core.database import get_supabase

# ML imports - commented out for MVP to avoid dependency issues
# import pandas as pd
# import numpy as np
# import lightgbm as lgb
# from prophet import Prophet
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import mean_absolute_error, mean_squared_error

# For MVP, we'll use basic Python for calculations
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

async def process_financial_data(file: UploadFile, company_id: str) -> List[Dict]:
    """
    Process uploaded financial data file and store in database.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Expected columns: year, revenue, profit, assets, liabilities, equity
        required_columns = ['year']
        optional_columns = ['revenue', 'profit', 'assets', 'liabilities', 'equity']
        
        if 'year' not in df.columns:
            raise ValueError("File must contain a 'year' column")
        
        # Clean and validate data
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year'])
        df['year'] = df['year'].astype(int)
        
        # Convert financial columns to numeric
        for col in optional_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Store in database
        supabase = get_supabase()
        financials = []
        
        for _, row in df.iterrows():
            financial_data = {
                "company_id": company_id,
                "year": int(row['year']),
            }
            
            for col in optional_columns:
                if col in df.columns and not pd.isna(row[col]):
                    financial_data[col] = float(row[col])
            
            # Upsert (insert or update if exists)
            result = supabase.table("financials").upsert(
                financial_data,
                on_conflict="company_id,year"
            ).execute()
            
            financials.extend(result.data)
        
        return financials
        
    except Exception as e:
        raise ValueError(f"Error processing financial data: {str(e)}")

def calculate_financial_ratios(financials: List[Dict]) -> Dict[str, Any]:
    """
    Calculate key financial ratios from financial data.
    """
    if not financials:
        return {}
    
    ratios = {}
    
    try:
        # Sort by year and get latest
        sorted_financials = sorted(financials, key=lambda x: x.get('year', 0))
        latest = sorted_financials[-1]
        
        # Profitability ratios
        if latest.get('revenue') and latest.get('profit') and latest['revenue'] > 0:
            ratios['profit_margin'] = (latest['profit'] / latest['revenue']) * 100
        
        # Leverage ratios
        if latest.get('assets') and latest.get('liabilities') and latest['assets'] > 0:
            ratios['debt_to_assets'] = (latest['liabilities'] / latest['assets']) * 100
        
        if latest.get('equity') and latest.get('liabilities') and latest['equity'] > 0:
            ratios['debt_to_equity'] = (latest['liabilities'] / latest['equity']) * 100
        
        # Growth rates (if we have multiple years)
        if len(sorted_financials) >= 2:
            prev = sorted_financials[-2]
            
            if latest.get('revenue') and prev.get('revenue') and prev['revenue'] > 0:
                ratios['revenue_growth'] = ((latest['revenue'] - prev['revenue']) / prev['revenue']) * 100
            
            if latest.get('profit') and prev.get('profit') and prev['profit'] > 0:
                ratios['profit_growth'] = ((latest['profit'] - prev['profit']) / prev['profit']) * 100
        
        # Multi-year averages
        if len(sorted_financials) >= 3:
            valid_margins = []
            for record in sorted_financials:
                if record.get('revenue', 0) > 0 and record.get('profit') is not None:
                    valid_margins.append((record['profit'] / record['revenue']) * 100)
            if valid_margins:
                ratios['avg_profit_margin'] = sum(valid_margins) / len(valid_margins)
        
        return ratios
        
    except Exception as e:
        print(f"Error calculating ratios: {e}")
        return {}

async def generate_financial_forecast(company_id: str, forecast_years: int = 3) -> Dict[str, Any]:
    """
    Generate simple financial forecasts (MVP version without ML).
    """
    try:
        supabase = get_supabase()
        
        # Fetch financial data
        result = supabase.table("financials").select("*").eq("company_id", company_id).order("year").execute()
        
        if not result.data or len(result.data) < 2:
            return {"error": "Insufficient historical data for forecasting (minimum 2 years required)"}
        
        financials = sorted(result.data, key=lambda x: x.get('year', 0))
        
        # Simple trend-based forecasting
        forecasts = {}
        base_year = financials[-1]['year']
        
        for metric in ['revenue', 'profit', 'assets', 'liabilities', 'equity']:
            if len(financials) >= 2 and all(f.get(metric) is not None for f in financials[-2:]):
                # Calculate simple growth rate from last 2 years
                recent = financials[-1][metric]
                previous = financials[-2][metric]
                
                if previous > 0:
                    growth_rate = (recent - previous) / previous
                else:
                    growth_rate = 0.05  # Default 5% growth
                
                # Generate forecast
                forecast_values = []
                current_value = recent
                for year in range(forecast_years):
                    current_value *= (1 + growth_rate)
                    forecast_values.append(current_value)
                
                forecasts[metric] = forecast_values
        
        # Calculate derived forecasts
        if 'revenue' in forecasts and 'profit' in forecasts:
            forecasts['profit_margin'] = [
                (p / r) * 100 if r > 0 else 0
                for p, r in zip(forecasts['profit'], forecasts['revenue'])
            ]
        
        # Generate simple scenario analysis
        scenarios = _generate_scenarios(forecasts)
        
        return {
            "base_case": forecasts,
            "scenarios": scenarios,
            "forecast_years": list(range(base_year + 1, base_year + forecast_years + 1)),
            "model_confidence": "medium",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Error generating forecast: {str(e)}"}

# Removed Prophet-based forecasting for MVP

def _generate_scenarios(base_forecasts: Dict[str, List[float]]) -> Dict[str, Dict[str, List[float]]]:
    """
    Generate optimistic and pessimistic scenarios based on base forecasts.
    """
    scenarios = {
        "optimistic": {},
        "pessimistic": {}
    }
    
    # Apply scenario adjustments
    optimistic_multiplier = 1.2  # 20% better
    pessimistic_multiplier = 0.8  # 20% worse
    
    for metric, values in base_forecasts.items():
        if isinstance(values, list) and len(values) > 0:
            scenarios["optimistic"][metric] = [v * optimistic_multiplier for v in values]
            scenarios["pessimistic"][metric] = [v * pessimistic_multiplier for v in values]
    
    return scenarios

async def calculate_credit_score(company_id: str) -> Dict[str, Any]:
    """
    Calculate a simple credit score based on financial metrics.
    """
    try:
        supabase = get_supabase()
        
        # Fetch financial data and ratios
        result = supabase.table("financials").select("*").eq("company_id", company_id).order("year").execute()
        
        if not result.data:
            return {"score": None, "rating": "No Data", "factors": []}
        
        financials = result.data
        ratios = calculate_financial_ratios(financials)
        
        # Simple scoring model (0-1000 scale)
        score = 500  # Base score
        factors = []
        
        # Profitability factor
        if 'profit_margin' in ratios:
            if ratios['profit_margin'] > 10:
                score += 100
                factors.append("Strong profitability")
            elif ratios['profit_margin'] > 5:
                score += 50
                factors.append("Moderate profitability")
            elif ratios['profit_margin'] < 0:
                score -= 100
                factors.append("Negative profitability")
        
        # Growth factor
        if 'revenue_growth' in ratios:
            if ratios['revenue_growth'] > 10:
                score += 75
                factors.append("Strong revenue growth")
            elif ratios['revenue_growth'] > 0:
                score += 25
                factors.append("Positive revenue growth")
            elif ratios['revenue_growth'] < -10:
                score -= 75
                factors.append("Declining revenue")
        
        # Leverage factor
        if 'debt_to_assets' in ratios:
            if ratios['debt_to_assets'] < 30:
                score += 50
                factors.append("Low leverage")
            elif ratios['debt_to_assets'] > 70:
                score -= 100
                factors.append("High leverage")
        
        # Ensure score is within bounds
        score = max(0, min(1000, score))
        
        # Convert to rating
        if score >= 800:
            rating = "AAA"
        elif score >= 700:
            rating = "AA"
        elif score >= 600:
            rating = "A"
        elif score >= 500:
            rating = "BBB"
        elif score >= 400:
            rating = "BB"
        elif score >= 300:
            rating = "B"
        else:
            rating = "C"
        
        return {
            "score": score,
            "rating": rating,
            "factors": factors,
            "ratios": ratios
        }
        
    except Exception as e:
        return {"error": f"Error calculating credit score: {str(e)}"}